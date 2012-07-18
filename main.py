# Handlers
from h_main import *
from h_static import *
from h_login_signup import *
from h_game_setup import *
from h_game_play import *
from h_question_submit import *
from h_question_list import *


app = webapp2.WSGIApplication([('/', MenuPage),
	                           ('/login/?', LoginPage),
							   ('/logout/?', LogoutPage),
							   ('/signup/?', SignupPage),
							   ('/play/?', PlayPage),
							   ('/play/Choose/?', ChooseGamePage),
							   ('/play/GameStart/?', StartGamePage),
							   ('/play/Game/?', PlayGamePage),
							   ('/submitQuestion/?', SubmitPage),
							   ('/listQuestions/?(?:.json)?', ListQuestionsPage),
							   ('/rules/?', RulesPage)],
							  debug=True)