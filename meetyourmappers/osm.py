import osmium

class UserHandler(osmium.SimpleHandler):
	def __init__(self):
		osmium.SimpleHandler.__init__(self)
		self.users = {}
		self.totals = {'n': 0, 'w': 0, 'r': 0}

	def node(self, o):
		self.totals['n'] += 1
		if o.user in self.users.keys():
			u = self.users[o.user]
			u['n'] += 1
			u['l'] = max(o.timestamp, u['l'])
			u['f'] = min(o.timestamp, u['f'])
		else:
			self.users[o.user] = {'n': 1, 'w': 0, 'r': 0, 'f': o.timestamp, 'l': o.timestamp}

	def way(self, o):
		self.totals['w'] += 1
		if o.user in self.users.keys():
			u = self.users[o.user]
			u['w'] += 1
			u['l'] = max(o.timestamp, u['l'])
			u['f'] = min(o.timestamp, u['f'])
		else:
			self.users[o.user] = {'n': 1, 'w': 0, 'r': 0, 'f': o.timestamp, 'l': o.timestamp}

	def relation(self, o):
		self.totals['r'] += 1
		if o.user in self.users.keys():
			u = self.users[o.user]
			u['r'] += 1
			u['l'] = max(o.timestamp, u['l'])
			u['f'] = min(o.timestamp, u['f'])
		else:
			self.users[o.user] = {'n': 1, 'w': 0, 'r': 0, 'f': o.timestamp, 'l': o.timestamp}
