class Player(object):
    """ Subclass this """

    def __init__(self, board):
        self.board = board

    def play(self):
        raise NotImplementedError()
