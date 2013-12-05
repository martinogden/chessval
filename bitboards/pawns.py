from .masks import *
from .lookups import *

W = 0
B = 1

### Pawn attacks ###

def wP_attacks(enemy, sq):
    return enemy & P_ATTACKS[W][sq]


def bP_attacks(enemy, sq):
    return enemy & P_ATTACKS[B][sq]


### Pawn pushes ###

def wP_spushes(wpawns, empty):
    return (empty >> 8) & wpawns                # set of white pawns with an empty space in front of them


def wP_dpushes(wpawns, empty):
    empty_A3H3 = (empty & A4H4) >> 8 & empty    # set of (imag) white pawns that have made a single push
    return wP_spushes(wpawns, empty_A3H3)       # set of (imag) white pawns than can single push from 3rd rank


def bP_spushes(bpawns, empty):
    return (empty << 8) & bpawns


def bP_dpushes(bpawns, empty):
    empty_A6H6 = (empty & A5H5) << 8 & empty
    return bP_spushes(bpawns, empty_A6H6)
