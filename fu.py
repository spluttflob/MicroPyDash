""" @file fu.py
      This file contains a test program for an HX711 Force Unit.
"""

import hx711


fubar = hx711.HX711 (19, 5)

fubar.tare ()
value = fubar.read ()
value = fubar.get_value ()

print (value)
