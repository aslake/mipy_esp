"""
Led functions for toggling and blinking of leds.

Aslak Einbu Jan 2020

"""

import utime


def toggle(led):
    """ Toggle led on/off. """
    if led.value() == 1:
        led.value(0)
    else:
        led.value(1)


def blink(led, times, on_time, off_time):
    """ Led blink sequence. """
    for i in range(times):
        led.on()
        utime.sleep(on_time)
        led.off()
        utime.sleep(off_time)

