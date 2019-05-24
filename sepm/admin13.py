from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_mysqldb import MySQL
from flask import url_for, redirect
from flask_basicauth import BasicAuth
from flask_login import UserMixin
from flask import render_template
from werkzeug.exceptions import HTTPException


app = Flask(__name__)
# .. read settings
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#app.config['MYSQL_HOST'] = 'localhost'
#app.config['MYSQL_USER'] = 'root'
#app.config['MYSQL_PASSWORD'] = ''
#app.config['MYSQL_DB'] = 'coffee_shop'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:''@localhost/coffee_shop'
app.config['SECRET_KEY'] = 'mysecret'
app.config['BASIC_AUTH_USERNAME'] = 'john'
app.config['BASIC_AUTH_PASSWORD'] = 'matrix'
app.config['BASIC_AUTH_FORCE'] = True


basic_auth = BasicAuth(app)

@app.route('/secret')
@basic_auth.required
def secret_view():
    return render_template('secret.html')

@app.route('/logout')
def Logout():
    raise AuthException('Successfully logged out.')


db = SQLAlchemy(app)


class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	first_name = db.Column(db.String(64), nullable=False)
	last_name = db.Column(db.String(50), nullable=False)
	password = db.Column(db.String(50), nullable=False)
	email = db.Column(db.String(128), nullable=False, unique=True)
	cafeorder = db.relationship('Cafe_order', backref='user', lazy=True)
	
	def __str__(self):
		return self.first_name

class UserView(ModelView):
	form_columns = ['first_name', 'last_name', 'password', 'email']
		

class Staff(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(50), nullable=False, unique=True)
	password = db.Column(db.String(50), nullable=False)
	email = db.Column(db.String(50), nullable=False)
	manage = db.relationship('Manage', backref='staff', lazy=True)
	
	def __str__(self):
		return self.name

class StaffView(ModelView):
	form_columns = ['name', 'password', 'email']
	

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

class DrinkView(ModelView):
	form_columns = ['name', 'price', 'size', 'image', 'description']

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

class FoodView(ModelView):
	form_columns = ['name', 'stock', 'price', 'image', 'description']

class Cafe_order(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	food_id = db.Column(db.Integer, db.ForeignKey('food.id'))
	drink_id = db.Column(db.Integer, db.ForeignKey('drink.id'))
	manageorder = db.relationship('Manage', backref='cafe_order', lazy=True)

class CafeView(ModelView):
	form_columns = ['id', 'user_id', 'food_id', 'drink_id']

class Manage(db.Model):
	id = db.Column(db.Integer, primary_key =True)
	isdone = db.Column(db.Boolean, default=False, nullable=False)
	order_id = db.Column(db.Integer, db.ForeignKey('cafe_order.id'))
	staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'))

class AdminUser(db.Model):
	id = db.Column(db.Integer, primary_key =True)
	login = db.Column(db.String(50))
	password = db.Column(db.String(50))

class MyModelView(ModelView):
	def is_accessible(self):
		return False

	def inaccessible_callback(self, name, **kwargs):
		return redirect(url_for('/admin'))

class AuthException(HTTPException):
	def __init__(self, message):
		super().__init__(message, Response( message, 401, {'WWW-Authenticate': 'Basic realm="Login Required"'}
	))

class ModelView(ModelView):
	def is_accessible(self):
		if not basic_auth.authenticate():
			raise AuthException('Not authenticated.')
		else:
			return True

	def inaccessible_callback(self, name, **kwargs):
		return redirect(basic_auth.challenge())


	

admin = Admin(app, name = 'Admin Panel')
admin.add_view(UserView(User, db.session))
admin.add_view(StaffView(Staff, db.session))
admin.add_view(ModelView(Cafe_order, db.session))
admin.add_view(FoodView(Food, db.session))	
admin.add_view(DrinkView(Drink, db.session))
admin.add_view(ModelView(AdminUser, db.session))	
db.create_all()	


	
if __name__ == '__main__':
	
	app.run('0.0.0.0', 8000, debug=True)
