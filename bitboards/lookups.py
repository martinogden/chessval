from .masks import *
from .twiddling import mirror


W = 0
B = 1
L_MASK = 0x3F3F3F3F3F3F3F3FL
R_MASK = 0xFCFCFCFCFCFCFCFCL


K_ATTACKS = [0L for _ in xrange(65)]                            # King attacks
N_ATTACKS = [0x00L for _ in xrange(65)]                         # Knight attacks
ATTACKS = [[0x00L for __ in xrange(256)] for _ in xrange(8)]    # 'Smeared' attacks for sliding pieces
P_ATTACKS = [[0x00L for __ in xrange(65)] for _ in xrange(2)]   # Pawn attacks


# Generate attack lookup tales for non-sliding pieces

# King attacks lookup table
K_OFFSETS = (7, 8, 9, 1, -7, -8, -9, -1)

for sq in xrange(65):
    for offset in K_OFFSETS:                                    # set all squares around king
        i = sq+offset
        if i > -1 and i < 64:                                    # only set if square is on the board
            K_ATTACKS[sq] |= (1<<i)

    if sq&7 < 4:                                                # mask off wrap arounds
        K_ATTACKS[sq] &= L_MASK
    else:
        K_ATTACKS[sq] &= R_MASK


# Knight attacks lookup table
N_OFFSETS = (6, 15, 17, 10, -6, -15, -17, -10)

for sq in xrange(65):
    for offset in N_OFFSETS:
        i = sq+offset
        if i > -1 and i < 64:
            N_ATTACKS[sq] |= (1<<i)

    if sq&7 < 4:
        N_ATTACKS[sq] &= L_MASK
    else:
        N_ATTACKS[sq] &= R_MASK


# Pawn attack lookup tables for both colors
P_OFFSETS = (7, 9)

for sq in xrange(65):
    for offset in P_OFFSETS:
        w = sq+offset
        b = sq-offset

        if w < 64:                                              # only set squares that are on the board
            P_ATTACKS[W][sq] |= 1<<w 
        if b > -1:
            P_ATTACKS[B][sq] |= 1<<b

        if sq&7 < 4:                                            # mask off wrap arounds
            P_ATTACKS[W][sq] &= FULL ^ A8H8
            P_ATTACKS[B][sq] &= FULL ^ A8H8
        else:
            P_ATTACKS[W][sq] &= FULL ^ A1H1
            P_ATTACKS[B][sq] &= FULL ^ A1H1


# Attacks for all occupancy variations on first rank "smeared"
# up over all ranks used to generate sliding piece attack sets
for i in xrange(8):
    for j in xrange(65):
        occ = j<<1
        sq = 1<<i

        east = (occ - (2 * sq))                                 # fill east until first block (inclusive)
        west = mirror(mirror(occ) - (2 * mirror(sq)))           # fill west until first block (inclusive)

        ATTACKS[i][j] = ((east ^ west) & 0xFF) * A1H1           # smear 1st rank occupancy across all ranks
