from functions import *
from db_games import *
from db_rounds import *
from db_questions import *
from h_main import *
from h_game_setup import Game_Handler
import random

class Game_Handler2(Game_Handler):
	def initialize(self, *a, **kw):
		Game_Handler.initialize(self, *a, **kw)
		if not self.gid:
			self.redirect('/play')
		self.g = Games.by_gid(self.gid)
		self.round_id = self.g.Rounds_IDs[len(self.g.Rounds_IDs) - 1]
		self.r = Rounds.by_rid(self.round_id)
		self.params['game'] = self.g
		self.params['round'] = self.r

		self.r_player = self.r.by_pseudonym(self.g_player[1])
		self.params['round_me'] = self.r_player[0]
		self.params['type'] = self.r_player[1]

class PlayGamePage(Game_Handler2):
	def get(self):
		if len(self.g.Questions_IDs) < 4:
			self.links.append(link_as_dict('New Game', '/play'))
			self.params['menu'] = self.links
			self.params['general_message'] = "You are out of questions, your game is over."
			self.render("base_round.html", **self.params)

		elif 'questioner' in self.r_player[1] and not self.r.Question_ID:
			self.params['questions'] = self.get_round_questions()
			self.params['question_message'] = "Choose a question to be answered this round."
			self.params['submit_text'] = 'Choose Question'
			self.render("game_question.html", **self.params)
		
		elif not self.r.Question_ID:
			self.links.append(link_as_dict('Refresh', '/play/Game'))
			self.params['menu'] = self.links
			self.params['general_message'] = "You are waiting for the questioner to choose a quetions."
			self.render("base_round.html", **self.params)

		elif self.r.all_answered() and self.guessed():
			self.params['Question_Text'] = Questions.get_by_id(int(self.r.Question_ID)).Question
			self.params['submit_text'] = 'Next Round'
			self.render("game_review.html", **self.params)

		elif self.r.all_answered() and 'reader' in self.r_player[1]:
			self.params['Question_Text'] = Questions.get_by_id(int(self.r.Question_ID)).Question
			self.params['r_players'] = self.r.aggregate_players()
			self.params['guess_message'] = "Read answers only. Check box guessed correctly."
			self.params['submit_text'] = 'Submit Guesses'
			self.render("game_guess.html", **self.params)

		elif self.r.all_answered():
			self.params['Question_Text'] = Questions.get_by_id(int(self.r.Question_ID)).Question
			self.links.append(link_as_dict('Refresh', '/play/Game'))
			self.params['menu'] = self.links
			self.params['game_message'] = "You are waiting for the questioner to guess who said what."
			self.render("game_wait.html", **self.params)

		elif '|' in self.r_player[0]:
			self.params['Question_Text'] = Questions.get_by_id(int(self.r.Question_ID)).Question
			self.links.append(link_as_dict('Refresh', '/play/Game'))
			self.params['menu'] = self.links
			self.params['game_message'] = "You are waiting for other players to answer the question."
			self.render("game_wait.html", **self.params)

		elif 'questioner' in self.r_player[1]:
			self.params['Question_Text'] = Questions.get_by_id(int(self.r.Question_ID)).Question
			self.links.append(link_as_dict('Refresh', '/play/Game'))
			self.params['menu'] = self.links
			self.params['game_message'] = "You are waiting for the players to answer your question."
			self.render("game_wait.html", **self.params)

		else:
			self.params['Question_Text'] = Questions.get_by_id(int(self.r.Question_ID)).Question
			self.params['submit_text'] = 'Submit Answer'
			self.render("game_answer.html", **self.params)

	def post(self):
		submit_type = self.request.get('button')
		success = True

		if submit_type == 'Choose Question':
			if self.request.get('question_id'):
				question_id = self.request.get('question_id')
				self.r.Question_ID = question_id
				self.r.put()
				self.g.Questions_IDs.remove(str(question_id))	
				self.g.put()			
			else:
				self.params['questions'] = self.get_round_questions()
				self.params['question_message'] = "Choose a question to be answered this round."
				self.params['question_error'] = "You must choose a question"
				self.params['submit_text'] = 'Choose Question'
				self.render("game_question.html", **self.params)
				success = False

		if submit_type == 'Next Round':
			if self.r.all_answered():
				next_r = self.r.next_round()
				self.g.Rounds_IDs.append(next_r.Round_ID)
				next_r.put()
				self.g.put()

		if submit_type == 'Submit Guesses':
			r_players = self.r.aggregate_players()
			score = 0
			for r_player in r_players:
				if self.request.get(r_player) == 'on':
					score = score + 1
			self.r.Questioner = self.r.Questioner + '|' + str(score)
			self.r.put()

			g_players = []
			for g_player in self.g.Player_Info:
				if g_player.split('|')[1] == self.r.Questioner.split('|')[0]:
					g_player = g_player.split('|')
					g_player[2] = str( int(g_player[2]) + score )
					g_players.append('|'.join(g_player))
				else:
					g_players.append(g_player)
			self.g.Player_Info = g_players
			self.g.put()

		if submit_type == 'Submit Answer':
			answer = self.request.get('answer')
			success = self.valid_answer(answer)
			if not success:
				self.params['Question_Text'] = Questions.get_by_id(int(self.r.Question_ID)).Question
				self.params['answer'] = answer
				self.params['submit_text'] = 'Submit Answer'
				self.render("game_answer.html", **self.params)
			else:
				self.submit_answer(answer)

		if success:
			self.redirect('/play/Game')

	def get_round_questions(self):
		g_questions = self.g.Questions_IDs
		r_questions = []

		for x in xrange(4):
			question_num = g_questions.pop(random.randrange(0,len(g_questions)))
			touple = [question_num, Questions.get_by_id(int(question_num)).Question]
			r_questions.append(touple)
		return r_questions

	def guessed(self):
		if '|' in self.r.Questioner:
			return True

	def generate_guess(self):
		self.r.Reader_Answer.split('|')

	def valid_answer(self, answer):
		if answer and len(answer) > 400:
			self.params['error_answer'] = "Your answer must be 400 characters or fewer."
			return False

		if answer == '':
			self.params['error_answer'] = "Please submit an answer."
			return False
			
		if not is_printable(answer) or '|' in answer:
			self.params['error_answer'] = "Your answer must only conain characters, numbers and punctuation."
			return False

		return True

	def submit_answer(self, answer):
		if 'reader' in self.r_player[1]:
			self.r.Reader_Answer = self.r.Reader_Answer + '|' + answer
			self.r.put()					
		if 'regular' in self.r_player[1]:
			pseudonyms = []
			for pseudonym in self.r.Pseudonym_Answer:
				if self.g_player[1] == pseudonym:
					pseudonym = pseudonym + '|' + answer
				pseudonyms.append(pseudonym)
			self.r.Pseudonym_Answer = pseudonyms
			self.r.put()