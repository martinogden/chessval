import sys
from board import Board


board = Board()
def perft(depth=3):
    if depth == 0:
        return 1

    nodes = 0
    moves = board.move_list()
    for frm, to, cpiece, flags in moves:
        board.makemove(frm, to)
        nodes += perft(depth - 1)
        board.unmakemove()
    return nodes


ply = int(sys.argv[1])
print perft(ply)
