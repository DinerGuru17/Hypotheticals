from h_main import *
from db_questions import *

class SubmitPage(LI_Handler):
	def get(self):
		self.links.append(link_as_dict('View Submitted Questions', '/listQuestions'))
		self.params['questionList'] = 'listQuestions'
		self.params['message'] = " "
		self.params['menu'] = self.links
		self.render("question_submit.html", **self.params)

	def post(self):
		self.links.append(link_as_dict('View Submitted Questions', '/listQuestions'))
		question = self.request.get('question')
		category = self.request.get('category')
		self.params['questionList'] = 'listQuestions'
		self.params['menu'] = self.links

		if question and category:
			if len(str(question)) > 500:
				self.params['question'] = question
				self.params['error'] = "Your question must be 500 characters or fewer."
				self.render("question_submit.html", **self.params)

			elif not is_printable(question):
				self.params['question'] = question
				self.params['error'] = "Your question must contain only numbers, characters and punctuation."
				self.render("question_submit.html", **self.params)

			else:
				q = Questions.register(self.pid, question, category)
				q.put()

				self.params['message'] = "Thank you. Submit another question."
				self.render("question_submit.html", **self.params)

		else:
			self.params['error'] = "Please enter a question"
			self.render("question_submit.html", **self.params)