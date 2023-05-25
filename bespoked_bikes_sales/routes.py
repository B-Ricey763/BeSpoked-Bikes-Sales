import calendar
from datetime import date
from flask import redirect, render_template, request
from flask_wtf import FlaskForm
from bespoked_bikes_sales.forms import *
from bespoked_bikes_sales.models import *
from bespoked_bikes_sales import app
from functools import partial

# HELPER FUNCTION(S)
#
# Most of the helpers are only used once and thus they
# are within their respective routes, but this one gets a bit
# more love

def price_of_sale(sale):
	# Discounts are never explicitly shown or added in the UI, but
	# as it was a requirement, some discounts were included on the backend 
	# (including 2 discounts on one item), and we have to factor them in 
	# when figuring out the price
    total_discount = 0
    # Assumes there can be multiple discounts for one item.
    for discount in sale.product.discounts:
        if discount.begin_date < sale.sales_date and discount.end_date > sale.sales_date:
            total_discount += discount.discount_percentage
    return sale.product.sale_price * (1 - total_discount)

# ROUTES

@app.route("/")
def index():
    return render_template("index.jinja")

@app.route("/salespeople")
def salespeople():
    people = db.session.execute(db.select(Salesperson).order_by(Salesperson.last_name)).scalars()
    return render_template("salespeople.jinja", salespeople=people)

@app.route("/salespeople/<int:id>", methods=["GET", "POST"])
def update_salesperson(id):
    person = Salesperson.query.get_or_404(id)
    form = UpdateSalespersonForm()

    if request.method == "GET":
        # Populate the form with the current db entry so user can edit
        form = UpdateSalespersonForm(obj=person, formdata=None)
    
    # Make sure we can't enter a duplicate salesperson
    def validate_no_duplicate_salesperson(id, form, field):
        duplicate = db.session.execute(db.select(Salesperson).where(Salesperson.first_name == field.data).where(Salesperson.last_name == form.last_name.data)).scalar()
        if duplicate and duplicate.id != id:
            raise ValidationError("Already a salesperson with the same name!")
    # We have to check the length of the validators to make sure we 
    # don't add extra of the same one after resubmissions
    if request.method == "POST":
        # Since we are validating the form dynamically, we have to manually
        # insert the validator function... I know, it's ugly
        if len(form.first_name.validators) < 2:
            # partial function application to keep the id variable in scope... python
            # why is there no first class functions??!?!?!
            form.first_name.validators.append(partial(validate_no_duplicate_salesperson, id))
        else:
            # And for some reason you have to do this every time to keep the current context??
            # I don't really know why I need this, but the form somehow persists a bit in between
            # requests so we have to re-add it every time -- don't really have time to figure out
            form.first_name.validators[1] = partial(validate_no_duplicate_salesperson, id)

    if form.validate_on_submit():
        # Convenient use of populate_obj so we don't have to compare
        # each and every field of the form with the person model 
        form.populate_obj(person)
        db.session.commit()
        # Bring them back to the list to see their updates
        return redirect("/salespeople")

    # We probably don't need to send the person as well as the form,
    # but for the rare case where the form is invalid, we don't want the 
    # title updating to something invalid as well
    return render_template("update_salesperson.jinja", person=person, form=form)

@app.route("/products")
def products():
    product_list = db.session.execute(db.select(Product).order_by(Product.sale_price)).scalars()
    return render_template("products.jinja", products=product_list)

@app.route("/products/<int:id>", methods=["GET", "POST"])
def update_product(id):
    # Basically the same deal as update_salesperson, but for products!
    product = Product.query.get_or_404(id)

    form = UpdateProductForm()
    if request.method == "GET":
        form = UpdateProductForm(obj=product, formdata=None)

	# No duplicate products allowed!
    def validate_no_duplicate_product(id, form, field):
        duplicate = db.session.execute(db.select(Product).where(Product.name == field.data)).scalar()
        if duplicate and duplicate.id != id:
            raise ValidationError("Already a product with the same name!")
    # Same mess for this as for the salesperson...
    if request.method == "POST":
        if len(form.name.validators) < 2:
            form.name.validators.append(partial(validate_no_duplicate_product, id))
        else:
            # My eyes..... 
            form.name.validators[1] = partial(validate_no_duplicate_product, id)

    if form.validate_on_submit():
        form.populate_obj(product)
        db.session.commit()
        return redirect("/products")

    return render_template("update_product.jinja", product=product, form=form)

@app.route("/customers")
def customers():
    customer_list = db.session.execute(db.select(Customer).order_by(Customer.last_name)).scalars()
    return render_template("customers.jinja", customers=customer_list)

@app.route("/sales", methods=["GET", "POST"])
def sales():
    def make_sale_readable(sale):
        return {
            "product": sale.product.name,
            "customer": f"{sale.customer.first_name} {sale.customer.last_name}",
            "date": sale.sales_date,
            "price": price_of_sale(sale), 
            "salesperson": f"{sale.salesperson.first_name} {sale.salesperson.last_name}",
            "commission": price_of_sale(sale) * sale.product.commission_percentage, 
        }


    sales_list = db.session.execute(db.select(Sale)).scalars()
    filter_form: FlaskForm = FilterSalesForm()
    if filter_form.validate_on_submit():
        # If they want a date filter, we do that
        sales_list = filter(
            lambda s: filter_form.start_date.data < s.sales_date < filter_form.end_date.data, sales_list)

    # Since a sale is basically just a list of foreign keys, we have to polish it up a bit
    readable_sales = map(make_sale_readable, sales_list)
    return render_template("sales.jinja", sales=readable_sales, form=filter_form)

@app.route("/create-sale", methods=["GET", "POST"])
def create_sale():
    form = CreateSaleForm()

	# Make sure the dates in which the salesperson is working
    # contains the requested sales date
    def validate_salesperson_date(form, field):
        salesperson = Salesperson.query.get(field.data)
        if salesperson.start_date > form.sales_date.data or form.sales_date.data > salesperson.termination_date:
            raise ValidationError("Salesperson is not active during sales date!")

    if request.method == "POST" and len(form.salesperson.validators) < 2:
        form.salesperson.validators.append(validate_salesperson_date)

    # Dynamically populate the dropdown list since it's sourced from the database 
    # This use of list comprehensions should've been neat, but honestly it's just ugly.
    # Gets the job done though 
    form.product.choices = [(product.id, product.name) for product in db.session.execute(db.select(Product)).scalars()]
    form.salesperson.choices = [(sp.id, f"{sp.first_name} {sp.last_name}") for sp in db.session.execute(db.select(Salesperson)).scalars()]
    form.customer.choices = [(c.id, f"{c.first_name} {c.last_name}") for c in db.session.execute(db.select(Customer)).scalars()]
    if form.validate_on_submit():
        new_sale = Sale(
            product_id=form.product.data,
            salesperson_id=form.salesperson.data,
            customer_id = form.customer.data,
            sales_date = form.sales_date.data 
        )
        db.session.add(new_sale) 
        db.session.commit()
        return redirect("/sales")
    return render_template("create_sale.jinja", form=form, today=date.today())

@app.route("/sales-report", methods=["GET", "POST"])
def sales_report():
    # Default year is this year
    year = date.today().year
    form = YearReportForm()
    
    if form.validate_on_submit():
        # If they specify a year and POST it, we change it 
        year = form.year.data

    # This entire next section of code could've been a lot more 
    # concise using functional programming strategies like folds, maps, and filters
    # but it would just not work very well in python... this does work nicely though 
    quarters = []
    for start_month in range(1, 12, 3):
        end_month = start_month + 2
        start_of_qtr = date(year, start_month, 1)
        # I have to this convoluted thing at the end to determine when months are 30 vs 31 days
        end_of_qtr = date(year, end_month, calendar.monthrange(year, end_month)[1])
        people = db.session.execute(db.select(Salesperson).where(Salesperson.start_date <= end_of_qtr).where(Salesperson.termination_date > start_of_qtr)).scalars()
        qtr = []
        for person in people:
            total_commission = 0
            for sale in filter(lambda s: s.sales_date > start_of_qtr and s.sales_date < end_of_qtr, person.sales):
                total_commission += price_of_sale(sale) * sale.product.commission_percentage
            qtr.append({
                "name": f"{person.first_name} {person.last_name}",
                "total_commission": total_commission
            })
        
        quarters.append(qtr)
    return render_template("sales_report.jinja", quarters=enumerate(quarters), form=form)