import os
from flask import Flask, url_for, redirect, render_template, request
from flask_sqlalchemy import SQLAlchemy
from wtforms import form, fields, validators
import flask_admin as admin
import flask_login as login
from flask_admin.contrib import sqla
from flask_admin import helpers, expose
from werkzeug.security import generate_password_hash, check_password_hash


# Create Flask application
app = Flask(__name__)

# Create dummy secrey key so we can use sessions
app.config['SECRET_KEY'] = 'mysecretkey'

# Create in-memory database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:''@localhost/test_user'
db = SQLAlchemy(app)



class Staff(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(50), nullable=False, unique=True)
	password = db.Column(db.String(50), nullable=False)
	email = db.Column(db.String(50), nullable=False)
	login = db.Column(db.String(100), nullable=False, unique=True)
	manage = db.relationship('Manage', backref='staff', lazy=True)
	
	def __str__(self):
		return self.name
	
	@property
	def is_authenticated(self):
		return True

	@property
	def is_active(self):
		return True

	@property
	def is_anonymous(self):
		return False

	def get_id(self):
		return self.id

	# Required for administrative interface
	def __unicode__(self):
		return self.username



class LoginForm(form.Form):
	login = fields.StringField(validators=[validators.required()])
	password = fields.PasswordField(validators=[validators.required()])

	def validate_login(self, field):
		user = self.get_user()

		if user is None:
			raise validators.ValidationError('Invalid user')

		if user.password != self.password.data:
			raise validators.ValidationError('Invalid password')

	def get_user(self):
		return db.session.query(Staff).filter_by(login=self.login.data).first()

class RegistrationForm(form.Form):
	login = fields.StringField(validators=[validators.required()])
	email = fields.StringField()
	password = fields.PasswordField(validators=[validators.required()])

	def validate_login(self, field):
		if db.session.query(AdminUser).filter_by(login=self.login.data).count() > 0:
			raise validators.ValidationError('Duplicate username')



def init_login():
	login_manager = login.LoginManager()
	login_manager.init_app(app)

	# Create user loader function
	@login_manager.user_loader
	def load_user(user_id):
		return db.session.query(Staff).get(user_id)


class MyModelView(sqla.ModelView):

	def is_accessible(self):
		return login.current_user.is_authenticated

	can_delete = False

	can_create = False
	
	can_edit = False

class MyyModelView(sqla.ModelView):

	def is_accessible(self):
		return login.current_user.is_authenticated

	can_delete = True

	can_create = False
	
	can_edit = False

class MyAdminIndexView(admin.AdminIndexView):
	@expose('/')
	def index(self):
		if not login.current_user.is_authenticated:
			return redirect(url_for('.login_view'))
		return super(MyAdminIndexView, self).index()

	@expose('/login/', methods=('GET', 'POST'))
	def login_view(self):
		# handle user login
		form = LoginForm(request.form)
		if helpers.validate_form_on_submit(form):
			user = form.get_user()
			login.login_user(user)

		if login.current_user.is_authenticated:
			return redirect(url_for('.index'))
		#link = '<p>Don\'t have an account? <a href="' + url_for('.register_view') + '">Click here to register.</a></p>'
		self._template_args['form'] = form
		#self._template_args['link'] = link
		return super(MyAdminIndexView, self).index()


	


	@expose('/logout/')
	def logout_view(self):
		login.logout_user()
		return redirect(url_for('.index'))


@app.route('/')
def index():
	return render_template('index.html')

init_login()


class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	first_name = db.Column(db.String(64), nullable=False)
	last_name = db.Column(db.String(50), nullable=False)
	password = db.Column(db.String(50), nullable=False)
	email = db.Column(db.String(128), nullable=False, unique=True)
	cafeorder = db.relationship('Cafe_order', backref='user', lazy=True)
	
	def __str__(self):
		return self.first_name

class Cafe_order(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	food_id = db.Column(db.Integer, db.ForeignKey('food.id'))
	drink_id = db.Column(db.Integer, db.ForeignKey('drink.id'))
	manageorder = db.relationship('Manage', backref='cafe_order', lazy=True)

class Drink(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(50), nullable=False)
	price = db.Column(db.Integer, nullable=False)
	size = db.Column(db.String(50), nullable=False)
	image = db.Column(db.String(300), nullable=False)
	description = db.Column(db.String(300), nullable=False)
	cafeorder = db.relationship('Cafe_order', backref='drink', lazy=True)

	def __str__(self):
		return self.name


class Food(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(50), nullable=False, unique=True)
	stock = db.Column(db.Integer, nullable=False)
	price = db.Column(db.Integer, nullable=False)
	image = db.Column(db.String(300), nullable=False)
	description = db.Column(db.String(300), nullable=False)
	cafeorder = db.relationship('Cafe_order', backref='food', lazy=True)
	
	def __str__(self):
		return self.name

class Manage(db.Model):
	id = db.Column(db.Integer, primary_key =True)
	isdone = db.Column(db.Boolean, default=False, nullable=False)
	order_id = db.Column(db.Integer, db.ForeignKey('cafe_order.id'))
	staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'))




admin = admin.Admin(app, 'Staff', index_view=MyAdminIndexView(url ='/staff'), base_template='my_master.html')


admin.add_view(MyModelView(Staff, db.session))
admin.add_view(MyyModelView(Cafe_order, db.session))
admin.add_view(MyModelView(Manage, db.session))
	
#db.create_all()	


if __name__ == '__main__':

    app.run('0.0.0.0', 9000, debug=True)
