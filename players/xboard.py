import re
import sys
import logging
from .player import Player

logging.basicConfig(**{
    'format': "[%(levelname)s] %(message)s",
    'filename': "xboard.log",
    'filemode': 'w',
    'level': logging.DEBUG,
})


MOVE_PATTERN = re.compile(r'^[a-h][1-8][a-h][1-8]$', re.IGNORECASE)


class XBoard(Player):

    def __init__(self, *args, **kwargs):
        super(XBoard, self).__init__(*args, **kwargs)
        logging.info("Game started")

    @staticmethod
    def to_index(san):
        f, r = list(san)
        return ((int(r) - 1) * 8) + ord(f.lower()) - 97

    def respond(self, msg):
        print msg
        sys.stdout.flush()

    def play(self):
        while True:
            cmd = sys.stdin.readline()
            if cmd:
                cmd = cmd.strip()
                logging.debug("[xboard] %s", cmd)
                try:
                    self.handle(cmd)
                except Exception, e:
                    logging.exception(e)

    def handle(self, cmd):
        if cmd == "xboard":
            self.respond("\n")

        elif cmd.startswith("protover"):
            logging.debug("[xboard] protocol v%i", cmd.split(" ")[1])
            self.respond("feature setboard=1 done=1")

        elif cmd == "new":
            self.board.reset()

        elif cmd.startswith("setboard"):
            try:
                fen = cmd.split("setboard ")[1]
                self.board.reset(fen)
                logging.info(fen == repr(self.board))
            except Exception, e:
                logging.exception(e)

        elif cmd == "quit":
            raise Exception("Game Over")
        elif re.match(MOVE_PATTERN, cmd):
            frm = XBoard.to_index(cmd[:2])
            to = XBoard.to_index(cmd[2:5])
            try:
                self.board.is_legal(frm, to)  # just in case
            except Exception, e:
                logging.exception(e)
                # logging.debug("Invalid move: %s [%s %s]", cmd, str(frm), str(to))
            else:
                self.board.makemove(frm, to)

            logging.info("%s", repr(self.board))
        else:
            # logging.error("unknown command %s", cmd)
            return  # ignore other commands for now
