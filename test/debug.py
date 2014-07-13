from serialization import san, to_bit


class Debugger(object):

    def __init__(self, board, quiet=False):
        self.board = board
        self.quiet = quiet

    def perft(self, depth=3):
        if depth == 0:
            return 1

        moves = self.board.move_list()
        if depth == 1:
            return len(list(moves))

        nodes = 0
        for frm, to, cpiece, flags, cr, promotion in moves:
            self.board.makemove(frm, to, promotion=promotion)
            nodes += self.perft(depth - 1)
            self.board.unmakemove()
        return nodes

    def divide(self, depth=3):
        nodes = 0
        moves = list(self.board.move_list())
        for frm, to, cpiece, flags, cr, promotion in moves:
            self.board.makemove(frm, to, promotion=promotion)
            result = self.perft(depth - 1)
            nodes += result
            self.board.unmakemove()
            if not self.quiet:
                p = promotion and "--nbrq"[promotion % 8] or ""
                print "%s%s%s: %i" % (san(frm), san(to), p, result)

        if not self.quiet:
            print "\n============"
            print "Moves: %i" % len(moves)
            print "Nodes: %i" % nodes
        return nodes
