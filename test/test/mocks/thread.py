from builtins import super
from threading import Thread

class MockThread(Thread):
    def __init__(self, target=None, args=None):
        super().__init__(target=target, args=args)
        self._terminates = 0
        self.exitcode = 0 # TODO maybe this needs to be setable? Mock sys.exit

    def terminate(self):
        self._terminates += 1
