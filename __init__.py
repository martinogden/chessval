#!/usr/bin/env python

import re

from board import Board, KingInCheck, InvalidMove
from serialization import to_bit
from ai import AI


LAN_PATT = r"([a-h]{1}[1-8]{1})-([a-h]{1}[1-8]{1})([nbrq]{1})?"


class Chess(object):

	board = Board()

	def __unicode__(self):
		return self.board.__unicode__()

	def __repr__(self):
		return self.board.__repr__()

	def reset(self):
		self.board.reset()

	def load(self, fen):
		self.board.reset(fen)

	def makemove(self, lan):
		""" :param lan: (LAN) form of move e.g.: a2a3 """
		frm, to, promotion = re.match(LAN_PATT, lan.lower()).groups()
		promotion = "nbrq"[promotion] if promotion else None
		try:
			self.board.makemove(to_bit(frm), to_bit(to), promotion=promotion)
		except (KingInCheck, InvalidMove) as e:
			print e
		else:
			print unicode(self.board)
			print "OK. Thinking",
			self.think()
			print
			print unicode(self.board)
			print "White to Move."

	def side_to_move(self):
		return ["W", "B"][self.board.player]

	def think(self):
		ai = AI(self.board)
		frm, to, _, _, _, promo = ai.best_move()
		self.board.makemove(frm, to, promotion=promo)


c=Chess()
