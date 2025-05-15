from pydantic import BaseModel
from sqlalchemy import Column, Date, Enum, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String, unique=True, index=True)
    customer_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    order_date = Column(Date, nullable=False)
    status = Column(
        Enum("pending", "shipped", "completed", "cancelled", name="status_enum"),
        nullable=False,
    )
    tracking_number = Column(String, nullable=False)


class CancelOrderRequest(BaseModel):
    # order_id: str
    tracking_number: int


class TrackOrderRequest(BaseModel):
    # order_id: str
    tracking_number: int
