from google.appengine.ext import db

class Questions(db.Model):
	Submitted_PID = db.StringProperty(required = True)
	Question = db.StringProperty(required = True)
	Category = db.StringProperty(required = True)

	@classmethod
	def register(cls, pid, question, category):
		return Questions(Submitted_PID = pid, 
						 Question = question, 
						 Category = category)

	@classmethod
	def by_user(cls, pid):
		return Questions.all().filter('Submitted_PID =', pid)
		
	def as_dict(self, username):
		d = {'submitted_by': self.Submitted_PID + '|' + username,
			 'question': self.Question,
			 'category': self.Category}
		return d