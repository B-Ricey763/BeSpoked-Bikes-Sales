from typing import List
from datetime import date
from bespoked_bikes_sales import db

Mapped = db.Mapped
mapped_column = db.mapped_column
String = db.String
relationship = db.relationship
ForeignKey = db.ForeignKey

# Because of Python 3.10, we can use type annotations on the models
# to faciliate their creation with as little boilerplate as possible.
#
# Each model defines a table of records in our database, with relational
# mappings denoted by the relationship() function

class Product(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    manufacturer: Mapped[str] = mapped_column(String(50))
    style: Mapped[str] = mapped_column(String(50))
    purchase_price: Mapped[float] = mapped_column(default=0.0)
    sale_price: Mapped[float] = mapped_column(default=0.0)
    quantity: Mapped[int] = mapped_column(default=0)
    commission_percentage: Mapped[float] = mapped_column(default=0.0)

    discounts: Mapped[List["Discount"]] = relationship()

class Salesperson(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(20))
    last_name: Mapped[str] = mapped_column(String(20))
    address: Mapped[str] = mapped_column(String(50))
    phone: Mapped[str] = mapped_column(String(10))
    start_date: Mapped[date] = mapped_column()
    termination_date: Mapped[date] = mapped_column()
    manager: Mapped[str] = mapped_column(String(40))
	# This is the only bidirectional relationship, since both
	# salespeople need their sales and sales need to know who sold them
    sales: Mapped[List["Sale"]] = relationship(back_populates="salesperson")

class Customer(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(20))
    last_name: Mapped[str] = mapped_column(String(20))
    address: Mapped[str] = mapped_column(String(50))
    phone: Mapped[str] = mapped_column(String(10))
    start_date: Mapped[date] = mapped_column()

class Sale(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    sales_date: Mapped[date] = mapped_column()

    product_id: Mapped[int] = mapped_column(ForeignKey("product.id"))
    product: Mapped[Product] = relationship()
    customer_id: Mapped[int] = mapped_column(ForeignKey("customer.id"))
    customer: Mapped[Customer] = relationship()
    salesperson_id: Mapped[int] = mapped_column(ForeignKey("salesperson.id"))
    salesperson: Mapped[Salesperson] = relationship(back_populates="sales")

class Discount(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    begin_date: Mapped[date] = mapped_column()
    end_date: Mapped[date] = mapped_column()
    discount_percentage: Mapped[float] = mapped_column()

    product_id: Mapped[int] = mapped_column(ForeignKey("product.id"))
