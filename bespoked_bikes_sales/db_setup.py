from bespoked_bikes_sales import app, db
from bespoked_bikes_sales.models import *

customers = [   
    Customer(first_name="Wayne", last_name="Baker", address="899 Griffin Ave.", phone="518-739-9795", start_date=date(2023, 2, 5)),
    Customer(first_name="Roger", last_name="Church", address="165 Young Rd.", phone="716-941-6327", start_date=date(2023, 4, 20)),
    Customer(first_name="Brady", last_name="Ware", address="498 Lafayette St.", phone="384-713-5683", start_date=date(2020, 1, 15)),
]

products = [
    Product(name="Saturn-V", style="Bricks", manufacturer="LEGO", purchase_price=15.0,sale_price=60.0, quantity=50, commission_percentage=0.3),
    Product(name="Lord of the Rings", style="Book", manufacturer="Penguin", purchase_price=2.0,sale_price=10.0, quantity=100, commission_percentage=0.1),
    Product(name="1500mL Water Bottle", style="Clear", manufacturer="CamelBak", purchase_price=11.0,sale_price=20.0, quantity=200, commission_percentage=0.25)
]

salespeople = [
    Salesperson(first_name="Thomas", last_name="Riordan", address="935 Selby Rd.", phone="518-739-9795", start_date=date(2023, 5, 1), termination_date=date(2023, 12, 2), manager="Bill"),
    Salesperson(first_name="Orion", last_name="Branch", address="5 Illinois Rd.", phone="231-491-2631", start_date=date(2022, 1, 10), termination_date=date(2022, 7, 14), manager="Kevin"),
    Salesperson(first_name="Luca", last_name="Benson", address="818 NE. Ann Court", phone="394-364-6606", start_date=date(2020, 10, 12), termination_date=date(2024, 12, 2), manager="Bill"),
]

discounts = [
    Discount(product_id=1, begin_date=date(2020, 1, 1), end_date=date(2024, 12, 2), discount_percentage=0.1),
    Discount(product_id=1, begin_date=date(2023, 5, 1), end_date=date(2023, 6, 2), discount_percentage=0.3),
    Discount(product_id=2, begin_date=date(2023, 2, 5), end_date=date(2023, 4, 10), discount_percentage=0.25)
]

def seed_db():
    with app.app_context():
        for customer in customers:
            db.session.add(customer)
        for product in products:
            db.session.add(product)
        for salesperson in salespeople:
            db.session.add(salesperson)
        for discount in discounts:
            db.session.add(discount)
        db.session.commit()

def create_tables():
    with app.app_context():
        db.create_all()


if __name__ == "__main__":
    create_tables()
    seed_db()