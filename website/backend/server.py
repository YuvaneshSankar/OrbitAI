from fastapi import FastAPI, APIRouter, BackgroundTasks, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Dict, Any
import uuid
from datetime import datetime, timedelta
import sys
import asyncio
import subprocess
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.mime.text import MIMEText

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agentic_rag import rag_chat

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    """Check for daily briefing on startup"""
    logger.info("Starting up OrbitAI backend...")
    asyncio.create_task(check_and_generate_briefing())

class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

class ChatMessage(BaseModel):
    query: str

class ChatResponse(BaseModel):
    response: str
    error: str = None

class DailyBriefingResponse(BaseModel):
    content: str
    last_generated: str
    sections: Dict[str, List[str]]

last_briefing_date = None

async def generate_daily_briefing():
    global last_briefing_date
    try:
        logger.info("Starting daily briefing generation...")
        
        crewai_dir = Path(__file__).parent.parent.parent / "update_crewai"
        run_script = crewai_dir / "run.py"
        
        if not run_script.exists():
            logger.error(f"run.py not found at {run_script}")
            return
        
        result = subprocess.run([
            sys.executable, str(run_script)
        ], cwd=str(crewai_dir), capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            logger.info("Daily briefing generated successfully")
            last_briefing_date = datetime.now().date()
        else:
            logger.error(f"Failed to generate daily briefing: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        logger.error("Daily briefing generation timed out")
    except Exception as e:
        logger.error(f"Error generating daily briefing: {str(e)}")

async def check_and_generate_briefing():
    global last_briefing_date
    today = datetime.now().date()
    
    if last_briefing_date != today:
        await generate_daily_briefing()

def parse_markdown_briefing(content: str) -> Dict[str, List[str]]:
    sections = {
        "events": [],
        "tasks": [],
        "news": [],
        "suggestions": []
    }

    current_section = None
    lines = content.split('\n')

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if "📅 Today's Events" in line:
            current_section = "events"
            continue
        elif "✅ Priority Tasks" in line:
            current_section = "tasks"
            continue
        elif "📰 Top News" in line:
            current_section = "news"
            continue
        elif "💡 Suggestions" in line:
            current_section = "suggestions"
            continue
        elif line.startswith('## '):
            current_section = None

        # Parse bullets for events and tasks (•)
        if current_section in ["events", "tasks"] and line.startswith('• '):
            item = line[2:].strip()
            if item:
                sections[current_section].append(item)
        # Parse bullets for news (-)
        elif current_section == "news" and line.startswith('- '):
            item = line[2:].strip()
            if item:
                sections[current_section].append(item)
        # Parse suggestions (plain text paragraphs)
        elif current_section == "suggestions" and not line.startswith('#') and not line.startswith('*'):
            if line and not line.startswith('---'):
                sections[current_section].append(line)

    return sections

@app.get("/")
async def root():
    return {"message": "Welcome to OrbitAI Backend!"}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(message: ChatMessage):
    try:
        logger.info(f"Received chat query: {message.query}")
        response = rag_chat(message.query)
        
        if response == "error":
            logger.error("RAG system returned error")
            return ChatResponse(
                response="Sorry, I encountered an error while processing your request. Please try again.",
                error="RAG system error"
            )
        
        logger.info(f"Generated response: {response[:100]}...")
        return ChatResponse(response=response)
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return ChatResponse(
            response="Sorry, I'm experiencing technical difficulties. Please try again in a moment.",
            error=str(e)
        )

@app.get("/daily_briefing")
async def get_daily_briefing(background_tasks: BackgroundTasks):
    try:
        await check_and_generate_briefing()
        
        briefing_file = Path(__file__).parent.parent.parent / "update_crewai" / "daily_briefing.md"
        
        if not briefing_file.exists():
            logger.info("Daily briefing file not found, generating...")
            print("Daily briefing file not found, generating...")
            await generate_daily_briefing()
            
            if not briefing_file.exists():
                print("Failed to generate daily briefing file.")
                raise HTTPException(status_code=404, detail="Daily briefing could not be generated")
        
        with open(briefing_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        sections = parse_markdown_briefing(content)
        print("Parsed sections:", sections)
        mod_time = datetime.fromtimestamp(briefing_file.stat().st_mtime)
        last_generated = mod_time.strftime("%Y-%m-%d %H:%M:%S")
        
        return DailyBriefingResponse(
            content=content,
            last_generated=last_generated,
            sections=sections
        )
        
    except Exception as e:
        logger.error(f"Error in daily briefing endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving daily briefing: {str(e)}")

@app.post("/notes_send_mail")  # Changed from GET to POST
async def send_mail(request: dict):
    try:
        logger.info("Sending mail...")
        
        # Get the note content from the request
        note_content = request.get('note', 'No note content provided')
        
        smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        sender_email = os.getenv('SENDER_EMAIL')
        sender_password = os.getenv('SENDER_PASSWORD')
        
        msg = MIMEMultipart()
        msg['From'] = "yuvanesh.skv@gmail.com"
        msg['To'] = "yuvanesh.ykv@gmail.com"
        msg['Subject'] = "Quick Note from OrbitAI"
        
        body = f"""
        Hi there! 👋

        You have a new quick note from OrbitAI:

        📝 Note: {note_content}

        Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

        Best regards,
        Yuvaansh S
        Orbit AI
        """

        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, "yuvanesh.ykv@gmail.com", text)  # ✅ Fixed line
        server.quit()
        logger.info("Email sent successfully")
        
        return {"message": "Note sent successfully", "note": note_content}
        
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error sending email: {str(e)}")

