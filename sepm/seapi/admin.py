from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask import url_for, redirect
from flask_login import UserMixin, LoginManager, current_user, login_user

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:''@localhost/coffee_shop'
app.config['SECRET_KEY'] = 'mysecret'

db = SQLAlchemy(app)
login = LoginManager(app)



class User(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	first_name = db.Column(db.String(64))
	last_name = db.Column(db.String(50))
	password = db.Column(db.String(50))
	email = db.Column(db.String(128))
	cafeorder = db.relationship('Cafe_order', backref='user', lazy=True)

class UserView(ModelView):
	form_columns = ['id', 'name', 'password', 'email']
		

class Staff(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(50))
	password = db.Column(db.String(50))
	email = db.Column(db.String(50))
	manage = db.relationship('Manage', backref='staff', lazy=True)

class StaffView(ModelView):
	form_columns = ['id', 'name', 'password', 'email']
	

class Drink(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(50))
	price = db.Column(db.Integer)
	size = db.Column(db.String(50))
	cafeorder = db.relationship('Cafe_order', backref='drink', lazy=True)

class DrinkView(ModelView):
	form_columns = ['id', 'name', 'price', 'size']

class Food(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(50))
	stock = db.Column(db.Integer)
	price = db.Column(db.Integer)
	cafeorder = db.relationship('Cafe_order', backref='food', lazy=True)

class FoodView(ModelView):
	form_columns = ['id', 'name', 'stock', 'price']

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


@login.user_loader
def load_user(user_id):
	return User.query.get(user_id)


class MyModelView(ModelView):
	def is_accessible(self):
		return current_user.is_authenticated

admin = Admin(app)
admin.add_view(MyModelView(User, db.session))
admin.add_view(MyModelView(Staff, db.session))
admin.add_view(MyModelView(Cafe_order, db.session))
admin.add_view(MyModelView(Food, db.session))	
admin.add_view(MyModelView(Drink, db.session))
db.create_all()	

@app.route('/login')
def log():
	user = User.query.get(1)
	login_user(user)
	return 'loggedin'
	
if __name__ == '__main__':
	app.run('0.0.0.0', 8000, debug=True)
