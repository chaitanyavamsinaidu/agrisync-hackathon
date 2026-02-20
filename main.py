from fastapi.responses import FileResponse
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from datetime import date

import models
import schemas
from database import engine, SessionLocal

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# ---------------------------
# CORS
# ---------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# Serve Frontend
# ---------------------------
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

# ---------------------------
# Database Dependency
# ---------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def home():
    return {"message": "AgriSync Backend is Running 🚜🔥"}

# ---------------------------
# Register Farmer
# ---------------------------
@app.post("/register-farmer")
def register_farmer(farmer: schemas.FarmerCreate, db: Session = Depends(get_db)):
    new_farmer = models.Farmer(
        name=farmer.name,
        phone=farmer.phone,
        location=farmer.location
    )

    db.add(new_farmer)
    db.commit()
    db.refresh(new_farmer)

    return {
        "message": "Farmer registered successfully 🚜",
        "farmer_id": new_farmer.id
    }

# ---------------------------
# Add Harvest
# ---------------------------
@app.post("/add-harvest")
def add_harvest(harvest: schemas.HarvestCreate, db: Session = Depends(get_db)):

    farmer = db.query(models.Farmer).filter(
        models.Farmer.id == harvest.farmer_id
    ).first()

    if not farmer:
        raise HTTPException(status_code=404, detail="Farmer not found")

    days_remaining = (harvest.expected_harvest_date - date.today()).days

    if days_remaining <= 5:
        harvest_score = 90
    elif days_remaining <= 10:
        harvest_score = 80
    else:
        harvest_score = 70

    new_harvest = models.Harvest(
        farmer_id=harvest.farmer_id,
        crop_name=harvest.crop_name,
        quantity=harvest.quantity,
        expected_harvest_date=harvest.expected_harvest_date,
        harvest_score=harvest_score
    )

    db.add(new_harvest)
    db.commit()
    db.refresh(new_harvest)

    return {
        "message": "Harvest added successfully 🌾",
        "harvest_id": new_harvest.id,
        "harvest_score": harvest_score,
        "days_remaining": days_remaining
    }

# ---------------------------
# Register Buyer
# ---------------------------
@app.post("/register-buyer")
def register_buyer(buyer: schemas.BuyerCreate, db: Session = Depends(get_db)):
    new_buyer = models.Buyer(
        name=buyer.name,
        phone=buyer.phone,
        location=buyer.location
    )

    db.add(new_buyer)
    db.commit()
    db.refresh(new_buyer)

    return {
        "message": "Buyer registered successfully 🛒",
        "buyer_id": new_buyer.id
    }

# ---------------------------
# Add Demand
# ---------------------------
@app.post("/add-demand")
def add_demand(demand: schemas.DemandCreate, db: Session = Depends(get_db)):

    buyer = db.query(models.Buyer).filter(
        models.Buyer.id == demand.buyer_id
    ).first()

    if not buyer:
        raise HTTPException(status_code=404, detail="Buyer not found")

    new_demand = models.Demand(
        buyer_id=demand.buyer_id,
        crop_name=demand.crop_name,
        quantity_required=demand.quantity_required
    )

    db.add(new_demand)
    db.commit()
    db.refresh(new_demand)

    return {
        "message": "Demand added successfully 📦",
        "demand_id": new_demand.id
    }

# ---------------------------
# Smart Match + Pricing
# ---------------------------
@app.post("/match-demand/{demand_id}")
def match_demand(demand_id: int, db: Session = Depends(get_db)):

    demand = db.query(models.Demand).filter(
        models.Demand.id == demand_id
    ).first()

    if not demand:
        raise HTTPException(status_code=404, detail="Demand not found")

    harvests = db.query(models.Harvest).filter(
        models.Harvest.crop_name == demand.crop_name,
        models.Harvest.quantity >= demand.quantity_required
    ).all()

    if not harvests:
        return {"message": "No matching harvest found ❌"}

    best_harvest = sorted(
        harvests,
        key=lambda x: x.harvest_score,
        reverse=True
    )[0]

    base_price = 20
    score_multiplier = best_harvest.harvest_score / 100

    days_remaining = (
        best_harvest.expected_harvest_date - date.today()
    ).days

    if days_remaining <= 5:
        urgency_multiplier = 1.2
    elif days_remaining <= 10:
        urgency_multiplier = 1.1
    else:
        urgency_multiplier = 1.0

    suggested_price = round(
        base_price * score_multiplier * urgency_multiplier, 2
    )

    return {
        "message": "Best match found ✅",
        "farmer_id": best_harvest.farmer_id,
        "harvest_id": best_harvest.id,
        "harvest_score": best_harvest.harvest_score,
        "available_quantity": best_harvest.quantity,
        "suggested_price_per_kg": suggested_price,
        "days_remaining": days_remaining
    }
# ---------------------------
# Dashboard Stats
# ---------------------------
@app.get("/dashboard")
def get_dashboard(db: Session = Depends(get_db)):

    total_farmers = db.query(models.Farmer).count()
    total_harvests = db.query(models.Harvest).count()
    total_buyers = db.query(models.Buyer).count()
    total_demands = db.query(models.Demand).count()

    return {
        "total_farmers": total_farmers,
        "total_harvests": total_harvests,
        "total_buyers": total_buyers,
        "total_demands": total_demands
    }
@app.get("/")
def serve_frontend():
    return FileResponse("frontend/index.html")