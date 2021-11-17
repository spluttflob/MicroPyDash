""" @file svgtest.py
        This file contains some tests in which I try to make SVG display 
        objects in super-simple Python so that they may be run on MicroPython. 
    @author JR Ridgely
    @date 2020-Jan-25 JRR Original file
"""

import math


## The background color for the page
BACKGROUND_COLOR = "#202020"

## The default font color used on the page
FONT_COLOR = "#FFFFFF"

## The type of font to be used for the HTML page
FONT_FAMILY = "Arial, Helvetica, sans-serif"

## The number of seconds between page reloads
RELOAD_RATE_SEC = 3


def polar2cartesian (x_center, y_center, radius, angle_deg):
    """ Function which converts locations such as the ends of an arc from
    polar to x,y coordinates.
    @param x_center The X coordinate of the center of the arc
    @param y_center The Y coordinate of the center of the arc
    @param radius The arc's radius
    @param angle_deg The angle of the given location in degrees
    @returns A tuple containing the x and y coordinates
    """
    angle_rad = angle_deg * math.pi / 180.0 
    return (x_center + radius * math.cos (angle_rad),
            y_center - radius * math.sin (angle_rad))


def svg_arc (x_center, y_center, radius, start_angle, end_angle):
    """ Function to create SVG code for an arc.
    @param x_center The X coordinate of the center of the arc
    @param y_center The Y coordinate of the center of the arc
    @param radius The arc's radius
    @param start_angle The angle from which the arc begins
    @param end_angle The angle to which the arc goes
    """
    # Convert the starting and ending points to rectangular coordinates
    start_pt = polar2cartesian (x_center, y_center, radius, start_angle)
    end_pt = polar2cartesian (x_center, y_center, radius, end_angle)

    # Set a flag which indicates if the arc covers more than 180 degrees
    big_arc = 0 if end_angle - start_angle < 180.0 else 1

    return ("M {:.3f} {:.3f} A {:d} {:d} 0 {:d} 0 {:.3f} {:.3f}".format (
            start_pt[0], start_pt[1],
            int (radius), int (radius), 
            big_arc, 
            end_pt[0], end_pt[1]))


# -----------------------------------------------------------------------------

class SVG_item:
    """ This is a base class for SVG displayable objects such as meters, plots,
    and sliders.
    """

    def __init__ (self, pos_x, pos_y, width, height, sender, border=False):
        """ Create a base SVG object which remembers its width and height as
        well as how to send bytes to a file, network socket, or wherever bytes
        need to go so they can get to a browser.
        @param pos_x The X coordinate in pixels of the upper left corner
        @param pos_y The Y coordinate in pixels of the upper left corner
        @param width The width on the screen
        @param height The height on the screen
        @param sender A callable which sends a string to a browser
        @param border Whether or not to draw a border rectangle
        """
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.width = width
        self.height = height
        self.sender = sender
        self.border = border

        self.border_color = "yellow"
        self.border_width = 2
        self.text_color = "white"
        self.text_size = 24


    def header (self):
        """ Use the sender to send the SVG header and a border if needed.
        """
        self.send ('<svg width="{:d}" height="{:d}">\n'.format (self.width, 
                   self.height))
        if self.border:
            self.send ('<rect x="0" y="0" width="{:d}" height="{:d}" '.format (
                       self.width, self.height))
            self.send ('style="stroke:{:s};stroke-width:{:d};'.format (
                       self.border_color, self.border_width))
            self.send ('fill:none;opacity:0.5" />\n')


    def footer (self):
        """ Use the sender to send the SVG footer at the end of this graphic.
        """
        self.send ('There should be a meter here; ')
        self.send ('your browser may not support SVG images.</svg>\n')


    def draw_text (self, text, x_pos, y_pos, size="medium", anchor="start"):
        """ Draw text in the normal text color at the given location within the
        SVG image.
        @param text The text to be drawn
        @param x_pos The X location for the text
        @param y_pos The Y location for the text
        @param size The size for the text in pixels
        @param anchor A value which causes text to be 'start', 'middle', or
               'end' anchored; default is 'left'
        """
        self.send ('<text x="{:d}" y="{:d}" style="fill:{:s}'.format (
                   x_pos, y_pos, self.text_color))
        self.send (';font-size:{:d}px;text-anchor:{:s}">{:s}</text>\n'.format (
                   size, anchor, text))


    def send (self, a_string):
        """ Send a string or a bytearray to whatever file or network port is
        used to get the data to a display device.
        @param a_string The string or byte array to be sent
        """
        self.sender (a_string)
        # TODO: Convert strings to bytes objects, maybe?


# -----------------------------------------------------------------------------

class Meter (SVG_item):
    """ This class implements a panel meter like display on an HTML page.
    The meter is drawn using SVG graphics.
    """

    def __init__ (self, pos_x, pos_y, width, height, sender, label="Meter",
                  units = "", text_size=24, min_val=0, max_val=10, 
                  border=False, arc_angle=160, full_color="#808000",
                  empty_color="#303030", needle_color="#FFFFFF"):
        """  Create a panel meter object. 
        @param pos_x The X coordinate in pixels of the upper left corner
        @param pos_y The Y coordinate in pixels of the upper left corner
        @param width The width on the screen
        @param height The height on the screen
        @param sender A callable which sends a string to a browser
        @param label A label to show what's measured and hopefully units
        @param units A string indicating the units of the measurand
        @param text_size The size for label and meter value text
        @param min_val The value at which the needle reads minimum
        @param max_val The value at which the needle reads maximum
        @param border Whether or not to draw a border rectangle
        @param arc_angle The angle in degrees through which the needle travels
        @param full_color The color of the "full" part of the needle arc
        @param empty_color The color of the "not full" part of the needle arc
        """
        super ().__init__ (pos_x, pos_y, width, height, sender, border)

        self.label = label
        self.units = units
        self.text_size = text_size
        self.min_val = min_val
        self.max_val = max_val
        self.arc_angle = arc_angle
        self.full_color = full_color
        self.empty_color = empty_color
        self.needle_color = needle_color

        ## The value sent to this meter to be displayed
        self.disp_value = min_val


    def draw (self):
        """ Draw the panel meter by creating its SVG image.
        """
        self.header ()

        # Saturate the value which is used to set the needle angle
        needle_value = self.disp_value
        if needle_value > self.max_val:
            needle_value = self.max_val
        elif needle_value < self.min_val:
            needle_value = self.min_val

        # Draw an arc which represents how "full" the reading is from the left
        # side of the meter to the needle angle; draw another arc from the
        # needle angle to the end of the needle's possible travel angle
        x_center = self.width // 2
        y_center = self.height * 80 // 100
        start_angle = 90 + self.arc_angle / 2
        end_angle = 90 - self.arc_angle / 2
        arc_radius = self.width * 40 // 100
        needle_angle = start_angle - self.arc_angle \
                       * (needle_value - self.min_val) \
                       / (self.max_val - self.min_val)

        # First the non-filled part of the arc, as it's on the right
        self.send ('<path id="arc0" d="{:s}" fill="none" '.format (
                   svg_arc (x_center, y_center,         # Center X, Y
                            arc_radius,                 # Radius
                            end_angle,                  # Angles
                            needle_angle)))
        self.send ('stroke="{:s}" stroke-width="{:d}" />\n'.format (
                   self.empty_color, self.height // 8))

        # Next the filled up portion of the arc
        self.send ('<path id="arc0" d="{:s}" fill="none" '.format (
                   svg_arc (x_center, y_center,         # Center X, Y
                            arc_radius,                 # Radius
                            needle_angle,               # Angles
                            start_angle)))
        self.send ('stroke="{:s}" stroke-width="{:d}" />\n'.format (
                   self.full_color, self.height // 8))

        # Draw the needle
        tip = polar2cartesian (x_center, y_center, 
                               arc_radius * 1.3, needle_angle)
        base_high = polar2cartesian (x_center, y_center, 
                                     arc_radius * 0.7, needle_angle + 5)
        base_low = polar2cartesian (x_center, y_center, 
                                    arc_radius * 0.7, needle_angle - 5)
        self.send ('<polygon points="{:.2f},{:.2f} {:.2f},{:.2f} {:.2f},{:.2f}" '.format (
                   tip[0], tip[1], base_high[0], base_high[1], 
                   base_low[0], base_low[1]))
        self.send ('style="stroke:none;fill:{:s}" />\n'.format (self.needle_color))

        # Display the meter label
        self.draw_text (self.label, x_center, self.height * 14 // 100, 
                        anchor='middle', size=(self.height // 8))

        # Display the value of the measured quantity and units
        self.draw_text ("{:.3g}{:s}".format (self.value, self.units), 
                        x_center, self.height * 9 // 10, 
                        anchor='middle', size=(self.height // 6))

        # Display the minimum and maximum readings on the scale
        self.draw_text ("{:g}".format (self.max_val),
                        self.width // 2 + arc_radius, self.height * 94 // 100,
                        anchor="middle", size=(self.height // 12))
        self.draw_text ("{:g}".format (self.min_val),
                        self.width // 2 - arc_radius, self.height * 94 // 100,
                        anchor="middle", size=(self.height // 12))

        self.footer ()


    @property
    def value (self):
        """ Read the value currently being displayed.
        @returns The current meter value
        """
        return self.disp_value


    @value.setter
    def value (self, new_value):
        """ Set the value to be displayed on the meter. The value will be
        saturated to the maximum and minimum the meter can display to imitate
        the physical restrictions of a meter needle. Just setting the value
        does @b not cause redrawing of the meter; that must be done separately.
        @param The new value to be displayed presently
        """
        self.disp_value = new_value


# -----------------------------------------------------------------------------

def page_style (sender):
    """ Use CSS to set a page style.
    """
    sender ('<style>body{background-color:#f0f0f0;text-color:blue;</style>\n')
#    sender ('font-family:"Helvetica,Arial,sans-serif"</style>\n')


def header (a_file):
    """ Create an HTML page header. 
    @param a_file The file object to which to print the header
    """
    a_file.write ('<html><body style="background-color:{:s}">'.format (
                  BACKGROUND_COLOR))
    a_file.write ('<font face="{:s}">\n'.format (FONT_FAMILY))
    a_file.write ('<font color="{:s}">\n'.format (FONT_COLOR))
    a_file.write ('<meta http-equiv="refresh" content="{:g}">\n'.format (
                  RELOAD_RATE_SEC))
#    page_style (a_file.write)
    a_file.write ("<h3>Testing SVG generation</h3><br>\r\n")


def footer (a_file):
    """ Create a generic HTML page footer.
    @param a_file The file object to which to print the footer
    """
    a_file.write ("</body></html>")


def test ():
    """ Create the test page.
    """
    import random

    with open ("svgtest.html", "w") as da_file:
        header (da_file)

        minny = -100.0
        maxie = 100.0
        meter = Meter (10, 10, 250, 200, da_file.write, border=True,
                       min_val=minny, max_val=maxie,
                       units=" FU", arc_angle=180)
        true_value = ((maxie + minny) / 2) \
                     + ((random.random () - 0.5) * (maxie - minny) * 1.5)
        meter.value = true_value
        print ("Value: {:g}".format (true_value))
        meter.draw ()

        footer (da_file)


if __name__ == "__main__":
    test ()
