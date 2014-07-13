import csv

from debug import Debugger
from board import Board


board = Board()
debugger = Debugger(board, quiet=False)


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
    if not 'D6' in results: continue
    try:
        assert debugger.divide(6) == results['D6']
        print "\n" +"+"*20+"\n"
    except AssertionError as e:
        print l, fen
        import pdb; pdb.set_trace()
