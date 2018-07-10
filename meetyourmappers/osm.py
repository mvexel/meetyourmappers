import osmium
from datetime import datetime, timezone


class UserHandler(osmium.SimpleHandler):
    def __init__(self):
        osmium.SimpleHandler.__init__(self)
        self.users = {}
        self.totals = {
            'n': 0,
            'w': 0,
            'r': 0,
            'f': datetime.now(timezone.utc),
            'l': datetime.now(timezone.utc)}

    def node(self, o):
        self.totals['n'] += 1
        self.totals['f'] = min(o.timestamp, self.totals['f'])
        self.totals['l'] = max(o.timestamp, self.totals['l'])
        if o.user in self.users.keys():
            u = self.users[o.user]
            u['n'] += 1
            u['l'] = max(o.timestamp, u['l'])
            u['f'] = min(o.timestamp, u['f'])
        else:
            self.users[o.user] = {
                'n': 1,
                'w': 0,
                'r': 0,
                'f': o.timestamp,
                'l': o.timestamp}

    def way(self, o):
        self.totals['w'] += 1
        self.totals['f'] = min(o.timestamp, self.totals['f'])
        self.totals['l'] = max(o.timestamp, self.totals['l'])
        if o.user in self.users.keys():
            u = self.users[o.user]
            u['w'] += 1
            u['l'] = max(o.timestamp, u['l'])
            u['f'] = min(o.timestamp, u['f'])
        else:
            self.users[o.user] = {
                'n': 1,
                'w': 0,
                'r': 0,
                'f': o.timestamp,
                'l': o.timestamp}

    def relation(self, o):
        self.totals['r'] += 1
        self.totals['f'] = min(o.timestamp, self.totals['f'])
        self.totals['l'] = max(o.timestamp, self.totals['l'])
        if o.user in self.users.keys():
            u = self.users[o.user]
            u['r'] += 1
            u['l'] = max(o.timestamp, u['l'])
            u['f'] = min(o.timestamp, u['f'])
        else:
            self.users[o.user] = {
                'n': 1,
                'w': 0,
                'r': 0,
                'f': o.timestamp,
                'l': o.timestamp}


if __name__ == '__main__':
    import sys
    args = sys.argv
    if len(args) != 2:
        print("please supply a filename")
        sys.exit(1)
    u = UserHandler()
    u.apply_file(args[1])
    print(u.users)
    print(u.totals)