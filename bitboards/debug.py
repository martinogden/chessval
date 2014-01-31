def ascii(bb, prnt=True):
    """ print board """
    output = ["." for _ in xrange(64)]
    for i in xrange(64):
        pos = (i | 56) - ((i >> 3) * 8)
        if (bb >> pos) & 1 == 1:
            output[i] = "x"
    ranks = []
    for r in xrange(8):
        ranks.append(' '.join(output[r*8:(r+1)*8]))

    board = '\n'.join(ranks)
    if not prnt:
        return board
    print board
