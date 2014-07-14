import sys
from constants import *

DEBUG = False

class TreeNode(object):

	def __init__(self, value, parent=None):
		self.value = value
		self.children = []

	def __repr__(self, level=0):
		val = "%s%s\n" % ("> " * level, self.value)
		for child in self.children:
			val += child.__repr__(level+1)
		return val

	def add_child(self, value):
		node = TreeNode(value, parent=self)
		self.children.append(node)
		return node


def evaluate(board):
	M = board.material
	sign = 1 if board.player == WHITE else -1

	material_score = sum([
		(M[WHITE_QUEEN] - M[WHITE_QUEEN | 8]) * 9,
		(M[WHITE_ROOK] - M[WHITE_ROOK | 8]) * 5,
		(M[WHITE_BISHOP] - M[WHITE_BISHOP | 8]) * 3,
		(M[WHITE_KNIGHT] - M[WHITE_KNIGHT | 8]) * 3,
		(M[WHITE_PAWN] - M[WHITE_PAWN | 8]) * 1,
	])

	return sign * material_score


def negamax(board, depth):

	def inner(alpha, beta, depth, parent):
		if depth == 0:
			return evaluate(board)

		for move in board.move_list():
			frm, to, cpiece, _, _, promo = move
			board.makemove(frm, to, promotion=promo)
			child = parent.add_child(None)
			score = -inner(-beta, -alpha, depth - 1, child)
			child.value = score
			board.unmakemove()

			if score >= beta:
				return beta
			if score > alpha:
				alpha = score
		return alpha

	root = TreeNode(None)
	score = inner(float("-inf"), float("inf"), depth, root)
	root.value = score
	if DEBUG:
		print root
	sys.stdout.write(".")
	sys.stdout.flush()
	return score


class AI(object):

	SEARCH_DEPTH = 4

	def __init__(self, board):
		self.board = board

	def best_move(self):
		move_list = self.board.move_list()

		max_ = float("-inf")
		best_move = None
		for move in self.board.move_list():
			frm, to, _, _, _, promo = move

			self.board.makemove(frm, to, promotion=promo)
			score = negamax(self.board, self.SEARCH_DEPTH)
			self.board.unmakemove()

			if score > max_:
				best_move = move
				max_ = score

		return best_move
