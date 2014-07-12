import operator
from bitboards.twiddling import *
from constants import *


EMPTY = "-"
PIECES = "PKNBRQ--pknbrq"
UPIECES = (u'\u2659\u2654\u2658\u2657\u2656\u2655-'
           u'-\u265F\u265A\u265E\u265D\u265C\u265B')
OFFSET = len(PIECES)


def to_bit(san):
    f, r = san
    return ((int(r) - 1) * 8) + ord(f.lower()) - 97

    
def san(sq):
    return "abcdefgh"[sq&7] + "12345678"[sq>>3]


class Serializer(object):

    def __init__(self, fen=INITIAL_FEN):
        self.setboard(fen)

    def __unicode__(self):
        """ Human friendly board output """

        b = [[str(8-i)] + [""] * 8 for i in xrange(8)]

        for i in xrange(64):
            f = i & 7
            r = 7 - (i>>3)

            occ = self.occupancy[i]
            if occ == -1:
                b[r][f] = [u'\u00B7', u'x'][(i+r) % 2]
            else:
                b[r][f] = UPIECES[occ]

        return u'\n'.join([' '.join(r) for r in b])

    def __repr__(self):
        """ Output the board state in Forsyth-Edwards Notation """

        gap = 0
        ranks = [""] * 8
        rank = 7
        for i, occ in enumerate(self.occupancy):
            if i and i % 8 == 0:                    # new rank
                if gap > 0:
                    ranks[rank] += str(gap)         #   output gap
                rank -= 1                           #   move to next rank
                gap = 0                             #   reset gap

            if occ == -1:                           # increment gap
                gap += 1
            else:                                   # we have a piece
                if gap > 0:
                    ranks[rank] += str(gap)         #   output gap
                    gap = 0                         #   reset gap
                ranks[rank] += PIECES[occ]          # output piece
        if gap > 0:
            ranks[rank] += str(gap)

        c = self.castling
        castling = "".join(["KQkq"[i] for i in xrange(4) if c & (1<<i)])
        output = (
            "/".join(ranks),                        # placement
            "wb"[self.player],                      # color
            castling or EMPTY,                      # castling
            self.ep and san(self.ep) or EMPTY,     # en passant
            str(self.half_moves),                   # half moves
            str(self.full_moves),                   # full moves
        )
        return " ".join(output)

    def u(self):
        print unicode(self)

    def setboard(self, fen):
        """ Load a game from a fen representation """
        p = self.positions
        position, player, castling, ep, hm, fm = fen.split(' ')
        ranks = reversed(position.split('/'))

        bit = 0
        for rank in ranks:
            for sq in rank:
                if sq.isdigit():
                    bit += int(sq)
                else:
                    piece = PIECES.index(sq)
                    cbb = OFFSET + (piece>>3)
                    self.occupancy[bit] = piece
                    self.positions[piece] |= 1<<bit
                    self.positions[cbb] |= 1<<bit
                    self.positions[-1] |= 1<<bit
                    if piece % 8 == WHITE_KING:
                        self.king[piece>>3] = bit
                    bit += 1

        self.castling = 0
        if castling != EMPTY:
            for c in castling:
                self.castling |= (1<<"KQkq".index(c))

        self.player = "wb".index(player)
        self.ep = ep != EMPTY and to_bit(ep) or None
        self.half_moves = int(hm)
        self.full_moves = int(fm)
