import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MONGODB_URL = os.getenv("MONGODB_URL")
WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast?latitude=12.9165&longitude=79.1325&current=temperature_2m,wind_speed_10m,relative_humidity_2m&hourly=temperature_2m,precipitation"
NEWS_API_URL = "https://saurav.tech/NewsAPI/top-headlines/category/general/in.json"

class DataCollector:
    def __init__(self):
        self.mongo_client = MongoClient(MONGODB_URL)
        self.db = self.mongo_client["OrbitAI"]
    
    def get_emails_and_calendar(self):
        """Enhanced extraction with proper calendar parsing"""
        documents = []
        
        try:
            collection = self.db["OrbitAI"]
            
            for record in collection.find().limit(50):
                for key, value in record.items():
                    if key == '_id' or key == 'id':
                        continue
                    
                    # Enhanced calendar parsing - THIS IS THE KEY PART
                    if key.startswith('calendar:'):
                        calendar_doc = self._parse_calendar_event(key)
                        if calendar_doc:
                            documents.append(calendar_doc)
                    else:
                        # Regular content extraction for emails and other data
                        content = self._extract_content_from_field(key, value)
                        if content:
                            doc_type = self._determine_content_type(key, content)
                            documents.append(Document(
                                page_content=content,
                                metadata={"type": doc_type, "source": "mongodb", "field": key[:50]}
                            ))
                            
        except Exception as e:
            print(f"MongoDB error: {e}")
            
        return documents
    
    def _parse_calendar_event(self, calendar_key):
        """Parse calendar event from the key string"""
        try:
            # Remove 'calendar:' prefix and split by newlines
            event_data = calendar_key.replace('calendar:', '').strip()
            
            # Initialize event details
            event_details = {}
            
            # Parse each line - handle both \n and \\n
            lines = event_data.replace('\\n', '\n').split('\n')
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    event_details[key.strip()] = value.strip()
            
            # Create readable calendar content
            event_name = event_details.get('name', 'Unnamed Event')
            start_time = event_details.get('start', '')
            end_time = event_details.get('end', '')
            organizer = event_details.get('organizer', 'Unknown')
            status = event_details.get('status', 'Unknown')
            
            # Parse datetime for better querying
            start_datetime = self._parse_datetime(start_time)
            end_datetime = self._parse_datetime(end_time)
            
            # Create human-readable content
            calendar_content = f"""Calendar Event: {event_name}
Start: {self._format_datetime(start_datetime)} 
End: {self._format_datetime(end_datetime)}
Organizer: {organizer}
Status: {status}
Duration: {self._calculate_duration(start_datetime, end_datetime)}"""
            
            return Document(
                page_content=calendar_content,
                metadata={
                    "type": "calendar",
                    "source": "mongodb",
                    "event_name": event_name,
                    "start_time": start_time,
                    "end_time": end_time,
                    "start_hour": start_datetime.hour if start_datetime else None,
                    "date": start_datetime.date().isoformat() if start_datetime else None
                }
            )
            
        except Exception as e:
            print(f"Calendar parsing error: {e}")
            return None
    
    def _parse_datetime(self, datetime_str):
        """Parse datetime string"""
        try:
            if datetime_str:
                # Handle format: 2025-09-05T08:00:00+05:30
                if '+' in datetime_str:
                    datetime_str = datetime_str.split('+')[0]
                return datetime.fromisoformat(datetime_str)
        except:
            pass
        return None
    
    def _format_datetime(self, dt):
        """Format datetime for display"""
        if dt:
            return dt.strftime("%Y-%m-%d at %I:%M %p")
        return "Unknown time"
    
    def _calculate_duration(self, start_dt, end_dt):
        """Calculate meeting duration"""
        if start_dt and end_dt:
            duration = end_dt - start_dt
            hours = duration.seconds // 3600
            minutes = (duration.seconds % 3600) // 60
            if hours > 0:
                return f"{hours}h {minutes}m"
            else:
                return f"{minutes}m"
        return "Unknown duration"
    
    def _extract_content_from_field(self, key, value):
        """Generic method to extract meaningful content from any field"""
        if isinstance(key, str) and len(key) > 30:
            clean_key = key.replace('mail:', '').replace('calendar:', '').strip()
            if len(clean_key) > 20 and not clean_key.lower().startswith('_'):
                return clean_key
        
        if isinstance(value, str) and len(value) > 20:
            return value
        
        if isinstance(value, dict):
            text_parts = []
            for k, v in value.items():
                if isinstance(v, str) and len(v) > 10:
                    text_parts.append(f"{k}: {v}")
            if text_parts:
                return " | ".join(text_parts)
        
        if isinstance(value, list):
            text_parts = []
            for item in value:
                if isinstance(item, str) and len(item) > 10:
                    text_parts.append(item)
                elif isinstance(item, dict):
                    for k, v in item.items():
                        if isinstance(v, str) and len(v) > 10:
                            text_parts.append(f"{k}: {v}")
            if text_parts:
                return " | ".join(text_parts[:5])
        
        return None
    
    def _determine_content_type(self, key, content):
        """Generic method to determine content type"""
        key_lower = key.lower()
        content_lower = content.lower()
        
        if any(word in key_lower or word in content_lower for word in ['mail', 'email', 'from:', 'subject:']):
            return "email"
        elif any(word in key_lower or word in content_lower for word in ['calendar', 'meeting', 'appointment', 'schedule', 'event']):
            return "calendar"
        elif any(word in key_lower or word in content_lower for word in ['payment', 'upi', 'transaction', 'pay', 'subscription']):
            return "payment"
        elif any(word in key_lower or word in content_lower for word in ['news', 'article', 'headline']):
            return "news"
        elif any(word in key_lower or word in content_lower for word in ['job', 'career', 'hiring', 'position']):
            return "job"
        else:
            return "general"
    
    def get_weather_data(self):
        """Fetch current weather data"""
        try:
            response = requests.get(WEATHER_API_URL)
            data = response.json()
            
            current = data.get('current', {})
            weather_content = f"""Current Weather:
Temperature: {current.get('temperature_2m', 'N/A')}°C
Wind Speed: {current.get('wind_speed_10m', 'N/A')} m/s
Humidity: {current.get('relative_humidity_2m', 'N/A')}%
Time: {current.get('time', 'N/A')}"""
            
            return [Document(
                page_content=weather_content,
                metadata={"type": "weather", "source": "api"}
            )]
        except Exception as e:
            print(f"Weather API error: {e}")
            return []
    
    def get_news_data(self):
        """Fetch latest news"""
        try:
            response = requests.get(NEWS_API_URL)
            data = response.json()
            
            documents = []
            for article in data.get('articles', [])[:3]:
                news_content = f"""News: {article.get('title', 'No title')}
Description: {article.get('description', 'No description')}
Source: {article.get('source', {}).get('name', 'Unknown')}"""
                
                documents.append(Document(
                    page_content=news_content,
                    metadata={"type": "news", "source": "api"}
                ))
                
            return documents
        except Exception as e:
            print(f"News API error: {e}")
            return []

class RAGSystem:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY)
        self.llm = ChatOpenAI(api_key=OPENAI_API_KEY, temperature=0.1)
        self.vectorstore = None
    
    def create_vectorstore(self, documents):
        if not documents:
            print("No documents to create vectorstore")
            return
        self.vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory="./chroma_db"
        )
        
    def setup_qa_chain(self):
        template = """You are a personal assistant with access to the user's emails, calendar events, weather, and news data.

IMPORTANT: Use ONLY the information provided in the context below from the user's database.

Context from user's database:
{context}

User question: {question}

Instructions:
- For calendar queries: Look for specific times, dates, and meeting details
- For "Do I have work/meeting at X time": Check if there are calendar events at that specific time
- If asking about availability: Check for conflicts in calendar events
- Be specific about meeting names, times, organizers, and durations
- For time-based queries (like "9 AM today"), look for events with matching hours
- Always provide complete event details when available
- If no calendar events match the time, say "You appear to be free at that time"
- Do NOT say "I don't have access" - you DO have access via the provided context

Answer:"""
        
        prompt = PromptTemplate(template=template, input_variables=["context", "question"])
        return RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(search_kwargs={"k": 15}),
            chain_type_kwargs={"prompt": prompt}
        )

def main():
    print(" Starting RAG system with enhanced calendar support...")
    print("=" * 60)
    
    collector = DataCollector()
    
    print(" Collecting all data...")
    email_cal_docs = collector.get_emails_and_calendar()
    weather_docs = collector.get_weather_data()
    news_docs = collector.get_news_data()
    
    all_documents = email_cal_docs + weather_docs + news_docs
    print(f" Total documents collected: {len(all_documents)}")
    
    # Show calendar events specifically
    calendar_docs = [doc for doc in all_documents if doc.metadata.get('type') == 'calendar']
    print(f" Calendar events found: {len(calendar_docs)}")
    
    for i, doc in enumerate(calendar_docs):
        event_name = doc.metadata.get('event_name', 'Unknown Event')
        print(f"   {i+1}. {event_name}")
    
    if not all_documents:
        print(" No documents found.")
        return
    
    rag = RAGSystem()
    print("\n Creating vector database...")
    rag.create_vectorstore(all_documents)
    
    print("⚡ Setting up QA chain...")
    qa_chain = rag.setup_qa_chain()
    
    print("\n Ready! Now supports detailed calendar queries!")
    print(" Try these:")
    print("   - 'Do I have work at 9 AM today?'")
    print("   - 'What meetings do I have today?'")
    print("   - 'Am I free around 8-9 AM?'")
    print("   - 'Show my calendar for today'")
    print("Type 'quit' to exit")
    print("=" * 60)
    
    while True:
        query = input(f"\n You: ").strip()
        
        if query.lower() == 'quit':
            print(" Goodbye!")
            break
        
        if not query:
            continue
        
        try:
            print(" Searching your database...")
            
            # Show relevant retrieved documents
            docs = rag.vectorstore.similarity_search(query, k=5)
            print(" Retrieved from your database:")
            for i, doc in enumerate(docs):
                doc_preview = doc.page_content[:120].replace('\n', ' ')
                print(f"   {i+1}. [{doc.metadata['type']}]: {doc_preview}...")
            print("-" * 50)
            
            result = qa_chain.invoke({"query": query})
            print(f" Assistant: {result['result']}")
            
        except Exception as e:
            print(f" Error: {e}")
        
        print("=" * 50)

if __name__ == "__main__":
    main()
