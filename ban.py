import time

class BanTracker:

	def __init__(self):
		self.banlist = []
		self.unban_queue = []

	def update_banlist(self):
		for user in self.banlist:
			delta_time = time.time() - user.time_of_ban
			if delta_time > user.duration:
				self.unban_queue.append(user)
				self.banlist.remove(user)

class BannedUser:

	def __init__(self, nick, channel, duration, reason=""):
		self.nick = nick
		self.channel = channel
		self.time_of_ban = time.time()
		self.duration = duration
		self.reason = reason

	@property
	def time_left(self):
		delta_time = time.time() - user.time_of_ban
		return self.duration - delta_time
