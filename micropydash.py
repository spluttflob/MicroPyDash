""" @file micropydash.py
        This file contains a very simple, lightweight HTML dashboard utility
        for MicroPython. The dashboard contains graphical elements which are
        somewhat similar to those in the Node-RED dashboard, which was the
        inspiration for this project. Node-RED is great if you have a PC or 
        Raspberry Pi on which to run it, but this project is aimed at small
        MicroPython platforms which would like to serve data on web pages
        without requiring anything but a browser on a PC or phone to use. 

        This is @b absolutely @b not a high-performance real-time plotting
        library. It is for comparatively low performance plotting in the sense
        that plots should be updated on browser screens on a timescale of 
        seconds, not milliseconds. 

    @author JR Ridgely

    @date 2020-Jan-25 JRR Original file
    
    @copyright (c) 2020 by JR Ridgely and released under the LGPL V3.
"""

import upd_base
import upd_meter
import upd_plot
import upd_input


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

    def __init__ (self, title="MicroPython Dashboard", sender=None, 
                  reload_rate=RELOAD_RATE_SEC):
        """ Initialize the dashboard interface.
        @param title A string to appear at the top of the dashboard web page
        @param sender A callable which writes HTML to a file or web socket, or
               None if the characters are to be thrown away because no sending
               device is currently ready
        @param reload_rate How often the web client is told to reload this page
               in seconds
        """
        self.send = sender
        self.reload_rate = reload_rate
        self.title = title

        ## A list of widgets (meters, buttons, etc.)
        self.widgets = []


    def add_widget (self, new_widget):
        """ Add the given widget to the set of widgets on the dashboard. The
        widget must have already been created, with its size specified. 
        """
        self.widgets.append (new_widget)
        new_widget.sender = self.send


    def set_sender (self, new_sender):
        """ Set a new callable which sends text to the web client. This needs
        to be done each time a new web connection is opened, and because of the
        weird way HTTP works, it happens frequently.
        @param new_sender A new function which sends characters to the Web
        """
        self.send = new_sender
        for widget in self.widgets:
            widget.sender = new_sender


    def header (self):
        """ Create an HTML page header. 
        @param a_file The file object to which to print the header
        """
        self.send ('<html><head>')

        # If there are buttons present, send their CSS style
        if upd_input.Button.buttons_present ():
            self.send ('<style>')
            self.send ('a.button {{ appearance: button; color:{:s}; '.format (
                       upd_input.Button.text_color))
            self.send ('background-color:{:s}; border: none; display:'.format (
                         upd_input.Button.background_color))
            self.send (' inline-block; padding: {:d}px {:d}px; '.format (
                         upd_input.Button.font_size // 2, 
                         upd_input.Button.font_size))
            self.send ('font-size: {:d}px; text-decoration: none; }}'.format (
                         upd_input.Button.font_size))
            self.send ('</style>')

        self.send ('</head>\n<body style="background-color:{:s}">'.format (
                       BACKGROUND_COLOR))
        self.send ('<font face="{:s}">\n'.format (FONT_FAMILY))
        self.send ('<font color="{:s}">\n'.format (FONT_COLOR))
        self.send ('<meta http-equiv="refresh" content="{:g}">\n'.format (
                       self.reload_rate))

        self.send ("<h3>{:s}</h3><br>\r\n".format (self.title))


    def footer (self):
        """ Create a generic HTML page footer.
        @param a_file The file object to which to print the footer
        """
        self.send ("</body></html>")


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
    
    import math

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

            # Create meters ---------------------------------------------------
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

            # Try a line break ------------------------------------------------
            break0 = upd_base.LineBreak ()
            dash.add_widget (break0)

            # Let's try a static plot -----------------------------------------
            plot0 = upd_plot.Plot (0, 0, 420, 320, title="It's a Plot", 
                                   num_traces=2)
            dash.add_widget (plot0)

            x_data = [t / 55 for t in range (120)]
            x_scaled = [t * 200 for t in x_data]
            y0_data = [x * x - x * x * x / 2.1 for x in x_data]
            y1_data = [math.sin (6.283 * t) for t in x_data]

            plot0.set_data (x_scaled, [y0_data, y1_data])
            plot0.traces[0].lines = True
            plot0.traces[0].markers = False

#            # Re-add the line break so the plots stack vertically
#            dash.add_widget (break0)

            # Try a scrolling plot --------------------------------------------
            SIZE1 = 20
            plot1 = upd_plot.Plot (0, 0, 400, 300, title="Scroll Me",
                                   x_label="Exiness", y_label="Y Bother",
                                   num_traces=1, scrolling=SIZE1)
            dash.add_widget (plot1)

            # Re-add the line break
            dash.add_widget (break0)

            # Try input -------------------------------------------------------
            button0 = upd_input.Button (None, "Button 0")
            dash.add_widget (button0)

            # Have things redrawn one or more times for testing purposes
            simtime = 0.0
            for count in range (SIZE1 * 3 // 2):

                true_value = ((maxie + minny) / 2) \
                             + ((random.random () - 0.5) * (maxie - minny))
                meter0.value = true_value

                meter1.value += 0.1375

                # Put another point into the scrolling plot
                simy = math.sin (simtime)
                plot1.add_data (simtime, [simy])
                simtime += 0.3125

                # Have the dash draw itself, then snooze a bit
                da_file.seek (0)
                da_file.truncate ()
                dash.draw ()
                da_file.flush ()
                time.sleep (1.2)

    test ()


