import socket
import ssl

class Message:
	
	def __init__(self, raw_message):
		self.raw_message = raw_message
		self.type = None

	@property
	def prefix(self):
		end = self.raw_message[1:].find(":")
		prefix = self.raw_message[:end]
		return prefix

	@property
	def suffix(self):
		start = self.raw_message[1:].find(":") + 2
		suffix = self.raw_message[start:]
		return suffix

class PING(Message):

	def __init__(self, raw_message):
		self.raw_message = raw_message
		self.type = "PING"

	@property
	def server(self):
		server = self.raw_message[6:]
		return server

class NAMES(Message):

	def __init__(self, raw_message):
		self.raw_message = raw_message
		self.type = "NAMES"

	@property
	def nicks(self):
		start = self.raw_message[1:].find(":") + 2
		nicks = self.raw_message[start:].split()
		return nicks

class PRIVMSG(Message):
	
	def __init__(self, raw_message):
		self.raw_message = raw_message
		self.type = "PRIVMSG"

	@property	
	def sender(self):
		end = self.raw_message.find("!")
		sender = self.raw_message[1:end]
		return sender

	@property
	def channel(self):
		start = self.raw_message.find("PRIVMSG") + len("PRIVMSG") + 1
		end = self.raw_message[1:].find(":")
		channel =  self.raw_message[start:end]
		if channel.startswith("#"):
			return channel
		else:
			return self.sender

	def get_parameter(self, ignored_string):
		return self.suffix[len(ignored_string)+1:]

def handle_message(raw_message):
	generic_message = Message(raw_message)
	prefix = generic_message.prefix

	if prefix.startswith("PING"):
		return PING(raw_message)

	if "PRIVMSG" in prefix:
		return PRIVMSG(raw_message)

	if "353" in prefix:
		return NAMES(raw_message)

	if "366" in prefix:
		generic_message.type = "end of NAMES list"
		return generic_message

	if "376" in prefix:
		generic_message.type = "end of MOTD command"
		return generic_message

	return generic_message

class Irc:

	def __init__(self):
		self.socket = socket.socket()
		self.message_queue = []

	def connect(self, host, port, ssl_enabled):
		if ssl_enabled:
			context = ssl.create_default_context()
			self.socket = context.wrap_socket(self.socket, server_hostname=host)
		self.socket.connect((host, port))

	def update_message_queue(self):
		del self.message_queue[:]		
		buff = ""
		while True:
			buff += self.socket.recv(1024).decode("UTF-8")
			if buff == "":
				return
			if buff[-2:] == "\r\n":
				break
			else:
				continue
		raw_messages = buff.split("\r\n")
		for raw_message in raw_messages:
			self.message_queue.append(handle_message(raw_message))

	def nick(self, nick):
		self.socket.send(bytes("NICK " + nick + "\r\n", "UTF-8"))
		
	def user(self, user):
		self.socket.send(bytes("USER " + user + " " + user + " " + user + " :" + user + "\r\n", 'UTF-8'))
	
	def pong(self, server):
		self.socket.send(bytes("PONG " + " :" + server + "\r\n", "UTF-8"))

	def join_channel(self, channel):
		self.socket.send(bytes("JOIN " + channel + "\r\n", "UTF-8"))

	def send_message(self, channel, message):
		self.socket.send(bytes("PRIVMSG " + channel + " :" + message + "\r\n", "UTF-8"))

	def kick(self, channel, user, kick_message=None):
		if kick_message:
			self.socket.send(bytes("KICK " + channel + " " + user + " :" + kick_message + "\r\n", "UTF-8"))
		else:
			self.socket.send(bytes("KICK " + channel + " " + user + "\r\n", "UTF-8"))

	def names(self, channel):
		self.socket.send(bytes("NAMES " + channel + "\r\n", "UTF-8"))

	def topic(self, channel, topic):	
		self.socket.send(bytes("TOPIC " + channel + " :" + topic + "\r\n", "UTF-8"))


