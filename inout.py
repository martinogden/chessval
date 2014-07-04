import operator
import string
from bitboards.twiddling import *
from constants import *


def to_bit(san):
    file_, rank = list(san)
    return ((int(rank) - 1) * 8) + ord(file_.lower()) - 97


def san(square):
    return ''.join([string.lowercase[square % 8], str(square / 8 % 8 + 1)])


def from_fen(board, fen):
    """ Load a game from a fen representation """

    piece_map = {
        'P': WHITE_PAWN, 'K': WHITE_KING, 'N': WHITE_KNIGHT,
        'B': WHITE_BISHOP, 'R': WHITE_ROOK, 'Q': WHITE_QUEEN,
        'p': BLACK_PAWN, 'k': BLACK_KING, 'n': BLACK_KNIGHT,
        'b': BLACK_BISHOP, 'r': BLACK_ROOK, 'q': BLACK_QUEEN,
    }
    castling_map = {
        'Q': CASTLING_WHITE_00, 'K': CASTLING_WHITE_000,
        'q': CASTLING_BLACK_00, 'k': CASTLING_BLACK_000,
    }

    EMPTY = '-'
    positions, player, castling, en_passant, half_moves, full_moves = fen.split(' ')
    positions = reversed(positions.split('/'))

    bit = 0
    for rank in positions:
        for square in list(rank):
            if square.isdigit():
                bit += int(square)
            else:
                piece = piece_map[square]
                board.occupancy[bit] = piece
                bb = set_bit(board.positions[piece], bit)
                board.positions[piece] = bb
                bit += 1

    if castling != EMPTY:
        for availability in list(castling):
            board.castling |= castling_map[availability]

    board.player = "wb".index(player)

    if en_passant != EMPTY:
        board.en_passant = to_bit(en_passant)

    board.half_moves = int(half_moves)
    board.full_moves = int(full_moves)

    # Update white piece / black piece / all piece bitboards
    offset = 14  # offset of aggregated bitboards
    white = reduce(operator.or_, board.positions[:6])
    board.positions[offset+WHITE] = white

    black = reduce(operator.or_, board.positions[8:14])
    board.positions[offset+BLACK] = black

    board.positions[offset+ALL] = white | black


def unicode(board):
    rows = ["  A B C D E F G H\n"]
    row = ["1"]

    piece_map = [
        u'\u2659', u'\u2654', u'\u2658', u'\u2657', u'\u2656', u'\u2655', None,
        None, u'\u265F', u'\u265A', u'\u265E', u'\u265D', u'\u265C', u'\u265B',
    ]
    piece_positions = zip(piece_map, board.positions[:14])

    for square in xrange(65): # one extra square so last row gets added
        if square and square % 8 == 0:
            rows.append(u' '.join(row))
            row = [str(1 + (square/8))]
        has_piece = False

        for piece, bb in piece_positions:
            if bb & 1 << square:
                row.append(piece)
                has_piece = True
                break

        if not has_piece:
            row += [u'\u2591', u' '][(square + (square>>3)) % 2]

    return u'\n'.join(reversed(rows))
