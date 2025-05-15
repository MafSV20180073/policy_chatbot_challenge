import os
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .db import get_db
from .models import CancelOrderRequest, Order, TrackOrderRequest


if os.getenv("DEBUG_MODE", "false").lower() == "true":
    import pydevd_pycharm

    print("DEBUG_MODE is true in routes, attempting to connect to PyCharm debugger...")
    pydevd_pycharm.settrace(
        "host.docker.internal", #"'localhost',
        port=5678,  #5678,
        stdoutToServer=True,
        stderrToServer=True,
        suspend=False
    )

router = APIRouter()


@router.post("/cancel_order")
def cancel_order(request: CancelOrderRequest, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.tracking_number == request.tracking_number)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found.")

    order_date = datetime.fromisoformat(order["order_date"])
    if datetime.now() - order_date > timedelta(days=10):
        return {"success": False, "message": "Cancellation period expired (10 days)"}
    else:
        # TODO: create response classes with pydantic and improve this part; should I simulate a real cancelled order?
        # TODO: what if the order exists and is already cancelled? Adapt the response according to that scenario
        return {"success": True, "message": "Order cancelled"}


@router.get("/track-order")
def track_order(request: TrackOrderRequest, db: Session = Depends(get_db)):
    # order = mock_orders.get(request.order_id)
    order = db.query(Order).filter(Order.tracking_number == request.tracking_number)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found.")

    # Note: I'm not doing any verification about the identification the person - is the person allowed to assess that data?
    print(f"Tracking number: {request.tracking_number}. Order found! Order = {order}")
    return {"order_id": request.tracking_number, "status": order.status}  # "order_date": order.order_date,
