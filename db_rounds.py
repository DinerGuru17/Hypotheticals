from functions import *
from google.appengine.ext import db

def make_round_id(game_id, round_num):
	return str(game_id) + '|' + str(round_num)

def next_round_id(round_id, inc = 1):
	info = str(round_id).split('|')
	return make_round_id(info[0], int(info[1]) + inc)


class Rounds(db.Model):
	Round_ID = db.StringProperty(required = True)
	Questioner = db.StringProperty(required = True)
	Reader_Answer = db.StringProperty(required = True)
	Pseudonym_Answer = db.StringListProperty(required = True)
	Question_ID = db.StringProperty()

	@classmethod
	def first_round(cls, round_id, players, question = None):
		r = Rounds(Round_ID = round_id,
				   Questioner = players.pop(),
				   Reader_Answer = players.pop(),
				   Pseudonym_Answer = players,
				   Question_ID = question)
		return r

	def next_round(self, question_id = None):
		pseudonyms = []
		for pseudonym in self.Pseudonym_Answer:
			pseudonyms.append(pseudonym.split('|')[0])
		pseudonyms.append(self.Reader_Answer.split('|')[0])

		r = Rounds(Round_ID = next_round_id(self.Round_ID),
				   Questioner = pseudonyms.pop(0),
				   Reader_Answer = self.Questioner.split('|')[0],
				   Pseudonym_Answer = pseudonyms,
				   Question_ID = question_id)
		return r

	def all_answered(self):
		if '|' not in self.Reader_Answer:
			return False
		else:
			for pseudonym in self.Pseudonym_Answer: 
				if '|' not in pseudonym:
					return False
		return True

	def aggregate_players(self):
		players = [self.Reader_Answer]
		for pseudonym in self.Pseudonym_Answer:
			players.append(pseudonym)
		return players
		
	@classmethod
	def by_rid(cls, round_id):
		r = Rounds.all().filter('Round_ID =', round_id)
		if r:
			return r.get()

	def by_pseudonym(self, pseudonym):
		if pseudonym == self.Questioner.split('|')[0]:
			return self.Questioner, 'player_questioner'
		elif pseudonym == self.Reader_Answer.split('|')[0]:
			return self.Reader_Answer, 'player_reader'
		else:
			for p in self.Pseudonym_Answer:
				if pseudonym == p.split('|')[0]:
					return p, 'player_regular'





