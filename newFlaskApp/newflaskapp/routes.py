from flask import render_template, url_for, flash, redirect, request
from newflaskapp import app, db, bcrypt
from newflaskapp.forms import RegistrationForm, LoginForm, UpdateAccountForm
from newflaskapp.models import User
from flask_login import login_user, current_user, logout_user, login_required

from sqlalchemy.exc import IntegrityError




@app.route('/')
@app.route('/home')
def home():
	return render_template('index.html')

@app.route('/resource')
@login_required
def resource():
	return render_template('resource.html')

@app.route('/register', methods= ['GET','POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = RegistrationForm()
	if form.validate_on_submit() :
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user = User(username = form.username.data, email= form.email.data, password = hashed_password)

		db.session.add(user)
		db.session.flush()
		db.session.commit()
		flash(f'Your account has been created !! You will be now able to Log In.', 'success')
		return redirect(url_for('login'))
	return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user and bcrypt.check_password_hash(user.password, form.password.data):
			login_user(user, remember = form.remember.data)
			next_page = request.args.get('next')
			return redirect(next_page) if next_page else redirect(url_for('home'))
		else:
			flash(f'Login Unsuccessful. Please check username and password', 'danger')
	return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
	logout_user()
	return redirect(url_for('home'))


@app.route("/account",  methods=['GET', 'POST'])
@login_required
def account():
	form = UpdateAccountForm()
	if form.validate_on_submit():
		current_user.username = form.username.data
		current_user.email = form.email.data
		db.session.commit()
		flash('Your account has been updated!!', 'success' )
		return redirect(url_for('account'))

	elif request.method == 'GET':
		form.username.data = current_user.username
		form.email.data = current_user.email

	image_file = url_for('static', filename = 'images/'+ current_user.image_file)
	return render_template('account.html', title = 'Account', image_file = image_file, form =form)
