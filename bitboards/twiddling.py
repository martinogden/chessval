### Bit Twiddling helpers ###


def is_set(bb, bit):
    """ Is bit a position `bit` set? """
    return (bb & 1 << bit) != 0


def set_bit(bb, bit):
    """ Set a bit to on `1` """
    return bb | (1 << bit)


def unset_bit(bb, bit):
    """ Set a bit to off `0` """
    return bb & ~(1 << bit)


def twiddle_bit(bb, bit):
    """ Flip a bit from on to off and vice-versa """
    return bb ^ (1 << bit)


def get_rank(bit):
    return bit / 8


### Bitboard twiddling helpers ###

def mirror(bb):
    """ Mirror a bitboard horizontally """
    # masks
    m1 = 0x5555555555555555L
    m2 = 0x3333333333333333L
    m4 = 0x0F0F0F0F0F0F0F0FL
 
    bb = ((bb >> 1) & m1) + 2 * (bb & m1)
    bb = ((bb >> 2) & m2) + 4 * (bb & m2)
    bb = ((bb >> 4) & m4) + 16 * (bb & m4)

    return bb


def bitscan(bb):
    """ Reverse parallel bitscan to find LSB

        Modifed @Link graphics.stanford.edu/~seander/bithacks.html#ZerosOnRightParallel
        to deal with 64-bit integers
    """
    v = bb  # 64-bit word input to count zero bits on right
    c = 64  # c will be the number of zero bits on the right
    v &= -v
    if (v):
        c -= 1

    if (v & 0x00000000FFFFFFFF):
        c -= 32
    if (v & 0x0000FFFF0000FFFF):
        c -= 16
    if (v & 0x00FF00FF00FF00FF):
        c -= 8
    if (v & 0x0F0F0F0F0F0F0F0F):
        c -= 4
    if (v & 0x3333333333333333):
        c -= 2
    if (v & 0x5555555555555555):
        c -= 1
    return c


def get_set_bits(bb):
    """ Reverse parallel bitscan
    """
    bits = []
    while(bb):
        bit = bitscan(bb)
        bits.append(bit)
        bb &= ~(1 << bit) & 0xFFFFFFFFFFFFFFFFL
    return bits
