from pydantic import BaseModel
from datetime import date


# -------------------------
# Farmer Schema
# -------------------------
class FarmerCreate(BaseModel):
    name: str
    phone: str
    location: str


# -------------------------
# Harvest Schema
# -------------------------
class HarvestCreate(BaseModel):
    farmer_id: int
    crop_name: str
    quantity: float
    expected_harvest_date: date


# -------------------------
# Buyer Schema
# -------------------------
class BuyerCreate(BaseModel):
    name: str
    phone: str
    location: str


# -------------------------
# Demand Schema
# -------------------------
class DemandCreate(BaseModel):
    buyer_id: int
    crop_name: str
    quantity_required: float