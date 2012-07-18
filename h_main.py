from functions import *
from db_players import *

import webapp2
import jinja2
import json
import os

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
							  autoescape = True)

class Handler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)

	def render_str(self, template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)

	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))

	def set_secure_cookie(self, name, value):
		cookie_value = make_secure_value(value)
		self.response.headers.add_header(
			'Set-Cookie',
			'%s=%s; Path=/' % (name, cookie_value))

	def read_secure_cookie(self, name):
		cookie_value = self.request.cookies.get(name)
		if check_secure_value(cookie_value):
			return str(cookie_value).split('|')[0]

	def render_json(self, q):
		json_txt = json.dumps(q)
		self.response.headers['Content-Type'] = 'application/json; charset=UTF-8'
		self.write(json_txt)

	def login(self, user):
		self.set_secure_cookie('player_id', str(user.key().id()))
		self.response.headers.add_header('Set-Cookie', 'game_id=; Path=/')

	def logout(self):
		self.response.headers.add_header('Set-Cookie', 'player_id=; Path=/')
		self.response.headers.add_header('Set-Cookie', 'game_id=; Path=/')

	def initialize(self, *a, **kw):
		webapp2.RequestHandler.initialize(self, *a, **kw)			
		self.params = dict()
		self.links = []
		self.pid = self.read_secure_cookie('player_id')
		if self.pid:
			self.player = Players.by_id(int(self.pid))
			if not self.player:
				self.logout()
				self.pid = None
			else:
				self.params['player'] = self.player

class LI_Handler(Handler):
	def initialize(self, *a, **kw):
		Handler.initialize(self, *a, **kw)
		if not self.pid:
			self.response.headers.add_header('Set-Cookie', 'game_id= ; Path/')
			self.redirect('/login')

class LO_Handler(Handler):
	def initialize(self, *a, **kw):
		Handler.initialize(self, *a, **kw)
		if self.pid:
			self.redirect('/')