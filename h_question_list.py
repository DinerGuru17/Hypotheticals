from h_main import *
from db_questions import *

class ListQuestionsPage(Handler):
	def get(self):
		questions = Questions.by_user(self.pid)
		if self.request.url.endswith('.json'):
			self.render_json([q.as_dict(self.player.username) for q in questions])
		else:
			self.params['questions'] = questions
			self.render("question_list.html", **self.params)
