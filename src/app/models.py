from pydantic import BaseModel


class Order(BaseModel):
    order_id: str
    order_date: str  # datetime?
    status: str


class CancelOrderRequest(BaseModel):
    order_id: str


class TrackOrderRequest(BaseModel):
    order_id: str
