
import sys
sys.dont_write_bytecode = False
import logging

import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "libs"))

logger = logging.getLogger("aqt.mediasrv")
logger.setLevel(logging.DEBUG)


def main():
    import libs
    from .features import cards_relocation
    from .features import import_ui
main()


