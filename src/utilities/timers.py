"""
Various utility functions.

Aslak Einbu Jan 2020
"""

import utime


class Countdown:
    """ Timer object for elapsed time check. """

    def __init__(self, countdowntime):
        self.countdowntime = countdowntime
        self.starttime = 0

    def start(self):
        """ Starts countdown timer. """
        self.starttime = utime.time()

    def is_overdue(self):
        """ Check if countdowntime has elapsed since start. """
        if (utime.time() - self.starttime) > self.countdowntime :
            return True
        else:
            return False
