import logging

from constants import *
from serialization import Serializer
import bitboards as bb
import move

logging.basicConfig(**{
    'format': "[%(levelname)s] %(message)s",
    'filename': "xboard.log",
    'filemode': 'w',
    'level': logging.CRITICAL,
})


OFFSET = 14
MAX_MOVES = 100


class InvalidMove(ValueError):
    pass


class KingInCheck(ValueError):
    pass


class Board(Serializer):

    player = WHITE
    ep = None  # en passant square
    castling = 0x00  # castling rights

    full_moves = 1
    half_moves = 0

    # [00-13] list of bitboards foreach piece type
    # [14-16] aggregated bitboards: w / b / all
    positions = [0x0L] * 17
    occupancy = [-1] * 64
    moves = []
    king = [-1, -1]

    def piece_bb(self, piece):
        return self.positions[piece]

    def piece_at(self, i):
        return self.occupancy[i]

    def pickup(self, piece, at):
        # pickup the pieces (Average White Band style)
        player = (piece & 8) >> 3
        mask = bb.masks.FULL ^ (1<<at)

        self.occupancy[at] = -1
        self.positions[piece] &= mask
        self.positions[OFFSET + player] &= mask
        self.positions[-1] &= mask

    def drop(self, piece, at):
        ### drop pieces
        player = (piece & 8) >> 3
        sq = 1 << at

        self.occupancy[at] = piece
        self.positions[piece] |= sq
        self.positions[OFFSET + player] |= sq
        self.positions[-1] |= sq

    def reset(self, fen=INITIAL_FEN):
        self.positions = [0x0L] * 17
        self.occupancy = [-1] * 64
        self.setboard(fen)

    def is_legal(self, frm, to, promotion=None):
        """ Check if move frm sq `frm` to square `to` is legal
            :todo: add check detection
            :todo: add castling moves
            :todo: add promotion moves
        """
        try:
            self.makemove(frm, to, promotion)
        except KingInCheck:
            return False
        else:
            self.unmakemove()
            return True

    def is_attacked(self, sq, by):
        pos = self.positions
        occ = pos[-1]
        by_offset = by<<3

        P = pos[WHITE_PAWN | by_offset]
        if bb.P_attacks[by^1](P, sq): logging.debug("check P"); return True
        N = pos[WHITE_KNIGHT | by_offset]
        if bb.N_attacks(occ, sq) & N: logging.debug("check N"); return True
        K = pos[WHITE_KING | by_offset]
        if bb.K_attacks(occ, sq) & K: logging.debug("check K"); return True
        B = pos[WHITE_BISHOP | by_offset] | pos[WHITE_QUEEN | by_offset]
        if bb.B_attacks(occ, sq) & B: logging.debug("check B"); return True
        R = pos[WHITE_ROOK | by_offset] | pos[WHITE_QUEEN | by_offset]
        if bb.R_attacks(occ, sq) & R: logging.debug("check R"); return True

        return False

    def makemove(self, frm, to, promotion=None):
        """ Make a (legal) move 
            :todo: add castling moves
            :todo: add promotion moves
        """

        occ = self.positions[-1]
        friendly = self.positions[OFFSET + self.player]
        piece = self.occupancy[frm]

        if piece == -1:
            raise InvalidMove("No piece to move")

        # pawns are a special case
        if piece % 8 == WHITE_PAWN:
            delta = to - frm
            my_pawns = self.positions[piece]
            empty = occ ^ bb.masks.FULL

            # if delta is congruent modulo. 8, this is pawn push
            if delta and delta % 8 == 0:  
                if delta % 16 == 0:  # double push
                    p_pawns = bb.P_dpushes[self.player](my_pawns, empty)
                else:  # single push
                    p_pawns = bb.P_spushes[self.player](my_pawns, empty)

                if p_pawns & (1<<frm) == 0L:
                    raise InvalidMove("Pawn not able to push")

                if (delta < 0 and self.player == WHITE) or\
                        (delta > 0 and self.player == BLACK):
                    raise InvalidMove("Pawns cannot push backwards")

            else:  # check for pawn attacks
                enemy = self.positions[OFFSET + (self.player ^ 1)]

                # treat en passant square as an enemy piece
                if self.ep:
                    enemy |= (1<<self.ep)

                targets = bb.P_attacks[self.player](enemy, frm)

                if targets & (1<<to) == 0L:
                    raise InvalidMove("Pawn unable to attack")

        else:
            # check for castling
            d = frm - to
            if piece % 8 == WHITE_KING and not (d % 2 and d % 3):
                if self.castling & (1<<self.player*2) and not d % 2:
                    pass  # king side castle
                elif self.castling & (2<<self.player*2) and not d % 3:
                    pass  # queen side castle
                else:
                    raise InvalidMove("Castling not allowed")

            else:
                # all other pieces can be dealt with generically
                attacks = bb.attacks[piece % 8](occ, frm)
                targets = attacks & (bb.masks.FULL ^ friendly)
                if targets & (1<<to) == 0L:
                    raise InvalidMove("Invalid slider target sq")


        #################
        ##### Make move #
        piece = self.occupancy[frm]
        cpiece = self.occupancy[to]
        flags = 0

        self.pickup(piece, frm)

        # handle capture
        if cpiece > -1:
            mask = bb.masks.FULL ^ (1 << to)
            self.positions[cpiece] &= mask
            self.positions[OFFSET + (self.player^1)] &= mask
            flags |= move.flags.CAPTURE

        elif to == self.ep and piece % 8 == WHITE_PAWN:  # handle en passant capture
            oppnt = self.player^1
            oppnt_pawn = to - 8 + self.player*16
            cpiece = WHITE_PAWN | oppnt<<3
            self.pickup(cpiece, oppnt_pawn)

            flags |= move.flags.EP | move.flags.CAPTURE

        self.drop(piece, to)

        # update king position (for check detection)
        if piece % 8 == WHITE_KING:
            self.king[self.player] = to

        ### store pieces TODO
        ### retrieve pieces TODO

        ### update game status
        if cpiece > -1 or piece % 8 == WHITE_PAWN:
            self.half_moves = 0
        else:
            self.half_moves += 1

        self.full_moves += self.player  # update on black
        self.player ^= 1

        # set or reset en passant square
        self.ep = None
        if piece % 8 == WHITE_PAWN:
            # if frm and to are congruent modulo 16, this is a dbl pawn push.
            delta = to - frm
            if delta % 16 == 0:
                self.ep = frm + (delta/2)
                flags |= move.flags.DPUSH

        self.moves.append(move.new(frm, to, cpiece, flags))
        if self.is_attacked(self.king[self.player^1], self.player):
            self.unmakemove()
            raise KingInCheck()

    def unmakemove(self):
        mv = self.moves.pop()
        logging.debug("unmakemove: %s", mv)
        frm, to, cpiece, flags = mv

        piece = self.occupancy[to]
        frm_sq = 1 << frm
        to_sq = 1 << to

        ### pickup pieces
        self.pickup(piece, to)

        ### drop pieces
        self.drop(piece, frm)

        # update king position (for check detection)
        if piece % 8 == WHITE_KING:
            self.king[self.player ^ 1] = frm


        if flags & move.flags.EP:  # revert en passant capture
            oppnt_pawn = to - 8 + (self.player^1) * 16
            self.drop(cpiece, oppnt_pawn)
        elif flags & move.flags.CAPTURE:  # revert capture
            self.drop(cpiece, to)

        ### store pieces TODO
        ### retrieve pieces TODO
        ### update game status
        # TODO how do we restore the half move counter?

        self.ep = None
        # restore ep square
        if self.moves:
            pfrm, pto, pcpiece, pflags = self.moves[-1]
            if pflags & move.flags.DPUSH:
                self.ep = pfrm + (pto - pfrm) / 2

        self.player ^= 1
        self.full_moves += self.player  # update on black

    def move_list(self):
        moves = []

        occ = self.positions[OFFSET + ALL]
        empty = ~occ & bb.masks.FULL

        friendly = self.positions[OFFSET + self.player]
        nfriendly = ~friendly & bb.masks.FULL
        enemy = self.positions[OFFSET + self.player ^ 1]
        if self.ep:  # treat en passant square as an enemy piece
            enemy |= (1<<self.ep)


        # TODO broad phase pawn attack detection
        pawns = self.positions[WHITE_PAWN | self.player << 3]

        spushes = bb.P_spushes[self.player](pawns, empty)
        dpushes = bb.P_dpushes[self.player](pawns, empty)

        for frm in bb.get_set_bits(pawns):

            attacks = bb.P_attacks[self.player](enemy, frm)
            for to in bb.get_set_bits(attacks):
                moves.append(move.new(frm, to))

            if 1 << frm & spushes:
                to = frm + 8 - self.player*16
                moves.append(move.new(frm, to))

            if 1 << frm & dpushes:
                to = frm + 16 - self.player*32
                moves.append(move.new(frm, to))


        for piece in [WHITE_KING, WHITE_KNIGHT, WHITE_BISHOP, WHITE_ROOK, WHITE_QUEEN]:
            piece_bb = self.positions[piece | self.player << 3]
            for frm in bb.get_set_bits(piece_bb):
                attacks = bb.pieces.attacks[piece](occ, frm) & nfriendly
                for to in bb.get_set_bits(attacks):
                    moves.append(move.new(frm, to))

        # castling
        C_000 = 0x0E << self.player*56
        C_00 = 0x60 << self.player*56
        king_sq = self.king[self.player]

        if self.castling & (2<<self.player*2) and C_000 & empty == C_000:
            # player can queenside castle
            moves.append(move.new(king_sq, king_sq - 3))

        if self.castling & (1<<self.player*2) and C_00 & empty == C_00:
            # player can king side castle
            moves.append(move.new(king_sq, king_sq + 2))
 
        # only return legal moves
        for m in moves:
            if self.is_legal(*m[:2]):
                yield m
