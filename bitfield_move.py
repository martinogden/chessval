"""
    A Move is a 32-bit bitfield

    +----------------------------------------------+
    | Move bitfield                       (32-bit) |
    +--------+--------+-----+---+--------+-----+---+
    | FFFFFF | TTTTTT | PPP | p | CCCCCC | xxx | c |
    +--------+--------+-----+---+--------+-----+---+
    | 0      | 6      | 12  | 15|16      | 22  | 25|
    +--------+--------+-----+---+--------+-----+---+

    +---+-----------------------+
    | F | from                  |
    | T | to                    |
    | P | piece                 |
    | p | player                |
    | C | capture / ep square   |
    | e | en passant            |
    | x | captured piece        |
    | c | castle                |
    +---+-----------------------+

"""

TO_SHIFT = 6
PIECE_SHIFT = 12
PLAYER_SHIFT = 15
CAPTURE_EP_SHIFT = 16
CPIECE_SHIFT = 22
CASTLE_SHIFT = 25

FULL_MASK  = 0xFFFFFFFFL
SQ_MASK    = 0x0000003FL
PIECE_MASK = 0x00000007L
BIT_MASK   = 0x00000001L





def get_from(mv):
    return mv & SQ_MASK


def get_to(mv):
    return mv >> TO_SHIFT & SQ_MASK


def get_piece(mv):
    return mv >> PIECE_SHIFT & PIECE_MASK


def get_player(mv):
    return mv >> PLAYER_SHIFT & BIT_MASK


def get_capture_ep(mv):
    return mv >> CAPTURE_EP_SHIFT & SQ_MASK


def get_cpiece(mv):
    return mv >> CPIECE_SHIFT & PIECE_MASK


def get_castle(mv):
    return mv >> CASTLE_SHIFT & BIT_MASK


def set_from(mv, sq):
    mv &= (~SQ_MASK & FULL_MASK)
   return mv | sq


def set_to(mv, sq):
    mv &= (FULL_MASK & ~(SQ_MASK << TO_SHIFT))
    return mv | sq << TO_SHIFT


def set_piece(mv, piece):
    mv &= (FULL_MASK & ~(PIECE_MASK << PIECE_SHIFT))
    return mv | piece << PIECE_SHIFT


def set_player(mv, bit):
    mv | bit << PLAYER_SHIFT


def set_capture_ep(mv, sq):
    mv &= (FULL_MASK & ~(SQ_MASK << CAPTURE_EP_SHIFT))
    return mv | sq << CAPTURE_EP_SHIFT


def set_cpiece(mv, piece):
    mv &= (FULL_MASK & ~(PIECE_MASK << CPIECE_SHIFT))
    return mv | piece << CPIECE_SHIFT


def set_castle(mv, bit):
    return mv | bit << CASTLE_SHIFT
