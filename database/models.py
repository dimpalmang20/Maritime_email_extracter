from sqlalchemy import Column, Integer, String, Float
from database.db import Base


class MaritimeRecord(Base):

    __tablename__ = "maritime_records"

    id = Column(Integer, primary_key=True, index=True)

    cargo = Column(String)

    cargo_type = Column(String)

    vessel_name = Column(String)

    vessel_type = Column(String)

    imo = Column(String)

    load_port = Column(String)

    discharge_port = Column(String)

    open_port = Column(String)

    quantity = Column(String)

    grain_capacity = Column(String)

    dwt = Column(String)

    laycan = Column(String)

    confidence_score = Column(Float)

    extraction_status = Column(String)

    template_type = Column(String)