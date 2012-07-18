from functions import *
from db_games import *
from db_questions import *
from db_rounds import *
from h_main import *

class Game_Handler(LI_Handler):
	def add_game(self, GID):
		self.set_secure_cookie('game_id', str(GID))

	def initialize(self, *a, **kw):
		LI_Handler.initialize(self, *a, **kw)
		self.gid = self.read_secure_cookie('game_id')
		self.params['gid'] = self.gid
		if self.gid:
			self.g_players = Games.by_gid(self.gid).Player_Info
			self.g_player = by_pid(self.pid, self.g_players)
			self.params['g_players'] = self.g_players
			self.params['g_player'] = self.g_player

class PlayPage(Game_Handler):
	def get(self):
		self.links.append(link_as_dict('Start a New Game', '/play/Choose?q=new'))
		self.links.append(link_as_dict('Join an Existing Game', '/play/Choose?q=join'))
		self.links.append(link_as_dict('Rejoin an Existing Game', '/play/Choose?q=rejoin'))
		self.params['menu'] = self.links
		self.render("base.html", **self.params)

class ChooseGamePage(Game_Handler):
	def get(self):
		choice = self.request.get('q')
		self.params['pseudonym'] = self.player.username

		if choice == 'new':
			self.params['Game_Text'] = 'Create Game'
			self.params['game_id'] = make_salt(7)
		elif choice == 'join':
			self.params['Game_Text'] = 'Join Game'
		elif choice == 'rejoin':
			self.params['Game_Text'] = 'Rejoin Game'
			if self.gid:
				self.params['game_id'] = self.gid
		else:
			self.redirect('/play')

		self.render("game_choose.html", **self.params)

	def post(self):
		choice = self.request.get('q')
		
		if choice == 'new':
			self.PostChoose_new()
		elif choice == 'join':
			self.PostChoose_join()
		elif choice == 'rejoin':
			self.PostChoose_rejoin()
		else:
			self.redirect('/play')

	def PostChoose_new(self):
		pseudonym = self.request.get('pseudonym')
		game_id = self.request.get('game_id')
		g = Games.by_gid(game_id)
		success = True

		if g:
			self.params['game_error'] = 'That was not a unique Game ID.'
			game_id = make_salt(7)
			success = False

		if not valid_username(game_id):
			self.params['game_error'] = 'That was not a valid Game ID.'
			game_id = make_salt(7)
			success = False

		if not valid_username(pseudonym):

			self.params['pseudonym_error'] = 'That was not a valid Pseudonym.'
			pseudonym = self.player.username
			success = False

		if success:
			g = Games.new_game(game_id, format_player_info(self.pid, pseudonym))
			questions = []

		#	question_master = Players.by_name('QuestionMaster')
		#	for question in Questions.by_user(str(question_master.key().id())):
		#		questions.append(str(question.key().id()))			
			for question in Questions.by_user(self.pid):
				questions.append(str(question.key().id()))
			g.Questions_IDs = questions
			
			g.put()
			self.add_game(game_id)
			self.redirect('/play/GameStart')

		else:
			self.params['game_id'] = game_id
			self.params['pseudonym'] = pseudonym
			self.params['Game_Text'] = 'Create Game'
			self.render("game_choose.html", **self.params)

	def PostChoose_join(self):
		pseudonym = self.request.get('pseudonym')
		game_id = self.request.get('game_id')
		g = Games.by_gid(game_id)
		success = True 

		if not g:
			self.params['game_error'] = 'That Game ID does not exist.'
			success = False

		if success and by_pid(self.pid, g.Player_Info):
			self.params['game_error'] = 'Your User is already registered for this game.'
			success = False

		if not valid_username(pseudonym):
			self.params['pseudonym_error'] = 'That was not a valid Pseudonym.'
			pseudonym = self.player.username
			success = False

		if success and by_pseudonym(pseudonym, g.Player_Info):
			self.params['pseudonym_error'] = 'Someone is already playing with that Pseudonym.'
			pseudonym = self.player.username
			success = False

		if success:
			questions = []
			for question in Questions.by_user(self.pid):
				questions.append(str(question.key().id()))
			g.Questions_IDs = g.Questions_IDs + questions

			g.Player_Info.append(format_player_info(self.pid, pseudonym))
			g.put()
			self.add_game(game_id)
			self.redirect('/play/GameStart')

		else:
			self.params['game_id'] = game_id
			self.params['pseudonym'] = pseudonym
			self.params['Game_Text'] = 'Join Game'
			self.render("game_choose.html", **self.params)

	def PostChoose_rejoin(self):
		game_id = self.request.get('game_id')
		g = Games.by_gid(game_id)
		success = True

		g = Games.by_gid(game_id)
		if not g:
			self.params['game_error'] = 'That Game ID does not exist.'
			success = False

		if success and not by_pid(self.pid, g.Player_Info):
			self.params['game_error'] = 'You must first join this game.'
			success = False

		if success:
			self.add_game(game_id)
			if not g.Rounds_IDs:
				self.redirect('/play/GameStart')
			else:
				self.redirect('/play/Game')

		else:
			self.params['game_id'] = game_id
			self.params['Game_Text'] = 'Rejoin Game'
			self.render("game_choose.html", **self.params)

class StartGamePage(Game_Handler):
	def get(self):
		if not self.gid:
			self.redirect('/play')

		self.render("game_almost.html", **self.params)

	def post(self):
		g = Games.by_gid(self.gid)
		
		if len(g.Player_Info) < 3:
			self.params['error'] = 'You need at least three players to play.'
			self.render("game_almost.html", **self.params)

		elif Rounds.by_rid(make_round_id(self.gid, 1)):
			#add player after first round is over.
			self.redirect('/play/Game')

		else:
			player = []
			for Player in g.Player_Info:
				player.append(Player.split('|')[1])
			r = Rounds.first_round(make_round_id(self.gid, 1), player)
			r.put()	

			g.Rounds_IDs = [r.Round_ID]
			g.put()
		
			self.redirect('/play/Game')
