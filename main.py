""" @file main.py
      This program fabricates artificial readings and sends them to a web 
      client (usually a browser) through an itty bitty webserver. 

      Based on example by the ESP8266 Micropython folks, at
      http://docs.micropython.org/en/latest/esp8266/esp8266/
              tutorial/network_tcp.html

    @author JR Ridgely

    @date 2020-Jan-26 Made from previous file which reads weather data

    @copyright (c) 2020 by JR Ridgely and released under the LGPL V3.
"""

import gc
import socket
import network
import machine
import micropydash
import upd_meter
import hx711


# There's no web client connected. This will become useful when one is
client = None


def web_sender (text):
    """ This function sends bytes to a web client if one is connected.
    @param text The bytes to be transmitted
    """
    global client

    if client is not None:
        client.send (text)


# Say hello to anyone listening on the USB-serial port
print ('ESP32 MicroPython Dashboard test: main.py')

# Prepare the network interface; make sure it disconnects previous session
access_point = network.WLAN (network.AP_IF)
access_point.active (True)
access_point.config (essid="thermy", password="stoodent")
#access_point.config (essid="thermy")
#access_point.config (authmode=3, password="stoodent")

print ("  Network: ", access_point.ifconfig ())

addr = socket.getaddrinfo ('0.0.0.0', 80)[0][-1]
socket2me = socket.socket ()
socket2me.setsockopt (socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
socket2me.bind (addr)
socket2me.listen (1)

print ('HTTP server listening on ', addr)

# Set up a MicroPython Dashboard object; its sender can't yet do anything, as
# the web isn't connected yet
dash = micropydash.MicroPyDash (web_sender, reload_rate=1)

# Create an HX711 force sensor object and a meter to display weight
fubar = hx711.HX711 (19, 5)
fubar.tare ()

minny = -50.0
maxie = 50.0
meter0 = upd_meter.Meter (10, 10, 250, 200, border=False,
                          min_val=minny, max_val=maxie,
                          label="Pushiness",
                          units=" FU", arc_angle=180)
dash.add_widget (meter0)


# -----------------------------------------------------------------------------
# Wait for HTTP requests and answer 'em as they arrive

while True:
    client, addr = socket2me.accept ()
    print ('Client connected from {:s} port {:d}'.format (addr[0], addr[1]))
    client_file = client.makefile ('rwb', 0)
    try:
        while True:
            line = client_file.readline ()
            if not line or line == b'\r\n':
                break

        # Tell the dashboard what function is used to send HTTP characters
        dash.set_sender (client.send)

        # Measure the weight and display it
        meter0.value = (fubar.read () - fubar.OFFSET) / 10000;

        # Have the dashboard do its drawing
        dash.draw ()

        client.close ()
        gc.collect ()
#        print ("Memory free: ", gc.mem_free ())

    except KeyboardInterrupt:
        break

    except OSError:
        machine.soft_reset ()

