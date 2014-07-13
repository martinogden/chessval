#!/usr/bin/env python

import re

from board import Board, KingInCheck, InvalidMove
from serialization import to_bit


LAN_PATT = r"([a-g]{1}[1-8]{1})-([a-g]{1}[1-8]{1})([nbrq]{1})?"


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
		try:
			self.board.makemove(to_bit(frm), to_bit(to), promotion=promotion)
		except (KingInCheck, InvalidMove) as e:
			return e
		else:
			return "OK"

	def side_to_move(self):
		return ["W", "B"][self.board.player]
