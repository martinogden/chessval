def ascii(bb):
    """ print board """
    output = ["." for _ in xrange(64)]
    for i in xrange(64):
        pos = (i | 56) - ((i >> 3) * 8)
        if (bb >> pos) & 1 == 1:
            output[i] = "x"
    for r in xrange(8):
        print ' '.join(output[r*8:(r+1)*8])
