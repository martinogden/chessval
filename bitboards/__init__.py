"""
    A Bitboard is a 64-bit chess board representation

    +-----------------+
  8 | . . . . . x . . |
  7 | x . . . x . . . |
  6 | . x . x . . . . |
  5 | . . . . . . . . |
  4 | . x . x . . . . |
  3 | x . . . x . . . |
  2 | . . . . . x . . |
  1 | . . . . . . x . |
    +-----------------+
      A B C D E F G H

    A bishop on C5 would have the above attack set on an empty board.
    This would be represented as the 64-bit integer:
        dec 2310639079102947392
        hex 20110a000a112040
        bin 10000000010001000010100000000000001010000100010010000001000000
"""


from .masks import *
from .pieces  import *
from .pawns import *
from .debug import *
