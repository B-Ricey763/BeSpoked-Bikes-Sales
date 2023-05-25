from datetime import date
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, FloatField, IntegerField, SelectField, ValidationError

from wtforms.validators import InputRequired
class UpdateSalespersonForm(FlaskForm):
    first_name = StringField("First Name", validators=[InputRequired()])
    last_name = StringField("Last Name", validators=[InputRequired()])
    address = StringField("Address")
    phone = StringField("Phone")
    start_date = DateField("Start Date")
    termination_date = DateField("Termination Date")
    manager = StringField("Manager")

    def validate_termination_date(form, field):
        if field.data < form.start_date.data:
            raise ValidationError("Termination date must be after start date!")

class UpdateProductForm(FlaskForm):
    name = StringField("Name", validators=[InputRequired()])
    manufacturer = StringField("Manufacturer")
    style = StringField("Style")
    purchase_price = FloatField("Purchase Price")
    sale_price = FloatField("Sale Price")
    quantity = IntegerField("Quantity on Hand")
    commission_percentage = FloatField("Commission Percentage")

class CreateSaleForm(FlaskForm):
    product = SelectField("Product", coerce=int)
    salesperson = SelectField("Salesperson", coerce=int)
    customer = SelectField("Customer", coerce=int)
    sales_date = DateField("Sales Date")

    def validate_sales_date(form, field):
        if field.data > date.today():
            raise ValidationError("Sales Date cannot be in the future!")

class FilterSalesForm(FlaskForm):
    start_date = DateField("Start")
    end_date = DateField("End")

class YearReportForm(FlaskForm):
    year = SelectField("Year", choices=[(y, y) for y in range(date.today().year, 2000, -1)], coerce=int)
