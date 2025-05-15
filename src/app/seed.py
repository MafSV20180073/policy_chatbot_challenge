import pandas as pd
from sqlalchemy.orm import Session

from .db import SessionLocal, initialize_db
from .models import Order


def seed_db():
    df = pd.read_csv("app/data/orders.csv")
    session: Session = SessionLocal()

    print("Seeding db...")

    for _, row in df.iterrows():
        order = Order(
            order_id=row["order_id"],
            customer_name=row["customer_name"],
            email=row["email"],
            order_date=row["order_date"],
            status=row["order_status"],
            tracking_number=row["tracking_number"],
        )

        session.add(order)

    session.commit()
    print("Load of mock orders data complete.")
    session.close()


if __name__ == "__main__":
    initialize_db()
    seed_db()
