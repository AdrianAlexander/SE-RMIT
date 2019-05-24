class LoginForm(Form):  # Create Login Form
	username = StringField('', [validators.length(min=1)],
						   render_kw={'autofocus': True, 'placeholder': 'Username'})
	password = PasswordField('', [validators.length(min=3)],
							 render_kw={'placeholder': 'Password'})


# User Login
@app.route('/login', methods=['GET', 'POST'])
@not_logged_in
def login():
	form = LoginForm(request.form)
	if request.method == 'POST' and form.validate():
		# GEt user form
		username = form.username.data
		# password_candidate = request.form['password']
		password_candidate = form.password.data

		# Create cursor
		cur = mysql.connection.cursor()

		# Get user by username
		result = cur.execute("SELECT * FROM users WHERE username=%s", [username])

		if result > 0:
			# Get stored value
			data = cur.fetchone()
			password = data['password']
			uid = data['id']
			name = data['name']

			# Compare password
			if sha256_crypt.verify(password_candidate, password):
				# passed
				session['logged_in'] = True
				session['uid'] = uid
				session['s_name'] = name
				x = '1'
				cur.execute("UPDATE users SET online=%s WHERE id=%s", (x, uid))

				return redirect(url_for('index'))

			else:
				flash('Incorrect password', 'danger')
				return render_template('login.html', form=form)

		else:
			flash('Username not found', 'danger')
			# Close connection
			cur.close()
			return render_template('login.html', form=form)
	return render_template('login.html', form=form)


@app.route('/out')
def logout():
	if 'uid' in session:
		# Create cursor
		cur = mysql.connection.cursor()
		uid = session['uid']
		x = '0'
		cur.execute("UPDATE users SET online=%s WHERE id=%s", (x, uid))
		session.clear()
		flash('You are logged out', 'success')
		return redirect(url_for('index'))
	return redirect(url_for('login'))
