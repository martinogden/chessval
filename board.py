import logging

from constants import *
from serialization import Serializer
import bitboards as bb
import move


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
        self.ep = None
        self.castling = 0
        full_moves = 1
        half_moves = 0
        self.moves = []
        king = [-1, -1]
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
        cr = self.castling
        d = frm - to
        is_castling = piece % 8 == WHITE_KING and d in [-2, 2]  # todo do this properly

        if piece == -1:
            raise InvalidMove("No piece to move")

        if (piece & 8) >> 3 != self.player:
            raise InvalidMove("Not side to move")

        if promotion:
            if piece % 8 != WHITE_PAWN:
                raise InvalidMove("Only pawns can be promoted")
            if not 1 << to & bb.masks.RANK_MASK[7*(self.player^1)]:
                raise InvalidMove("Pawn cannot be promoted here")
            if (promotion & 8) >> 3 != self.player:
                raise InvalidMove("Invalid promotion piece")

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
            # validate castling
            if is_castling:
                if self.castling & (1<<self.player*2) and d == -2:
                    rook_sq = frm + 1  # king side castle
                elif self.castling & (2<<self.player*2) and d == 2:
                    rook_sq = frm - 1  # queen side castle
                else:
                    raise InvalidMove("Castling not allowed")

                if self.is_attacked(rook_sq, self.player^1):
                    raise InvalidMove("Castling not allowed: King passes through attacked square")
                if self.is_attacked(frm, self.player^1):
                    raise InvalidMove("Castling not allowed: King in check")
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

        ### pickup the pieces
        self.pickup(piece, frm)

        # special case: castling is a compound move, pickup both pieces
        if is_castling:
            rook_sq = to > frm and frm + 3 or frm - 4
            self.pickup(WHITE_ROOK | self.player<<3, rook_sq)


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

        ### drop the pieces
        if promotion:
            self.drop(promotion, to)
        else:
            self.drop(piece, to)

        if is_castling:
            rook_sq = to > frm and frm + 1 or frm - 1
            self.drop(WHITE_ROOK | self.player<<3, rook_sq)

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


        W_rooks = self.positions[WHITE_ROOK]
        W_king = self.king[WHITE]
        B_rooks = self.positions[WHITE_ROOK | 8]
        B_king = self.king[BLACK]
        if not (1<<7 & W_rooks and W_king == 4):
            self.castling &= 0xF ^ castling.WHITE_00
        if not (1 & W_rooks and W_king == 4):
            self.castling &= 0xF ^ castling.WHITE_000
        if not (1<<63 & B_rooks and B_king == 60):
            self.castling &= 0xF ^ castling.BLACK_00
        if not (1<<56 & B_rooks and B_king == 60):
            self.castling &= 0xF ^ castling.BLACK_000

        if is_castling:
            if to > frm:  # king-side
                flags |= move.flags.KCASTLE
            else:  # queen-side
                flags |= move.flags.QCASTLE

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

        self.moves.append(move.new(frm, to, cpiece, flags, cr, promotion))
        if self.is_attacked(self.king[self.player^1], self.player):
            self.unmakemove()
            raise KingInCheck()

    def unmakemove(self):
        mv = self.moves.pop()
        logging.debug("unmakemove: %s", mv)
        frm, to, cpiece, flags, cr, promotion = mv
        friendly_rook = WHITE_ROOK | (self.player^1)<<3  # for castling

        piece = self.occupancy[to]
        frm_sq = 1 << frm
        to_sq = 1 << to


        ### pickup pieces
        self.pickup(piece, to)

        if flags & move.flags.KCASTLE:
            self.pickup(friendly_rook, frm + 1)
        elif flags & move.flags.QCASTLE:
            self.pickup(friendly_rook, frm - 1)


        ### drop pieces
        if promotion:
            self.drop(WHITE_PAWN | (self.player^1)<<3, frm)
        else:
            self.drop(piece, frm)

        if flags & move.flags.KCASTLE:
            self.drop(friendly_rook, frm + 3)
        elif flags & move.flags.QCASTLE:
            self.drop(friendly_rook, frm - 4)


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
            pfrm, pto, pcpiece, pflags, pcr, ppromotion = self.moves[-1]
            if pflags & move.flags.DPUSH:
                self.ep = pfrm + (pto - pfrm) / 2

        self.player ^= 1
        self.full_moves -= self.player  # update on black
        self.castling = cr

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
        def do_promo(frm, to):
            # check for promotions
            if 1 << to & bb.masks.RANK_MASK[7*(self.player^1)]:
                for piece in [WHITE_KNIGHT, WHITE_BISHOP, WHITE_ROOK, WHITE_QUEEN]:
                    moves.append(move.new(frm, to, promotion=piece | self.player<<3))
            else:
                # otherwise, just a normal push / attack
                moves.append(move.new(frm, to))

        pawns = self.positions[WHITE_PAWN | self.player << 3]

        spushes = bb.P_spushes[self.player](pawns, empty)
        dpushes = bb.P_dpushes[self.player](pawns, empty)

        for frm in bb.get_set_bits(pawns):

            attacks = bb.P_attacks[self.player](enemy, frm)
            for to in bb.get_set_bits(attacks):
                do_promo(frm, to)

            if 1 << frm & spushes:
                to = frm + 8 - self.player*16
                do_promo(frm, to)

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

        if self.castling & (2<<self.player*2) and C_000 & empty == C_000 and\
                not self.is_attacked(king_sq - 1, self.player^1) and\
                not self.is_attacked(king_sq, self.player^1):
            # player can queenside castle
            moves.append(move.new(king_sq, king_sq - 2))

        if self.castling & (1<<self.player*2) and C_00 & empty == C_00 and\
                not self.is_attacked(king_sq + 1, self.player^1) and\
                not self.is_attacked(king_sq, self.player^1):
            # player can king side castle
            moves.append(move.new(king_sq, king_sq + 2))
 
        # only return legal moves
        for m in moves:
            if self.is_legal(*m[:2]):
                yield m
