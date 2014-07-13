import sys
import csv

from debug import Debugger
from board import Board

if len(sys.argv) > 1:
    depth = int(sys.argv[1])
    assert 0 < depth < 7


board = Board()
debugger = Debugger(board, quiet=True)


def parse_perftsuite():
    with open('test/perftsuite.epd', 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        for row in reader:
            parsed = [c.strip() for c in row]
            fen, results = parsed[0], [r.split() for r in parsed[1:]]
            yield fen, {k: int(v) for k, v in results}


l = 0
for fen, results in parse_perftsuite():
    l += 1
    board.reset(fen)
    if not 'D%i' % depth in results: continue
    try:
        assert debugger.divide(depth) == results['D%i' % depth]
    except AssertionError as e:
        print "Error\n====="
        print l, fen
        import pdb; pdb.set_trace()

print "OK"