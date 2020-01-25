"""Tester for logfile.py."""

import logfile

levels = "DEBUG INFO WARNING ERROR".split()

log = logfile.LogFile("TestLog", "testlog.txt", 200, "DEBUG", False)
for i in range(10):
    ind = i % 4
    msg = "Melding {}".format(i)
    if levels[ind] == "DEBUG":
        log.debug(msg)
    elif levels[ind] == "INFO":
        log.info(msg)
    elif levels[ind] == "WARNING":
        log.warning(msg)
    elif levels[ind] == "ERROR":
        log.error(msg)

log.level = "DEBUG"

log.debug("Sjekk om vi får ut debug melding til slutt")
