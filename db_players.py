from functions import *
from google.appengine.ext import db

class Players(db.Model):
	username = db.StringProperty(required = True)
	password_hash = db.StringProperty(required = True)
	email = db.StringProperty()

	@classmethod
	def by_id(cls, ID):
		return Players.get_by_id(ID)

	@classmethod
	def by_name(cls, username):
		p = Players.all().filter('username =', username).get()
		return p

	@classmethod
	def register(cls, username, password, email = None):
		password_hash = make_password_hash(password)
		return Players(username = username,
					   password_hash = password_hash,
					   email = email)

	@classmethod
	def login(cls, username, password):
		p = cls.by_name(username)
		if p and valid_pw(password, p.password_hash):
			return p
