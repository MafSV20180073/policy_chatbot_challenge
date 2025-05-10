import random
from pathlib import Path

import pandas as pd
from faker import Faker

NUM_ORDERS = 3000
ORDER_STATUSES = ["pending", "shipped", "completed", "cancelled"]
OUTPUT_FILE = f"{Path(__file__).parent.parent}/data/orders.csv"


def generate_orders(num_orders: int) -> pd.DataFrame:
    faker = Faker()
    Faker.seed(12)
    random.seed(12)

    orders = []
    for i in range(num_orders):
        order_date = faker.date_between(start_date="-30d", end_date="today")
        customer_name = faker.name()
        orders.append(
            {
                "order_id": faker.uuid4(),
                "customer_name": customer_name,
                "email": f"{customer_name.rstrip().replace(' ', '_')}@somerandomemail.com",
                "order_date": order_date,
                "order_status": random.choice(ORDER_STATUSES),
                "tracking_number": faker.random_number(digits=7),
            }
        )

    orders = pd.DataFrame(orders) 

    return orders


if __name__ == "__main__":
    orders_df = generate_orders(NUM_ORDERS)
    orders_df.to_csv(OUTPUT_FILE, index=False)
    print("Mock orders data successfully generated.")
