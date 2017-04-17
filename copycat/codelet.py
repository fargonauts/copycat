class Codelet(object):
    def __init__(self, name, urgency, timestamp):
        self.name = name
        self.urgency = urgency
        self.arguments = []
        self.timeStamp = timestamp

    def __repr__(self):
        return '<Codelet: %s>' % self.name
