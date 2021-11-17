""" @file upd_base.py
        This file contains basic utilities for a MicroPython dashboard. 

    @author jr
    
    @date Sat Jan 25 12:03:56 2020
        
    @copyright (c) 2020 by JR Ridgely and released under the LGPL V3.
"""

import math


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

    def __init__ (self, pos_x, pos_y, width, height, border=False):
        """ Create a base SVG object which remembers its width and height as
        well as how to send bytes to a file, network socket, or wherever bytes
        need to go so they can get to a browser.
        @param pos_x The X coordinate in pixels of the upper left corner
        @param pos_y The Y coordinate in pixels of the upper left corner
        @param width The width on the screen
        @param height The height on the screen
        @param border Whether or not to draw a border rectangle
        """
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.width = width
        self.height = height
        self.border = border

        self.sender = None

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
            self.send ('fill:none" />\n')


    def footer (self):
        """ Use the sender to send the SVG footer at the end of this graphic.
        """
        self.send ('There should be a widget here; ')
        self.send ('your browser may not support SVG images.</svg>\n')


    def draw_text (self, text, x_pos, y_pos, size="medium", anchor="start",
                   baseline=None, angle=None):
        """ Draw text in the normal text color at the given location within the
        SVG image.
        @param text The text to be drawn
        @param x_pos The X location for the text
        @param y_pos The Y location for the text
        @param size The size for the text in pixels
        @param anchor A value which causes text to be 'start', 'middle', or
               'end' anchored; default is 'left'
        @param baseline The vertical orientation of the text, for example
               'hanging' or 'central' or 'middle'
        @param angle An angle in degrees through which to rotate the text
        """
        self.send ('<text x="{:d}" y="{:d}" '.format (x_pos, y_pos))

        if angle is not None:
            self.send ('transform="rotate({:d} {:d},{:d})" '.format (
                       int (angle), x_pos, y_pos))
        if baseline is not None:
            self.send ('dominant-baseline="{:s}" '.format (baseline))
        self.send ('style="fill:{:s};'.format (self.text_color))
        self.send ('font-size:{:d}px;text-anchor:{:s}">{:s}</text>\n'.format (
                   size, anchor, text))


    def draw_line (self, x0, y0, x1, y1, color="#808080", width=1):
        """ Draw a line from position (x0, y0) to position (x1, y1) in the 
        given color and line width. The default is a thin, boring gray line.
        @param x0 The X coordinate of the starting point
        @param y0 The Y coordinate of the starting point
        @param x1 The X coordinate of the ending point
        @param y1 The Y coordinate of the ending point
        @param color The color in which the line is drawn
        @param width The line width in pixels
        """
        self.send ('<line x1="{:d}" y1="{:d}" x2="{:d}" y2="{:d}" '.format (
                   x0, y0, x1, y1))
        self.send ('style="stroke:{:s};stroke-width:{:d}" />\n'.format (
                   color, width))


    def draw_circle (self, x_center, y_center, radius, color="#808080", 
                     filled=True):
        """ Draw a circle at the given center position with the given radius
        and color. It will be filled, without a stroke, by default.
        @param x_center The X coordinate of the center in pixels
        @param y_center The Y coordinate of the center in pixels
        @param radius The circle's radius in pixels
        @param color The color with which to draw the circle
        @param filled Whether the circle is drawn filled with no stroke, if
               @c True, or as a stroke ring with no fill, if @c False
        """
        self.send ('<circle cx="{:d}" cy="{:d}" r="{:d}" '.format (
                   x_center, y_center, radius))
        if filled:
            self.send ('fill="{:s}" />'.format (color))
        else:
            self.send ('stroke="{:s}" stroke-width="{:d}" />'.format (
                    color, 1 if radius < 4 else radius // 3))


    def send (self, a_string):
        """ Send a string or a bytearray to whatever file or network port is
        used to get the data to a display device. If the data is a bunch of
        bytes, convert it to a string before sending it. 
        @param a_string The string or byte array to be sent
        """
        if self.sender is not None:
            if type (a_string) is str:
                self.sender (a_string)
            elif type (a_string) is bytes:
                self.sender (a_string.decode ('UTF-8'))   # Bytes to string
            else:
                print ("BAD send(): " + str (a_string))


# -----------------------------------------------------------------------------

class LineBreak:
    """ This class implements a newline on the dashboard. When asked to draw
    itself, it just sends an HTML line break, @c <br>.
    """

    def __init__ (self):
        """ It doesn't take much to initialize a line break, so just set up the
        callable by which we send characters to the HTML client as nothing; the
        dashboard will set the sender to something when this object is added
        to the dashboard's widget list.
        """
        self.sender = None


    def draw (self):
        """ Render the line break by sending the correct HTML command.
        """
        if self.sender is not None:
            self.sender ("<br>")


