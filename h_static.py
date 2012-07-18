from h_main import *
from functions import *

class MenuPage(Handler):
	def get(self):
		if self.pid:
			self.links.append(link_as_dict('Logout', '/logout'))
		else:
			self.links.append(link_as_dict('Login', '/login'))
		self.links.append(link_as_dict('Play U.W. Hypotheticals', '/play'))
		self.links.append(link_as_dict('Submit Questions', '/submitQuestion'))
		self.links.append(link_as_dict('Read the Rules', '/rules'))
		self.params['menu'] = self.links

		self.render("base.html", **self.params)

class RulesPage(Handler):
	def get(self):
		self.render("rules.html", **self.params)