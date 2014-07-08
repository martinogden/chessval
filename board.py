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
    ep = None
    castling = 0x00

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
        from_sq = 1<<frm
        friendly_king = self.king[self.player]

        self.positions[-1] ^= from_sq
        is_king_attacked = self.is_attacked(friendly_king, self.player^1)
        self.positions[-1] |= from_sq

        return not is_king_attacked

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
            # all other pieces can be dealt with generically
            attacks = bb.attacks[piece % 8](occ, frm)
            targets = attacks & (bb.masks.FULL ^ friendly)
            if targets & (1<<to) == 0L:
                raise InvalidMove("Invalid slider target sq")
            # TODO castling moves


        #################
        ##### Make move #
        piece = self.occupancy[frm]
        cpiece = self.occupancy[to]
        frm_sq = 1 << frm
        to_sq = 1 << to
        flags = 0

        ### pickup pieces
        self.occupancy[frm] = -1
        not_frm_sq = bb.masks.FULL ^ frm_sq
        self.positions[piece] &= not_frm_sq
        self.positions[OFFSET + self.player] &= not_frm_sq
        self.positions[-1] &= not_frm_sq

        # handle capture
        if cpiece > -1:
            self.positions[cpiece] &= bb.masks.FULL ^ to_sq
            self.positions[OFFSET + (self.player^1)] &= bb.masks.FULL ^ to_sq
            flags |= move.flags.CAPTURE

        elif to == self.ep and piece % 8 == WHITE_PAWN:  # handle en passant capture
            oppnt = self.player^1
            oppnt_pawn = to - 8 + self.player*16
            not_c_sq = bb.masks.FULL ^ (1<<oppnt_pawn)

            self.occupancy[oppnt_pawn] = -1
            self.positions[WHITE_PAWN | oppnt<<3] &= not_c_sq
            self.positions[OFFSET + oppnt] &= not_c_sq
            self.positions[-1] &= not_c_sq

            cpiece = WHITE_PAWN | oppnt<<3
            flags |= move.flags.EP | move.flags.CAPTURE

        ### drop pieces
        self.occupancy[to] = piece
        self.positions[piece] |= to_sq
        self.positions[OFFSET + self.player] |= to_sq
        self.positions[-1] |= to_sq
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

        # pickup pieces
        self.occupancy[to] = -1
        not_to_sq = bb.masks.FULL ^ to_sq
        self.positions[piece] &= not_to_sq
        self.positions[OFFSET + (self.player^1)] &= not_to_sq
        self.positions[-1] &= not_to_sq


        ### drop pieces
        self.occupancy[frm] = piece
        self.positions[piece] |= frm_sq
        self.positions[OFFSET + (self.player^1)] |= frm_sq
        self.positions[-1] |= frm_sq
        # update king position (for check detection)
        if piece % 8 == WHITE_KING:
            self.king[self.player ^ 1] = frm


        if flags & move.flags.EP:  # revert en passant capture
            oppnt_pawn = to - 8 + (self.player^1) * 16
            pawn_sq = 1 << oppnt_pawn

            self.occupancy[oppnt_pawn] = cpiece
            self.positions[WHITE_PAWN | self.player<<3] |= pawn_sq
            self.positions[OFFSET + self.player] |= pawn_sq
            self.positions[-1] |= pawn_sq

        elif flags & move.flags.CAPTURE:  # revert capture
            self.positions[cpiece] |= to_sq
            self.positions[OFFSET + self.player] |= to_sq
            self.positions[-1] |= to_sq
            self.occupancy[to] = cpiece


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


        for frm in bb.get_set_bits(pawns):

            if 1 << frm & dpushes:
                to = frm + 16 - self.player*32
                moves.append(move.new(frm, to))


        for piece in [WHITE_KING, WHITE_KNIGHT, WHITE_BISHOP, WHITE_ROOK, WHITE_QUEEN]:
            piece_bb = self.positions[piece | self.player << 3]
            for frm in bb.get_set_bits(piece_bb):
                attacks = bb.pieces.attacks[piece](occ, frm) & nfriendly
                for to in bb.get_set_bits(attacks):
                    moves.append(move.new(frm, to))

        # only return legal moves
        for m in moves:
            if self.is_legal(*m[:2]):
                yield m
