""" @file micropydash.py
        This file contains a very simple, lightweight HTML dashboard utility
        for MicroPython. The dashboard contains graphical elements which are
        somewhat similar to those in the Node-RED dashboard, which was the
        inspiration for this project. Node-RED is great if you have a PC or 
        Raspberry Pi on which to run it, but this project is aimed at small
        MicroPython platforms which would like to serve data on web pages
        without requiring anything but a browser on a PC or phone to use. 

    @author JR Ridgely

    @date 2020-Jan-25 JRR Original file
    
    @copyright (c) 2020 by JR Ridgely and released under the LGPL V3.
"""

import upd_meter
import upd_plot


## The background color for the page
BACKGROUND_COLOR = "#202020"

## The default font color used on the page
FONT_COLOR = "#FFFFFF"

## The type of font to be used for the HTML page
FONT_FAMILY = "Arial, Helvetica, sans-serif"

## The number of seconds between page reloads
RELOAD_RATE_SEC = 3


# -----------------------------------------------------------------------------

class MicroPyDash:
    """ This class implements an HTML based dashboard. Elements such as meters,
    plots, and buttons (hopefully someday!) are used to create a real-time-ish
    display and control interface for a small MicroPython board. Only a browser
    is needed to operate the dashboard.
    """

    def __init__ (self, sender=None, reload_rate=RELOAD_RATE_SEC):
        """ Initialize the dashboard interface.
        @param sender A callable which writes HTML to a file or web socket, or
               None if the characters are to be thrown away because no sending
               device is currently ready
        """
        self.sender = sender
        self.reload_rate = reload_rate

        ## A list of widgets (meters, buttons, etc.)
        self.widgets = []


    def add_widget (self, new_widget):
        """ Add the given widget to the set of widgets on the dashboard. The
        widget must have already been created, with its size specified. 
        """
        self.widgets.append (new_widget)
        new_widget.sender = self.sender


    def set_sender (self, new_sender):
        """ Set a new callable which sends text to the web client. This needs
        to be done each time a new web connection is opened, and because of the
        weird way HTTP works, it happens frequently.
        @param new_sender A new function which sends characters to the Web
        """
        self.sender = new_sender
        for widget in self.widgets:
            widget.sender = new_sender


    def header (self):
        """ Create an HTML page header. 
        @param a_file The file object to which to print the header
        """
        self.sender ('<html><body style="background-color:{:s}">'.format (
                       BACKGROUND_COLOR))
        self.sender ('<font face="{:s}">\n'.format (FONT_FAMILY))
        self.sender ('<font color="{:s}">\n'.format (FONT_COLOR))
        self.sender ('<meta http-equiv="refresh" content="{:g}">\n'.format (
                       self.reload_rate))
        self.sender ("<h3>Testing MicroPython Dashboard</h3><br>\r\n")


    def footer (self):
        """ Create a generic HTML page footer.
        @param a_file The file object to which to print the footer
        """
        self.sender ("</body></html>")


    def draw (self):
        """ Redraw the web interface. This might be done in response to an HTML
        query or it might just be saving a page in a file.
        """
        self.header ()

        for widget in self.widgets:
            widget.draw ()

        self.footer ()


# -----------------------------------------------------------------------------

if __name__ == "__main__":

    # A reference to a file to which text will be printed instead of sending it
    # through a web interface. This makes for handy debugging, as a browser can
    # just read the file and refresh itself quickly and easily
    da_file = None


    def file_sender (text):
        """ Send text to the Web client. This function is here in case some
        conversion needs to be done (strings to byte arrays or whatever).
        """
        da_file.write (text)


    def test ():
        """ Create the test page.
        """
        import time
        import random
        global da_file

        with open ("svgtest.html", "w") as file_handle:
            da_file = file_handle

            # Create the dashboard object, using writing to a file to send HTML
            dash = MicroPyDash (sender=file_sender)

            # Create a meter
            minny = -100.0
            maxie = 100.0
            meter0 = upd_meter.Meter (10, 10, 250, 200, border=False,
                                      min_val=minny, max_val=maxie,
                                      label="Randomness",
                                      units=" FU", arc_angle=180)
            dash.add_widget (meter0)

            # Another meter
            meter1 = upd_meter.Meter (290, 10, 250, 200, border=False,
                                      min_val=0, max_val=5,
                                      label="Orderedness",
                                      units=" lb", arc_angle=180)

            dash.add_widget (meter1)
            meter1.value = 0.123

            # Let's try a scrolling(?) plot
            plot0 = upd_plot.Plot (0, 0, 420, 320, title="It's a Plot", 
                                   traces=1, buffer_size=10)
            dash.add_widget (plot0)

            x_data = [t / 10 for t in range (10)]
            x_scaled = [t * 100 for t in x_data]
            y_data = [x * x for x in x_data]
            plot0.set_data ([x_scaled, y_data])

            # Have things redraw a few times for testing purposes
            for count in range (1):

                true_value = ((maxie + minny) / 2) \
                             + ((random.random () - 0.5) * (maxie - minny))
                meter0.value = true_value

                meter1.value += 0.375

                # Have the dash draw itself, then snooze a bit
                da_file.seek (0)
                da_file.truncate ()
                dash.draw ()
                da_file.flush ()
                time.sleep (2.0)

    test ()


