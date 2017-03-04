import os
import random
import time
import usertracker
import irc
import ban

##Todo
##*Notes to DICK: 6,7,8 all suited bonus 21, Ace should be added as a 1 at 21 not 22, and Ties should be called Pushes 
##Hall of game

class Blackjack:

	def __init__(self, guest_player):
		colors = ["Diamonds", "Clubs", "Hearts", "Spades"]
		names = ["Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King"]
		values = [11, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10]
		self.deck = [Card(color, name, value) for color in colors for name, value in zip(names, values)]
		self.dealer = Player("Dealer")		
		self.guest_player = guest_player
		self.winner = None
		self.stalemate = False
		self.prep_game()

	def prep_game(self):
		self.shuffle_deck()
		
		self.guest_player.cards.append(self.deck.pop())
		self.guest_player.cards.append(self.deck.pop())
		self.set_score(self.guest_player)
		
		self.dealer.cards.append(self.deck.pop())
		self.dealer.cards.append(self.deck.pop())
		self.set_score(self.dealer)
		self.set_winner()

	def shuffle_deck(self):
		random.shuffle(self.deck)

	def process_turn(self):
		self.hit(self.guest_player)
		self.set_score(self.guest_player)
		self.set_bust(self.guest_player)
		if self.guest_player.bust:
			self.check_for_ace_card(self.guest_player)
		self.set_winner()
		if self.winner:
			return

		self.dealer_rules()	
		self.hit(self.dealer)
		self.set_score(self.dealer)
		self.set_bust(self.dealer)
		if self.dealer.bust:
			self.check_for_ace_card(self.dealer)
		self.set_winner()

	def dealer_rules(self):
		if self.dealer.score >= 17:
			self.dealer.hit = False
		else:
			self.dealer.hit = True

	def hit(self, player):
		if player.hit == True:	
			player.cards.append(self.deck.pop())

	def set_score(self, player):
		score = 0
		for card in player.cards:
			score += card.value
		player.score = score

	def set_bust(self, player):			
		if player.score > 21:
			player.bust = True
		if player.score <= 21:
			player.bust = False

	def check_for_ace_card(self, player):
		for card in player.cards:
			if card.name == "Ace":
				card.value = 1
			self.set_score(player)
			self.set_bust(player)
			if player.bust == False:
				return

	def set_winner(self):
		if self.guest_player.bust:
			self.winner = self.dealer
		if self.dealer.bust:
			self.winner = self.guest_player

		if self.guest_player.score == 21 and len(self.guest_player.cards) == 2:
			self.winner = self.guest_player		
		if self.dealer.score == 21 and len(self.dealer.cards) == 2:
			self.winner = self.dealer
		if self.guest_player.score == 21 and len(self.guest_player.cards) == 2 and self.dealer.score == 21 and len(self.dealer.cards) == 2:
			self.stalemate = True
	
		if self.guest_player.hit == False and self.dealer.hit == False:
			if self.guest_player.score > self.dealer.score and self.guest_player.bust != True:
				self.winner = self.guest_player
			if self.dealer.score > self.guest_player.score and self.dealer.bust != True:
				self.winner = self.dealer
			if self.guest_player.score == self.dealer.score:
				self.stalemate = True
		

class Player:

	def __init__(self, name):
		self.name = name
		self.cards = []
		self.score = 0
		self.bust = False
		self.hit = True

class Card:
	
	def __init__(self, color, name, value):
		self.name = name
		self.color = color
		self.value = value

def display_cards(irc, channel, blackjack):
	cardlist = ""
	for card in blackjack.guest_player.cards:
		cardlist += "[" + card.name + " of " + card.color + "] "
	irc.send_message(channel, blackjack.guest_player.name + "'s " + "cards - " + cardlist)

	cardlist = ""
	if blackjack.winner == None and blackjack.stalemate == False:
		cardlist += "[" + blackjack.dealer.cards[0].name + " of " + blackjack.dealer.cards[0].color + "] "
	else:
		for card in blackjack.dealer.cards:
			cardlist += "[" + card.name + " of " + card.color + "] "
	irc.send_message(channel, "Dealer's cards - " + cardlist)

def announce_winner(irc, channel, blackjack, wager):
	if blackjack.stalemate:
		irc.send_message(channel, "Draw!")
	else:				
		irc.send_message(channel, blackjack.winner.name + " wins!" + " +" + str(wager) + " added to " + blackjack.winner.name + "'s wallet")

def init_user_stats(user_tracker, user):
	if user_tracker.is_in_userlist(user):
		return
	user_stats = usertracker.UserStats(user, 1000)
	user_tracker.add_user_stats(user_stats)

def track_wins(blackjack, user_tracker):
	user_stats = user_tracker.get_user_stats(blackjack.guest_player.name)
	dealer_stats = user_tracker.get_user_stats(blackjack.dealer.name)
	if blackjack.stalemate:
		user_stats.games_tied += 1	
		dealer_stats.games_tied += 1
		return
	if blackjack.winner.name == blackjack.guest_player.name:
		user_stats.games_won += 1
		dealer_stats.games_lost += 1
		return
	if blackjack.winner.name == blackjack.dealer.name:
		user_stats.games_lost += 1
		dealer_stats.games_won += 1
		return

def track_highscores(blackjack, user_tracker):
	if blackjack.winner != None:
		user = user_tracker.get_user_stats(blackjack.winner.name)
		if user.wallet > user.highscore:
			user.highscore = user.wallet

def show_user_stats(irc, channel, user_tracker, username):
	if user_tracker.is_in_userlist(username) is not True:
		irc.send_message(channel, "No such user")
		return
	user_stats = user_tracker.get_user_stats(username)
	string = ""
	string += str(user_stats.name) + ":"	
	string += " Games Won: " + str(user_stats.games_won)
	string += " Games Lost: " + str(user_stats.games_lost)
	string += " Games Tied: " + str(user_stats.games_tied)
	string += " Wallet: " + str(user_stats.wallet)
	string += " Highscore: " + str(user_stats.highscore)
	irc.send_message(channel, string)

def adjust_wallets(blackjack, user_tracker, wager):
	user_stats = user_tracker.get_user_stats(blackjack.guest_player.name)
	dealer_stats = user_tracker.get_user_stats(blackjack.dealer.name)
	if blackjack.stalemate:
		return
	if blackjack.winner.name == blackjack.guest_player.name:
		dealer_stats.wallet -= wager
		user_stats.wallet += wager
	if blackjack.winner.name == blackjack.dealer.name:
		dealer_stats.wallet += wager
		user_stats.wallet -= wager
	

host = "irc.tripsit.me"
port = 6697
bot_nick = "blackjackbot"
password = ""
bot_channel = "##blackjack"
user_tracker = usertracker.UserTracker()
with open("savefile", "r") as savefile:
	user_tracker.load_state(savefile)

delay = .35
antiflood_timer = 0
antiflood_cooldown = 5

while True:
	irc = irc.Irc()
	irc.connect(host, port, True)
	irc.nick(bot_nick)
	irc.user(bot_nick)
	
	blackjack = None
	timer = 0

	bantracker = ban.BanTracker()

	dd = False
		
	while True:
		irc.update_message_queue()

		if irc.message_queue == []:
			break

		for message in irc.message_queue:

			print(message.suffix)
			
			if message.type == "PRIVMSG":

				if message.suffix.startswith("!play") and blackjack == None:
					if message.sender in [banned_user.nick for banned_user in bantracker.banlist]:
						irc.send_message(bot_channel, "Cooldown is still in effect")
						continue
		
					parameter = message.get_parameter("!play")
					if parameter == "":
						parameter = 0
					try:
						if parameter != "max":
							wager = int(parameter)
					except:
						irc.send_message(bot_channel, "Invalid wager parameter")
						continue

					blackjack = Blackjack(Player(message.sender))
					init_user_stats(user_tracker, message.sender)
					user_stats = user_tracker.get_user_stats(blackjack.guest_player.name)
					timer = time.time()

					if user_stats.wallet < 1:
						user_stats.wallet = 1000
						user_stats.wallet_resets += 1
						irc.send_message(bot_channel, "Your wallet has been reset")
					
					if parameter == "max":
						wager = user_stats.wallet

					if wager > user_stats.wallet:
						irc.send_message(bot_channel, "You can't bet that much")
						blackjack = None
						timer = 0				
						continue

					if wager < 0:
						irc.send_message(bot_channel, "You can't bet less than 0")
						blackjack = None
						timer = 0				
						continue

					display_cards(irc, bot_channel, blackjack)


				if message.suffix.startswith("!hit") and blackjack != None:
					if message.sender == blackjack.guest_player.name:
						blackjack.guest_player.hit = True
						blackjack.process_turn()
						display_cards(irc, bot_channel, blackjack)

				if message.suffix.startswith("!stay") and blackjack != None:
					if message.sender == blackjack.guest_player.name:
						blackjack.guest_player.hit = False
						while True:
							blackjack.process_turn()
							if blackjack.winner != None or blackjack.stalemate == True:
								break
						display_cards(irc, bot_channel, blackjack)

				if message.suffix.startswith("!dd") and blackjack != None:
					if message.sender == blackjack.guest_player.name:
						dd = True
						blackjack.guest_player.hit = True
						wager *= 2
						blackjack.process_turn()
						display_cards(irc, bot_channel, blackjack)

				if message.suffix.startswith("!stats"):
					parameter = message.get_parameter("!stats")
					if parameter == "":
						username = message.sender
					else:
						username = parameter
					show_user_stats(irc, bot_channel, user_tracker, username)
			
				if blackjack != None and (blackjack.winner != None or blackjack.stalemate is True):
					track_wins(blackjack, user_tracker)
					adjust_wallets(blackjack, user_tracker, wager)
					track_highscores(blackjack, user_tracker)
					announce_winner(irc, bot_channel, blackjack, wager)
					with open("savefile", "w+") as savefile:
						user_tracker.save_state(savefile)				
					blackjack = None
					timer = 0

				if message.suffix.startswith("!topic"):
					topic = message.get_parameter("!topic")		
					top_scores = user_tracker.get_topscores()
					for user in top_scores:
						if user.name == "Dealer":
							top_scores.remove(user)			
					if message.sender == top_scores[0].name or message.sender == "DICK":
						irc.topic(message.channel, str(topic))

				if message.suffix.startswith("!highscores"):
					if not (time.time() - antiflood_timer > antiflood_cooldown):
						irc.send_message(message.channel, "Antiflood cooldown is in effect")
						continue
					for user in user_tracker.get_highscores():
						if user.name != "Dealer" and user.highscore > 1000:
							irc.send_message(message.channel, user.name + " " + str(user.highscore))
							time.sleep(delay)
					antiflood_timer = time.time()

				if message.suffix.startswith("!topwins"):
					if not (time.time() - antiflood_timer > antiflood_cooldown):
						irc.send_message(message.channel, "Antiflood cooldown is in effect")
						continue
					for user in user_tracker.get_topwins():
						if user.name != "Dealer" and user.games_won > 0:
							irc.send_message(message.channel, user.name + " " + str(user.games_won))
							time.sleep(delay)
					antiflood_timer = time.time()

				if message.suffix.startswith("!toplosses"):
					if not (time.time() - antiflood_timer > antiflood_cooldown):
						irc.send_message(message.channel, "Antiflood cooldown is in effect")
						continue
					for user in user_tracker.get_toplosses():
						if user.name != "Dealer" and user.games_lost > 0:
							irc.send_message(message.channel, user.name + " " + str(user.games_lost))
							time.sleep(delay)
					antiflood_timer = time.time()


				if message.suffix.startswith("!topties"):
					if not (time.time() - antiflood_timer > antiflood_cooldown):
						irc.send_message(message.channel, "Antiflood cooldown is in effect")
						continue
					for user in user_tracker.get_topties():
						if user.name != "Dealer" and user.games_tied > 0:
							irc.send_message(message.channel, user.name + " " + str(user.games_tied))
							time.sleep(delay)
					antiflood_timer = time.time()


				if message.suffix.startswith("!topscores"):
					if not (time.time() - antiflood_timer > antiflood_cooldown):
						irc.send_message(message.channel, "Antiflood cooldown is in effect")
						continue
					for user in user_tracker.get_topscores():
						if user.name != "Dealer" and user.wallet > 1000:
							irc.send_message(message.channel, user.name + " " + str(user.wallet))
							time.sleep(delay)
					antiflood_timer = time.time()


				if message.suffix.startswith("!lowestscores"):
					if not (time.time() - antiflood_timer > antiflood_cooldown):
						irc.send_message(message.channel, "Antiflood cooldown is in effect")
						continue
					for user in user_tracker.get_lowest_scores():
						if user.name != "Dealer" and user.wallet < 0:
							irc.send_message(message.channel, user.name + " " + str(user.wallet))
							time.sleep(delay)
					antiflood_timer = time.time()


				if message.suffix.startswith("!transfer"):
					parameters = message.get_parameter("!transfer").split()
					user1 = message.sender
					try:
						user2 = parameters[0]
						value = parameters[1]
					except:
						irc.send_message(message.channel, "Usage: !transfer <user> <amount>")
						continue
					if not user_tracker.is_in_userlist(user1):
						icr.send_message(message.channel, "No such user")
						continue
					if not user_tracker.is_in_userlist(user2):
						irc.send_message(message.channel, "No such user")
						continue
					if user1 == "Dealer":
						irc.send_message(message.channel, "Nice try")
						continue
					user1 = user_tracker.get_user_stats(user1)
					user2 = user_tracker.get_user_stats(user2)
					try:
						value = int(value)
					except:
						irc.send_message(message.channel, "Invalid parameter")
						continue
					if value > user1.wallet:
						irc.send_message(message.channel, "You can't transfer that much")
						continue
					if value < 1:
						irc.send_message(message.channel, "Invalid parameter")
						continue
					user1.wallet -= value
					user2.wallet += value
					irc.send_message(message.channel, "Transferred +" + str(value) + " to " + user2.name + "'s wallet")
					with open("savefile", "w+") as savefile:
						user_tracker.save_state(savefile)

				if message.suffix.startswith("!source"):
					if not (time.time() - antiflood_timer > antiflood_cooldown):
						irc.send_message(message.channel, "Antiflood cooldown is in effect")
						continue
					irc.send_message(message.channel, "https://github.com/q1mCjdoG/blackjack")
					antiflood_timer = time.time()
				
					

				if message.suffix.startswith("!help"):
					if not (time.time() - antiflood_timer > antiflood_cooldown):
						irc.send_message(message.channel, "Antiflood cooldown is in effect")
						continue
		
					command_list = ["Start the game. Wager defaults to 0:  !play <wager>",
								"Receive another card from the dealer:  !hit",
								"Keep your cards as they are until the game is over: !stay",
								"Receive another card from the dealer and double the wager: !dd",
								"Show stats such as wins and losses. Nick defaults to your nick: !stats <nick>",
								"Set topic to anything you want. Only works for the player with the highest score: !topic <topic>",
								"Show leaderboard sorted by games won: !topwins",
								"Show leaderboard sorted by games lost: !toplosses",
								"Show leaderboard sorted by games tied: !topties",
								"Show leaderboard sorted by score: !topscores",
								"Show leaderboard sorted by highest scores recorded: !highscores",
								"Stores your feedback for the creator to see: !feedback <msg>",
								"Link to the full source of the bot: !source"]

					for command in command_list:
						irc.send_message(message.channel, command)
						time.sleep(delay)

					antiflood_timer = time.time()

				if message.suffix.startswith("!feedback"):
					with open("feedback", "a") as feedback:
						feedback.write("\n")
						feedback.write(message.sender + ": " + message.get_parameter("!feedback"))
						feedback.write("\n")

			if "MOTD" in message.suffix:
				irc.send_message("nickserv", "identify " + password)
				irc.join_channel(bot_channel)

			if message.type == "PING":
				irc.pong(message.server)

			delta_time = time.time() - timer
			if blackjack != None and delta_time > 120:
				irc.send_message(bot_channel, "Took too long to respond. Resetting")
				irc.send_message(bot_channel,  blackjack.guest_player.name + " will receive a 5 minute cooldown")	
				banned_user = ban.BannedUser(blackjack.guest_player.name, bot_channel, 5*60)
				bantracker.banlist.append(banned_user)		
				blackjack = None
				timer = 0

			bantracker.update_banlist()
			del bantracker.unban_queue[:]
				

	time.sleep(60)

