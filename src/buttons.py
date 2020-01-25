"""
Button interactions - with callback.

Aslak Einbu, Jan  2020

"""

from machine import Pin
import logfile
import config

log = logfile.LogFile("Button-test", config.log_filename, config.log_sizelimit,
                      config.log_level, config.log_print)


class Button:
    """ Attach pin and callback to button."""
    def __init__(self, pin, callback):
        self.pin = pin
        self.state = Pin(pin, Pin.IN, Pin.PULL_UP)
        self.laststate = self.state.value()
        self.callback = callback
        log.debug("Button attached to pin %s with callback %s" % (str(pin), str(callback)))

    def check_pressed(self):
        """ Run callback function if button was pressed since last check. """
        state = self.state.value()
        if state != self.laststate:
            if state == 1:
                self.callback()
        self.laststate = state

    def is_on(self):
        """ Check if button is pressed. """
        if self.state.value() == 0:
            return True
        else:
            return False






