from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .db import get_db
from .models import CancelOrderRequest, Order, TrackOrderRequest


router = APIRouter()


@router.post("/cancel_order")
def cancel_order(request: CancelOrderRequest, db: Session = Depends(get_db)):
    print("\n\nI reached cancel_order endpoint, yey!!!")
    order = db.query(Order).filter(Order.tracking_number == str(request.tracking_number)).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found.")

    if order.status == "cancelled":
        return {"success": True, "message": "Order is already cancelled."}

    order_date = datetime.fromisoformat(order.order_date.isoformat())
    if datetime.now() - order_date > timedelta(days=10):
        return {"success": False, "message": "Cancellation period expired (10 days)"}
    else:
        # TODO: create response classes with pydantic and improve this part; should I simulate a real cancelled order?
        # TODO: what if the order exists and is already cancelled? Adapt the response according to that scenario
        return {"success": True, "message": "Order cancelled"}


@router.get("/track_order")  # request: TrackOrderRequest
def track_order(tracking_number: int, db: Session = Depends(get_db)):
    print("\n\nI reached track_order endpoint, yey!!!")
    # order = mock_orders.get(request.order_id)
    order = db.query(Order).filter(Order.tracking_number == str(tracking_number)).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found.")

    # Note: I'm not doing any verification about the identification the person - is the person allowed to assess that data?
    print(f"Tracking number: {tracking_number}. Order found! Order = {order}")
    return {"order_id": tracking_number, "status": order.status}  # "order_date": order.order_date,
