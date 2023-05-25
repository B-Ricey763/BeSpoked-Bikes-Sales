import calendar
from datetime import date
from flask import redirect, render_template, request
from flask_wtf import FlaskForm
from bespoked_bikes_sales.forms import *
from bespoked_bikes_sales.models import *
from bespoked_bikes_sales import app

# HELPER FUNCTIONS

def price_of_sale(sale):
    total_discount = 0
    # Assumes there can be multiple discounts for one item
    for discount in sale.product.discounts:
        if discount.begin_date < sale.sales_date and discount.end_date > sale.sales_date:
            total_discount += discount.discount_percentage
    return sale.product.sale_price * (1 - total_discount)

def validate_no_duplicate_product(form, field):
    duplicate = db.session.execute(db.select(Product).where(Product.name == field.data)).first()
    if duplicate:
        raise ValidationError("Already a product with the same name!")

def validate_no_duplicate_salesperson(form, field):
    duplicate_first = db.session.execute(db.select(Salesperson).where(Salesperson.first_name == field.data)).first()
    duplicate_last = db.session.execute(db.select(Salesperson).where(Salesperson.last_name == form.last_name.data)).first()
    if duplicate_first and duplicate_last:
        raise ValidationError("Already a salesperson with the same name!")

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
    # make this less ugly potentially
    if request.method == "GET":
        form = UpdateSalespersonForm(obj=person, formdata=None)
    
    if request.method == "POST":
        form.first_name.validators.append(validate_no_duplicate_salesperson)
    if form.validate_on_submit():
        form.populate_obj(person)
        db.session.commit()
        return redirect("/salespeople")

    return render_template("update_salesperson.jinja", person=person, form=form)

@app.route("/products")
def products():
    product_list = db.session.execute(db.select(Product).order_by(Product.sale_price)).scalars()
    return render_template("products.jinja", products=product_list)

@app.route("/products/<int:id>", methods=["GET", "POST"])
def update_product(id):
    product = Product.query.get_or_404(id)
    form = UpdateProductForm()
    # make this less ugly potentially
    if request.method == "GET":
        form = UpdateProductForm(obj=product, formdata=None)


    if request.method == "POST":
        form.name.validators.append(validate_no_duplicate_product)

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
    sales_list = db.session.execute(db.select(Sale)).scalars()
    filter_form: FlaskForm = FilterSalesForm()
    if filter_form.validate_on_submit():
        sales_list = filter(lambda s: filter_form.start_date.data < s.sales_date < filter_form.end_date.data, sales_list)

    def make_sale_readable(sale):
        return {
            "product": sale.product.name,
            "customer": f"{sale.customer.first_name} {sale.customer.last_name}",
            "date": sale.sales_date,
            "price": price_of_sale(sale), 
            "salesperson": f"{sale.salesperson.first_name} {sale.salesperson.last_name}",
            "commission": price_of_sale(sale) * sale.product.commission_percentage, 
        }
    readable_sales = map(make_sale_readable, sales_list)

    return render_template("sales.jinja", sales=readable_sales, form=filter_form)

@app.route("/create-sale", methods=["GET", "POST"])
def create_sale():
    form = CreateSaleForm()
    # Dynamically populate the dropdown list since it's sourced from the database 
    form.product.choices = [(product.id, product.name) for product in db.session.execute(db.select(Product)).scalars()]
    form.salesperson.choices = [(sp.id, f"{sp.first_name} {sp.last_name}") for sp in db.session.execute(db.select(Salesperson)).scalars()]
    form.customer.choices = [(c.id, f"{c.first_name} {c.last_name}") for c in db.session.execute(db.select(Customer)).scalars()]
    if request.method == "POST" and form.validate():
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
    year = date.today().year
    form = YearReportForm()
    print(form.validate())
    
    if form.validate_on_submit():
        year = form.year.data

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