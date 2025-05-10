from pydantic import BaseModel
from sqlalchemy import Column, Date, Enum, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    customer_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    order_date = Column(Date, nullable=False)
    status = Column(
        Enum("pending", "shipped", "completed", "cancelled", name="status_enum"),
        nullable=False,
    )
    tracking_number = Column(String, nullable=False)


# class Order(BaseModel):
#    order_id: str
#    order_date: str  # datetime?
#    status: str


class CancelOrderRequest(BaseModel):
    order_id: str


class TrackOrderRequest(BaseModel):
    order_id: str
