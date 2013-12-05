from .masks import *
from .lookups import *


# Non-sliding piece attacks

def K_attacks(occ, sq):
    return K_ATTACKS[sq]


def N_attacks(occ, sq):
    return N_ATTACKS[sq]


# Sliding piece attacks

def R_attacks(occ, sq):

    def rank(occ, sq):
        i = sq >> 3                                     # get rank index
        mask = RANK_MASK[i]                             # bit mask for rank
        occ = (((mask & occ) * B1B8) & FULL) >> 58      # calculate index
        return mask & ATTACKS[sq&7][occ]                # attack set for occupancy


    def file_(occ, sq):
        i = sq & 7                                      # get file index
        rsq = (sq ^ 56) >> 3                            # get rotated (90 A/C) square
        mask = FILE_MASK[i]                             # get file mask
        occ = A1H1 & (occ >> i)                         # shift occupancy to A file and mask
        occ = ((C2H7 *  occ) & FULL) >> 58              # rotate (90 A/C) occupancy onto 1st rank
        occ = (A1H8 * (ATTACKS[rsq][occ] & A1A8))       # use rotated occ and sq to index rank attack table
                                                        # (n.b: we need to mask the smeared attacks here)
        return (A8H8 & occ) >> (i^7)                    # mask occ with H file and shift back to correct file 

    return rank(occ, sq) | file_(occ, sq)


def B_attacks(occ, sq):

    def diag(occ, sq):
        i = 7 + (sq >> 3) - (sq & 7)
        mask = DIAG_MASK[i]
        occ = (((mask & occ) * B1B8) & FULL) >> 58
        return mask & ATTACKS[sq&7][occ]

     
    def adiag(occ, sq):
        i = (sq >> 3) + (sq & 7)
        mask = ADIAG_MASK[i]
        occ = (((mask & occ) * B1B8) & FULL) >> 58
        return mask & ATTACKS[sq&7][occ]

    return diag(occ, sq) | adiag(occ, sq)


def Q_attacks(occ, sq):
    return R_attacks(occ, sq) | B_attacks(occ, sq)
