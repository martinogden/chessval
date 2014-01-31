from .player import *

class AI(Player):

	def play(self):
		for i in xrange(64):
			for j in xrange(64):
				try:
					self.board.is_valid(i, j)
				except:
					continue
				else:
					self.board.makemove(i, j)
					return
