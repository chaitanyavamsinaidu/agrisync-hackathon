from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


# -------------------------
# Farmer Model
# -------------------------
class Farmer(Base):
    __tablename__ = "farmers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    location = Column(String, nullable=False)


# -------------------------
# Harvest Model
# -------------------------
class Harvest(Base):
    __tablename__ = "harvests"

    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id"))
    crop_name = Column(String, nullable=False)
    quantity = Column(Float, nullable=False)
    expected_harvest_date = Column(Date, nullable=False)
    harvest_score = Column(Integer)


# -------------------------
# Buyer Model
# -------------------------
class Buyer(Base):
    __tablename__ = "buyers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    location = Column(String, nullable=False)


# -------------------------
# Demand Model
# -------------------------
class Demand(Base):
    __tablename__ = "demands"

    id = Column(Integer, primary_key=True, index=True)
    buyer_id = Column(Integer, ForeignKey("buyers.id"))
    crop_name = Column(String, nullable=False)
    quantity_required = Column(Float, nullable=False)