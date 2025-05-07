from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException

from .mock_data import mock_orders
from .models import CancelOrderRequest, TrackOrderRequest

router = APIRouter()


@router.post("/cancel_order")
def cancel_order(request: CancelOrderRequest):
    order = mock_orders.get(request.order_id)
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
def track_order(request: TrackOrderRequest):
    order = mock_orders.get(request.order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found.")

    # Note: I'm not doing any verification about the identification the person - is the person allowed to assess that data?
    return {"order_id": request.order_id, "status": order["status"]}
