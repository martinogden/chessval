import sys
from board import Board
from inout import san


board = Board()
def perft(depth=3):
    if depth == 0:
        return 1

    moves = board.move_list()
    if depth == 1:
        return len(list(moves))

    nodes = 0
    for frm, to, cpiece, flags in moves:
        board.makemove(frm, to)
        nodes += perft(depth - 1)
        board.unmakemove()
    return nodes


def divide(depth=3):
    nodes = 0
    moves = list(board.move_list())
    for frm, to, cpiece, flags in moves:
        board.makemove(frm, to)
        result = perft(depth - 1)
        nodes += result
        board.unmakemove()
        print "%s%s: %i" % (san(frm), san(to), result)

    print "\n============"
    print "Moves: %i" % len(moves)
    print "Nodes: %i" % nodes


depth = int(sys.argv[1])
divide(depth)
