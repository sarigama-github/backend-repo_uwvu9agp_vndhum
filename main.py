import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="Site Service Bane API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    context: Optional[str] = None

class ChatResponse(BaseModel):
    reply: str


@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI Backend!"}


@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}


@app.post("/api/chat", response_model=ChatResponse)
def chat_endpoint(body: ChatRequest):
    """
    Simple local AI-like responder with rule-based answers tailored to
    Site Service Bane (railway/samferdsel). No external API required.
    """
    if not body.messages:
        raise HTTPException(status_code=400, detail="No messages provided")

    user_msg = ""
    # Find latest user message
    for m in reversed(body.messages):
        if m.role.lower() == "user":
            user_msg = m.content.strip()
            break

    def generate_reply(text: str) -> str:
        t = text.lower()
        if any(k in t for k in ["kontakt", "contact", "telefon", "epost", "email", "tilbud"]):
            return (
                "Takk for henvendelsen! Du kan kontakte oss for tilbud eller befaring. "
                "Fortell gjerne kort om behov (område, type arbeid, tidsperspektiv), så følger vi opp."
            )
        if any(k in t for k in ["samferdsel", "bane", "jernbane", "rail"]):
            return (
                "Vi leverer tjenester innen samferdsel/bane: grunnarbeid, kabel/kanal, sikring, drift og vedlikehold. "
                "Alt levert trygt, effektivt og i henhold til krav.")
        if any(k in t for k in ["tjeneste", "services", "hva tilbyr", "leverer dere"]):
            return (
                "Våre hovedtjenester omfatter: prosjekt- og byggeledelse, grunn- og betongarbeider, "
                "kabelkanaler og trekkerør, belysning og el, sikkerhetstiltak, samt drift og vedlikehold.")
        if any(k in t for k in ["referanse", "case", "prosjekt", "portfolio"]):
            return (
                "Vi har erfaring fra en rekke leveranser i samferdselssektoren. "
                "Ta en titt på referansene for et utvalg av prosjekter – alt fra utskifting av kabelgrøfter "
                "til større infrastrukturtiltak.")
        if len(t) < 3:
            return "Hei! Hvordan kan vi hjelpe deg i dag?"
        return (
            "Forstår. Kan du beskrive litt mer konkret hva du trenger hjelp til (område, omfang, tid)? "
            "Jeg kan også koble deg til riktig fagperson hos oss.")

    reply = generate_reply(user_msg)
    return ChatResponse(reply=reply)


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    
    try:
        # Try to import database module
        from database import db
        
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            
            # Try to list collections to verify connectivity
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]  # Show first 10 collections
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
            
    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    
    # Check environment variables
    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    
    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
