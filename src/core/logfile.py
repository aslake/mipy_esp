"""
logfile: storage of logfiles

Created: Sat Jan 11 2020
Authors: Torbjørn Pettersen, Aslak Einbu
"""
__version__ = '0.1.0'
import os
import machine
import config


_level_dict = {"ERROR": 40,
               "WARNING": 30,
               "INFO": 20,
               "DEBUG": 10,
               "NOTSET": 0}


def _timestamp():
    """Get timestamp from the chip."""
    yr, mnt, day, wday, hh, mm, sec, ms = machine.RTC().datetime()
    return "{}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(yr, mnt, day, hh, mm, sec)


class LogFile:
    """Administration of log files on microcontroller devices."""
    def __init__(self, name, filename, sizelimit=1000, level="INFO", logprint=False):
        self.name = name
        self.filename = filename
        self.sizelimit = sizelimit
        self.level = level
        self.logprint = logprint
        if not filename in os.listdir():
            with open(filename, "w") as f:
                stamp = _timestamp()
                f.write("Log {} created {}\n".format(name, stamp))

    def debug(self, msg):
        self.log("DEBUG", msg)

    def info(self, msg):
        self.log("INFO", msg)

    def warning(self, msg):
        self.log("WARNING", msg)

    def error(self, msg):
        self.log("ERROR", msg)

    def log(self, flag, msg):
        """Add item to logfile. Drop old items if logfile>sizelimit."""
        if config.debug:
            stamp = _timestamp()
            if self.logprint:
                print("{} - {}: {}".format(stamp, flag, msg))
            if _level_dict[self.level] <= _level_dict[flag]:
                if (os.stat(self.filename)[6] > self.sizelimit):
                    with open(self.filename) as f:
                        log = f.readlines()
                        log = log[1:]

                    with open(self.filename, "w") as f:
                        for _line in log:
                            f.write(_line)
                else:
                    with open(self.filename, "a+") as f:
                        f.write("{} - {}: {}\n".format(stamp, flag, msg))
