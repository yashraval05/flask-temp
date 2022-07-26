from flask.helpers import flash
from market import app, db, admin
from flask import render_template, redirect, url_for, flash, request
from market.models import Item, User
from market.forms import RegisterForm, LoginForm, PurchaseItemForm, SellItemForm
from flask_login import login_user, logout_user, login_required, current_user

@app.route('/')
@app.route('/home')
def home_page():
    return render_template('index.html')


@app.route('/market',  methods=['GET', 'POST'])
@login_required
def market_page():

    purchase_form = PurchaseItemForm()
    selling_form = SellItemForm()

    if request.method == 'POST':
        
        # Purchase Item Logic 

        purchased_item = request.form.get('purchased_item')
        p_item_object = Item.query.filter_by(name=purchased_item).first()

        if p_item_object:

            if current_user.can_purchase(p_item_object):

                p_item_object.buy(current_user)
                flash(f'You have purchased a {p_item_object.name} for {p_item_object.price} Rs', category='success')

            else:
                flash(f'You do not have enough money to purchase {p_item_object.name}', category = 'danger')
        # Sell Item Logic

        sold_item = request.form.get('sold_item')
        s_item_object = Item.query.filter_by(name = sold_item).first()

        if s_item_object:

            if current_user.can_sell(s_item_object):

                s_item_object.sell(current_user)
                flash(f'You have sold {s_item_object.name} back to the market.', category = 'success')

            else:
                flash('Something went wrong tosell {s_item_object.name}', category = 'danger')

        return redirect(url_for('market_page'))
            
    if request.method == 'GET':

        items = Item.query.filter_by(owner = None)
        owned_items = Item.query.filter_by(owner = current_user.id)

        return render_template('market.html', items=items, purchase_form=purchase_form, owned_items=owned_items, selling_form=selling_form)


@app.route('/register', methods=['GET', 'POST'])
def register_page():

    form = RegisterForm()

    if form.validate_on_submit():
        user_to_create = User(username=form.username.data, 
                                email_address=form.email_address.data,
                                password=form.password1.data,
                                )
        db.session.add(user_to_create)
        db.session.commit()

        login_user(user_to_create)
        flash(f'Account created succesfully. You are now logged in as {user_to_create.username}', category='success')
        
        return redirect(url_for('market_page'))
    
    if form.errors != {}: #If there are no errors from the validations
        for err_msg in form.errors.values():
            flash(f'There was an error in creating user: {err_msg}', category='danger')
   
    return render_template('register.html', form=form)

@app.route('/login', methods = ['GET', 'POST'])
def login_page():

    form = LoginForm()

    if form.validate_on_submit(): #it will validate and submit action
        attempted_user = User.query.filter_by(username=form.username.data).first() #first() to get the object value, else it shows the object name
        if attempted_user and attempted_user.check_password_correction(
                                    attempted_password=form.password.data
                                    ):
            login_user(attempted_user)
            flash(f'Success! You are logged in as: {attempted_user.username}', category='success')
            
            return redirect(url_for('market_page'))


        else: 
            flash('Username and password are not matched. Please try again.', category='danger')


    return render_template('login.html', form=form)

@app.route('/logout')
def logout_page():
    logout_user()
    flash('You are logged out.', category='info')
    return redirect(url_for('home_page'))

@app.route('/create_admin', methods=['GET', 'POST'])
def create_admin():

    form = RegisterForm()

    if form.validate_on_submit():
        admin_user_to_create = User(username=form.username.data, 
                                email_address=form.email_address.data,
                                password=form.password1.data,
                                is_admin=True
                                )
        db.session.add(admin_user_to_create)
        db.session.commit()

        login_user(admin_user_to_create)
        flash(f'Admin Account created succesfully. You are now logged in as Admin {admin_user_to_create.username}', category='success')
        
        return redirect(url_for('market_page'))
    
    if form.errors != {}: #If there are no errors from the validations
        for err_msg in form.errors.values():
            flash(f'There was an error in creating user: {err_msg}', category='danger')
   
    return render_template('admin_register.html', form=form)