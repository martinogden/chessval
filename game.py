#!/usr/bin/env python

from board import Board
from players import XBoard, AI


if __name__ == "__main__":
	board = Board()
	p1 = XBoard(board)
	p2 = AI(board)
	players = [p1, p2]
	while True:
		players[board.player].play()
