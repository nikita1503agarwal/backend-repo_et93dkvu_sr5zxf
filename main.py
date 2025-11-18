import os
import smtplib
from email.message import EmailMessage
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from database import create_document, get_documents, db
from schemas import Lead, Booking, Service, Product, Testimonial, Post

app = FastAPI(title="Lele's Boutique API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def send_email(subject: str, body: str, to_email: str) -> bool:
    """Send email using SMTP settings from environment variables.
    Required env: SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, EMAIL_FROM
    Returns True if sent, False if not configured.
    """
    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASS")
    sender = os.getenv("EMAIL_FROM") or user

    if not (host and user and password and sender and to_email):
        return False

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = to_email
    msg.set_content(body)

    with smtplib.SMTP(host, port) as server:
        server.starttls()
        server.login(user, password)
        server.send_message(msg)
    return True


@app.get("/")
def root():
    return {"name": "Lele's Boutique API", "status": "ok"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set",
        "database_name": "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set",
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:120]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:120]}"
    return response


# Content endpoints (read-only for site display)
@app.get("/services", response_model=List[Service])
def list_services(limit: Optional[int] = None):
    docs = get_documents("service", {}, limit)
    if not docs:
        sample = [
            {"title": "Signature Makeup", "description": "Flawless, camera-ready finish.", "price_from": 180, "duration_min": 90},
            {"title": "Haute Couture Styling", "description": "Personalized wardrobe curation.", "price_from": 350, "duration_min": 120},
            {"title": "Brow Sculpt & Tint", "description": "Perfectly framed elegance.", "price_from": 60, "duration_min": 30}
        ]
        return sample[: limit or len(sample)]
    for d in docs:
        d.pop("_id", None)
    return docs


@app.get("/products", response_model=List[Product])
def list_products(limit: Optional[int] = None):
    docs = get_documents("product", {}, limit)
    if not docs:
        sample = [
            {"title": "Velvet Matte Lip Color", "description": "Petal-soft finish.", "price": 48, "image": "https://images.unsplash.com/photo-1585238342028-4bbc0a3d88a5?w=800&q=60", "tag": "New"},
            {"title": "Silk Glow Serum", "description": "Radiant complexion.", "price": 82, "image": "https://images.unsplash.com/photo-1615485737656-371b3f21a6f1?w=800&q=60"},
            {"title": "Noir Parfum", "description": "Smoked velvet, white florals.", "price": 120, "image": "https://images.unsplash.com/photo-1594035910387-fea47794261f?w=800&q=60", "tag": "Bestseller"}
        ]
        return sample[: limit or len(sample)]
    for d in docs:
        d.pop("_id", None)
    return docs


@app.get("/testimonials", response_model=List[Testimonial])
def list_testimonials(limit: Optional[int] = None):
    docs = get_documents("testimonial", {}, limit)
    if not docs:
        sample = [
            {"name": "Amara L.", "quote": "An experience, not a service. I felt exquisite.", "avatar": "https://images.unsplash.com/photo-1554151228-14d9def656e4?w=200&q=60"},
            {"name": "Celeste R.", "quote": "Every detail considered. Effortlessly elegant.", "avatar": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=200&q=60"}
        ]
        return sample[: limit or len(sample)]
    for d in docs:
        d.pop("_id", None)
    return docs


# Lead capture and booking
@app.post("/lead")
def create_lead(payload: Lead):
    try:
        lead_id = create_document("lead", payload)
        owner_email = os.getenv("EMAIL_TO")
        body = (
            f"New website lead for Lele's Boutique\n\n"
            f"Name: {payload.name}\n"
            f"Email: {payload.email}\n"
            f"Phone: {payload.phone or '-'}\n\n"
            f"Message:\n{payload.message or '-'}\n"
        )
        send_email("New Lead – Lele's Boutique", body, owner_email or "")
        return {"status": "ok", "id": lead_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/book")
def create_booking(payload: Booking):
    try:
        booking_id = create_document("booking", payload)
        owner_email = os.getenv("EMAIL_TO")
        body = (
            f"New booking request for Lele's Boutique\n\n"
            f"Name: {payload.name}\n"
            f"Email: {payload.email}\n"
            f"Phone: {payload.phone or '-'}\n"
            f"Service: {payload.service}\n"
            f"Date: {payload.date}\n\n"
            f"Notes:\n{payload.notes or '-'}\n"
        )
        send_email("New Booking – Lele's Boutique", body, owner_email or "")
        return {"status": "ok", "id": booking_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Blog/Lookbook
@app.get("/posts", response_model=List[Post])
def list_posts(limit: Optional[int] = None):
    docs = get_documents("post", {}, limit)
    if not docs:
        sample = [
            {"title": "Autumn Atelier", "excerpt": "Tonal layering in cashmere and silk.", "image": "https://images.unsplash.com/photo-1509631179647-0177331693ae?w=1200&q=60"},
            {"title": "Gilded Evenings", "excerpt": "A study in light and shadow.", "image": "https://images.unsplash.com/photo-1483985988355-763728e1932f?w=1200&q=60"}
        ]
        return sample[: limit or len(sample)]
    for d in docs:
        d.pop("_id", None)
    return docs


# Simple config
@app.get("/config")
def config():
    return {
        "instagram_user": os.getenv("INSTAGRAM_USER", "lelesboutique"),
        "ga_id": os.getenv("GA_ID", "")
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
