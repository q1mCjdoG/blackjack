class UserStats:

	def __init__(self, name, wallet):
		self.name = name
		self.wallet = wallet
		self.highscore = 0
		self.wallet_resets = 0
		self.games_won = 0
		self.games_lost = 0
		self.games_tied = 0

class UserTracker:
	
	def __init__(self):
		self.users = []
		
	def add_user_stats(self, new_user):
		self.users.append(new_user)
	
	def is_in_userlist(self, username):
		for user in self.users:
			if user.name == username:
				return True
		return False

	def get_user_stats(self, username):
		for user in self.users:
			if user.name == username:
				return user

	def get_topwins(self):
		return sorted(self.users, key=lambda user: user.games_won, reverse=True)

	def get_topties(self):
		return sorted(self.users, key=lambda user: user.games_won, reverse=True)

	def get_toplosses(self):
		return sorted(self.users, key=lambda user: user.games_lost, reverse=True)

	def get_topscores(self):
		return sorted(self.users, key=lambda user: user.wallet, reverse=True)

	def get_highscores(self):
		return sorted(self.users, key=lambda user: user.highscore, reverse=True)

	def get_lowestscores(self):
		return sorted(self.users, key=lambda user: user.wallet, reverse=False)

	def save_state(self, file):
		for user in self.users:				
			data = ""
			data += user.name + " "
			data += str(user.wallet) + " "
			data += str(user.wallet_resets) + " "
			data += str(user.games_won) + " "
			data += str(user.games_lost) + " "
			data += str(user.games_tied) + " "
			data += str(user.highscore) + " \n"
			file.write(data)

	def load_state(self, file):
		for line in file.readlines():
			data = line.split()
			name = data[0]
			wallet = int(data[1])
			wallet_resets = int(data[2])
			games_won = int(data[3])
			games_lost = int(data[4])
			games_tied = int(data[5])
			highscore = int(data[6])

			user = UserStats(name, wallet)
			user.wallet_resets = wallet_resets
			user.games_won = games_won
			user.games_lost = games_lost
			user.games_tied = games_tied			
			user.highscore = highscore
			self.add_user_stats(user)
