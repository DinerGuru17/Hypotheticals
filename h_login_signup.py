from h_main import *

class LoginPage(LO_Handler):
	def get(self):
		self.links.append(link_as_dict('Sign Up!', '/signup'))
		self.params['menu'] = self.links
		self.render("login_signup.html", **self.params)

	def post(self):
		username = self.request.get('username')
		password = self.request.get('password')

		p = Players.by_name(username)
		if p and validate_password(password, p.password_hash):
			self.login(p)
			self.redirect('/')

		elif not p:
			self.params['username_error'] = "Invalid Username."

		elif not validate_password(password, p.password_hash):
			self.params['username'] = username
			self.params['password_error'] = "Invalid Password"

		self.links.append(link_as_dict('Sign Up!', '/signup'))
		self.params['menu'] = self.links
		self.render("login_signup.html", **self.params)

class LogoutPage(Handler):
	def get(self):
		self.logout()
		self.redirect('/')

class SignupPage(LO_Handler):
	def get(self):
		self.params['page_type'] = 'submit'
		self.render("login_signup.html", **self.params)

	def post(self):
		username = self.request.get('username')
		password = self.request.get('password')
		verify = self.request.get('verify')
		email = self.request.get('email')
		self.params['page_type'] = 'submit'
		self.params['username'] = username
		self.params['email'] = email
		success = True

		p = Players.by_name(username)
		if p:
			self.params['username_error'] = "That username is already taken."
			success = False

		if not valid_username(username):
			self.params['username_error'] = "That is not a valid username."
			success = False

		if not valid_password(password):
			self.params['password_error'] = "That is not a  valid password."
			success = False
		elif password != verify:
			self.params['verify_error'] = "Your passwords do not match."
			success = False

		if not valid_email(email):
			if success:
				self.params['password'] = password
			self.params['email_error'] = "That is not a valid email address."
			success = False

		if not success:
			self.render("login_signup.html", **self.params)
		else:
			p = Players.register(username, password, email)
			p.put()

			self.login(p)
			self.redirect('/')
