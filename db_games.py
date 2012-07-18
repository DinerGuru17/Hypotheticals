from functions import *
from google.appengine.ext import db


def format_player_info(PID, pseudonym, score = 0):
	return str(PID) + '|' + str(pseudonym) + '|' + str(score)

#could be put into a class function (not a classmethod)
def by_pid(PID, players):
	for player in players:
		if player.split('|')[0] == PID:
			return player.split('|')
	return False

#could be put into a class function (not a classmethod)
def by_pseudonym(pseudonym, players):
	for player in players:
		if player.split('|')[1] == pseudonym:
			return player.split('|')
	return False

class Games(db.Model):
	Game_ID = db.StringProperty(required = True)
	Player_Info = db.StringListProperty(required = True)
	Questions_IDs = db.StringListProperty()
	Rounds_IDs = db.StringListProperty()

	@classmethod
	def new_game(cls, GID, player):
		g = Games(Game_ID = GID,
			      Player_Info = [])
		g.Player_Info.append(player)
		return g

	@classmethod
	def by_gid(cls, GID):
		return Games.all().filter('Game_ID =', GID).get()