A simple chess program.

### Usage

	>> from chessval import Chess
	>> chess = Chess()
	>> chess.makemove("a2-a4") # only LAN move format is supported (for now)
	'OK'
	>> chess.side_to_move()
	'B'
	>> print chess  # FEN board repr
	rnbqkbnr/pppppppp/8/8/P7/8/1PPPPPPP/RNBQKBNR b KQkq a3 0 1
	>> print unicode(chess)
	♜ ♞ ♝ ♛ ♚ ♝ ♞ ♜ 
	♟ ♟ ♟ ♟ ♟ ♟ ♟ ♟ 
	· x · x · x · x 
	x · x · x · x · 
	♙ x · x · x · x 
	x · x · x · x · 
	· ♙ ♙ ♙ ♙ ♙ ♙ ♙ 
	♖ ♘ ♗ ♕ ♔ ♗ ♘ ♖ 


### Testing

Chessval has a suite of perft tests, to test 120+ different positions to {1,2,3,4,5,6} ply.

	$ python test <ply>

A word of warning: running tests to 6-ply takes about 8 hours on a machine with a Core i5 and 8gb of RAM.

To see output of divide / perft pass `quiet=False` to the debugger in `test/__main__.py`.

### Licence

MIT Licence

### Authors

Martin Ogden
