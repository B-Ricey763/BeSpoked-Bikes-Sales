from datetime import date
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, FloatField, IntegerField, SelectField, ValidationError

from wtforms.validators import InputRequired
class UpdateSalespersonForm(FlaskForm):
    first_name = StringField("First Name", validators=[InputRequired()])
    last_name = StringField("Last Name", validators=[InputRequired()])
    address = StringField("Address", validators=[InputRequired()])
    phone = StringField("Phone", validators=[InputRequired()])
    start_date = DateField("Start Date", validators=[InputRequired()])
    termination_date = DateField("Termination Date", validators=[InputRequired()])
    manager = StringField("Manager", validators=[InputRequired()])

    def validate_termination_date(form, field):
        if field.data < form.start_date.data:
            raise ValidationError("Termination date must be after start date!")

class UpdateProductForm(FlaskForm):
    name = StringField("Name", validators=[InputRequired()])
    manufacturer = StringField("Manufacturer", validators=[InputRequired()])
    style = StringField("Style", validators=[InputRequired()])
    purchase_price = FloatField("Purchase Price", validators=[InputRequired()])
    sale_price = FloatField("Sale Price", validators=[InputRequired()])
    quantity = IntegerField("Quantity on Hand", validators=[InputRequired()])
    commission_percentage = FloatField("Commission Percentage", validators=[InputRequired()])

class CreateSaleForm(FlaskForm):
    product = SelectField("Product", coerce=int)
    salesperson = SelectField("Salesperson", coerce=int, validators=[InputRequired()])
    customer = SelectField("Customer", coerce=int, validators=[InputRequired()])
    sales_date = DateField("Sales Date")

    def validate_sales_date(form, field):
        if field.data > date.today():
            raise ValidationError("Sales Date cannot be in the future!")

class FilterSalesForm(FlaskForm):
    start_date = DateField("Start")
    end_date = DateField("End")

    def validate_end_date(form, field):
        if not field.data or not form.start_date.data or field.data < form.start_date.data:
            raise ValidationError("End date must be after start date!")

class YearReportForm(FlaskForm):
    year = SelectField("Year", choices=[(y, y) for y in range(date.today().year, 2000, -1)], coerce=int)
