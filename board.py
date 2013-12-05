#!/usr/bin/env python

from constants import *
import inout as io
import bitboards as bb


class InvalidMove(ValueError):
    pass


class Board(object):

    player = WHITE
    ep = None
    castling = 0x00

    full_moves = 1
    half_moves = 0

    # [00-13] list of bitboards foreach piece type
    # [14-16] aggregated bitboards: w / b / all
    positions = [0x0L] * 17
    occupancy = [-1] * 64

    def __init__(self, fen=None):
        super(Board, self).__init__()
        self.reset()

    def __unicode__(self):
        return io.unicode(self)

    def reset(self, fen=INITIAL_FEN):
        self.player = WHITE
        self.en_passant = None
        self.castling = 0x00
        self.half_moves = 0
        self.full_moves = 1
        self.positions = [0x0L] * 17
        self.occupancy = [-1] * 64
        io.from_fen(self, fen or INITIAL_FEN)

    def is_legal(self, frm, to, promotion=None):
        """ Check if move frm sq `frm` to square `to` is legal
            :todo: add check detection
            :todo: add castling moves
            :todo: add promotion moves
        """

        offset = 14

        occ = self.positions[offset + ALL]
        friendly = self.positions[offset + self.player]
        piece = self.occupancy[frm]

        if piece == -1:
            raise InvalidMove("No piece to move")

        # pawns are a special case
        if piece % 8 == WHITE_PAWN:
            sp_map = (bb.wP_spushes, bb.bP_spushes)
            dp_map = (bb.wP_dpushes, bb.bP_dpushes)
            pa_map = (bb.wP_attacks, bb.bP_attacks)

            delta = to - frm
            my_pawns = self.positions[piece]
            empty = occ ^ bb.masks.FULL

            # if frm and to are congruent modulo 16, this is a dbl pawn push.
            if delta % 16 == 0:  # double push
                p_pawns = dp_map[self.player](my_pawns, empty)

                if p_pawns & (1<<frm) == 0L:
                    raise InvalidMove("Pawn not able to push")

            # or if cong. mod. 8 it is a single push
            elif delta % 8 == 0:  # single push
                p_pawns = sp_map[self.player](my_pawns, empty)

                if p_pawns & (1<<frm) == 0L:
                    raise ValueError("Pawn not able to push")
            else:                
                # check for pawn attacks
                enemy = self.positions[offset + (self.player ^ 1)]

                # treat en passant square as an enemy piece
                if self.ep:
                    enemy |= (1<<self.ep)

                targets = pa_map[self.player](enemy, frm)

                if targets & (1<<to) == 0L:
                    raise ValueError("Pawn unable to attack")

            # TODO en passant and promotion moves
        else:
            # all other pieces can be dealt with generically
            a_map = (
                None, bb.K_attacks, bb.N_attacks,
                bb.B_attacks, bb.R_attacks, bb.Q_attacks
            )
            attacks = a_map[piece % 8](occ, frm)
            targets = attacks & (bb.masks.FULL ^ friendly)
            if targets & (1<<to) == 0L:
                raise ValueError("Invalid slider target sq")
            # TODO castling moves


    def makemove(self, frm, to, promotion=None):
        """ Make a (legal) move 
            :todo: add castling moves
            :todo: add promotion moves
        """
        # this will throw if move not valid
        self.is_legal(frm, to, promotion=promotion)

        piece = self.occupancy[frm]
        frm_sq = 1 << frm
        to_sq = 1 << to

        ### pickup pieces
        self.occupancy[frm] = -1
        not_frm_sq = bb.masks.FULL ^ frm_sq
        self.positions[piece] &= not_frm_sq
        self.positions[offset + self.player] &= not_frm_sq
        self.positions[offset + ALL] &= not_frm_sq

        # handle capture
        cpiece = self.occupancy[to]
        if cpiece > -1:
            self.positions[cpiece] &= bb.masks.FULL ^ to_sq


        ### drop pieces
        self.occupancy[to] = piece
        self.positions[piece] |= to_sq
        self.positions[offset + self.player] |= to_sq
        self.positions[offset + ALL] |= to_sq

        ### store pieces TODO
        ### retreive pieces TODO

        ### update game status
        self.half_moves += 1
        self.full_moves + self.half_moves % 2
        self.player ^= 1

        # set or reset en passant square
        if piece % 16 == WHITE_PAWN:
            # if frm and to are congruent modulo 16, this is a dbl pawn push.
            delta = to - frm
            if delta % 16 == 0:
                self.ep = frm + (delta/2)
        else:
            self.ep = None


if __name__ == "__main__":
    from sys import stdout
    b = Board()

    while(True):
        stdout.write(unicode(b))
        player = ["W", "B"][b.player]
        mv = raw_input("%s to move: \033[K" % player)
        try:
            frm = io.to_bit(mv[:2])
            to = io.to_bit(mv[2:5])
            b.makemove(frm, to)
        except Exception, e:
            stdout.write("\033[F" * 10)
            stdout.write(" " * 20)
            stdout.write(str(e) + "\n" + "\033[K")
            stdout.write("\033[F")
        else:
            stdout.write("\033[F" * 10)
