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
        """Generic content extraction from MongoDB"""
        documents = []
        
        try:
            collection = self.db["OrbitAI"]
            
            for record in collection.find().limit(50):
                for key, value in record.items():
                    if key == '_id':
                        continue
                    
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
        template = """You are a personal assistant with access to the user's emails, calendar, and other data stored in their database.

IMPORTANT: Use ONLY the information provided in the context below. This data comes directly from the user's MongoDB database containing their emails, calendar events, and other personal information.

Context from user's database:
{context}

User question: {question}

Instructions:
- Answer based on the provided context from the user's database
- If the context contains email information, provide the email details including content, sender, subject
- If the context contains calendar information, provide the schedule details  
- Be specific and detailed using the actual content from the context
- Do NOT say "I don't have access" - you DO have access via the provided context
- If no relevant information is in the context, then say "I couldn't find that specific information in your current data"
- When showing emails, include the actual content and details from the context

Answer:"""
        
        prompt = PromptTemplate(template=template, input_variables=["context", "question"])
        return RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(search_kwargs={"k": 15}),
            chain_type_kwargs={"prompt": prompt}
        )

def main():
    print("🚀 Starting RAG system with explicit database access prompt...")
    print("=" * 60)
    
    collector = DataCollector()
    
    print("📥 Collecting all data...")
    email_cal_docs = collector.get_emails_and_calendar()
    weather_docs = collector.get_weather_data()
    news_docs = collector.get_news_data()
    
    all_documents = email_cal_docs + weather_docs + news_docs
    print(f"✅ Total documents collected: {len(all_documents)}")
    
    # Show sample extracted content for debugging
    print("\n📋 Sample extracted content:")
    for i, doc in enumerate(all_documents[:5]):
        print(f"{i+1}. [{doc.metadata['type']}]: {doc.page_content[:100]}...")
    
    if not all_documents:
        print("❌ No documents found.")
        return
    
    rag = RAGSystem()
    print("\n🧠 Creating vector database...")
    rag.create_vectorstore(all_documents)
    
    print("⚡ Setting up QA chain...")
    qa_chain = rag.setup_qa_chain()
    
    print("\n🎯 Ready! Ask questions about your emails, calendar, weather, and news.")
    print("💡 Try: 'What are my recent emails from Coding Ninjas?'")
    print("Type 'quit' to exit")
    print("=" * 60)
    
    # Interactive mode with debugging
    while True:
        query = input(f"\n💬 You: ").strip()
        
        if query.lower() == 'quit':
            print("👋 Goodbye!")
            break
        
        if not query:
            continue
        
        try:
            print("🔍 Searching your database...")
            
            # DEBUG: Show what's actually retrieved
            docs = rag.vectorstore.similarity_search(query, k=5)
            print("📊 Retrieved from your database:")
            for i, doc in enumerate(docs):
                print(f"   {i+1}. [{doc.metadata['type']}]: {doc.page_content[:120]}...")
            print("-" * 50)
            
            result = qa_chain.invoke({"query": query})
            print(f"🤖 Assistant: {result['result']}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("=" * 50)

if __name__ == "__main__":
    main()
