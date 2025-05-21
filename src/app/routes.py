import logging
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .db import get_db
from .models import CancelOrderRequest, Order

router = APIRouter()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@router.post("/cancel_order")
def cancel_order(request: CancelOrderRequest, db: Session = Depends(get_db)):
    """Cancels an order given a tracking number.

    Note: to simplify the technical challenge exercise, I am not verifying details
    such as correct username or email to authorize the order cancellation.

    Parameters
    ----------
    request : CancelOrderRequest
        The request body containing the tracking number.
    db : Session
        SQLAlchemy database session.

    Returns
    -------
    dict
        A response indicating the result of the cancellation request.
    """
    logger.info(
        "Received request to cancel order with tracking number: %s",
        request.tracking_number,
    )
    try:
        order = (
            db.query(Order)
            .filter(Order.tracking_number == str(request.tracking_number))
            .first()
        )
        if not order:
            logger.warning(
                "Order not found for tracking number: %s", request.tracking_number
            )
            raise HTTPException(status_code=404, detail="Order not found.")

        if order.status == "cancelled":
            logger.info("Order already cancelled: %s", request.tracking_number)
            return {"success": True, "message": "Order is already cancelled."}

        order_date = datetime.fromisoformat(order.order_date.isoformat())
        if datetime.now() - order_date > timedelta(days=10):
            logger.info(
                "Cancellation period expired for order: %s", request.tracking_number
            )
            return {
                "success": False,
                "message": "Cancellation period expired (10 days)",
            }
        else:
            logger.info("Order successfully cancelled: %s", request.tracking_number)
            return {"success": True, "message": "Order cancelled"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error while cancelling order: %s", str(e))
        raise HTTPException(status_code=503, detail="Service Unavailable")


@router.get("/track_order")
def track_order(tracking_number: int, db: Session = Depends(get_db)):
    """Tracks the status of an order by its tracking number.

    Note: to simplify the technical challenge exercise, I am not verifying details
    such as correct username or email to authorize the order tracking.

    Parameters
    ----------
    tracking_number : int
        The tracking number of the order.
    db : Session
        SQLAlchemy database session.

    Returns
    -------
    dict
        A response containing the order id and current status.
    """
    logger.info(
        "Received request to track order with tracking number: %s", tracking_number
    )
    try:
        order = (
            db.query(Order)
            .filter(Order.tracking_number == str(tracking_number))
            .first()
        )
        if not order:
            logger.warning("Order not found for tracking number: %s", tracking_number)
            raise HTTPException(status_code=404, detail="Order not found.")

        logger.info(
            "Order found for tracking number: %s. Status: %s",
            tracking_number,
            order.status,
        )
        return {"order_id": tracking_number, "status": order.status}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error while tracking order: %s", str(e))
        raise HTTPException(status_code=503, detail="Service Unavailable")
