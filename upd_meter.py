""" @file upd_meter.py
        This file contains a panel meter widget for use with the MicroPython
        dashboard. 

    @author JR Ridgely
    
    @date 2020-Jan-25 JRR Extracted from micropydash test program
        
    @copyright (c) 2020 by JR Ridgely and released under the LGPL V3.
"""

import upd_base


class Meter (upd_base.SVG_item):
    """ This class implements a panel meter like display on an HTML page.
    The meter is drawn using SVG graphics.
    """

    def __init__ (self, pos_x, pos_y, width, height, label="Meter", units = "", 
                  text_size=24, min_val=0, max_val=10, border=False, 
                  arc_angle=160, full_color="#808000", empty_color="#303030", 
                  needle_color="#FFFFFF"):
        """  Create a panel meter object. 
        @param pos_x The X coordinate in pixels of the upper left corner
        @param pos_y The Y coordinate in pixels of the upper left corner
        @param width The width on the screen
        @param height The height on the screen
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
        super ().__init__ (pos_x, pos_y, width, height, border)

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
                   upd_base.svg_arc (x_center, y_center,
                                     arc_radius,
                                     end_angle,
                                     needle_angle)))
        self.send ('stroke="{:s}" stroke-width="{:d}" />\n'.format (
                   self.empty_color, self.height // 8))

        # Next the filled up portion of the arc
        self.send ('<path id="arc0" d="{:s}" fill="none" '.format (
                   upd_base.svg_arc (x_center, y_center,
                                     arc_radius,
                                     needle_angle,
                                     start_angle)))
        self.send ('stroke="{:s}" stroke-width="{:d}" />\n'.format (
                self.full_color, self.height // 8))

        # Draw the needle
        tip = upd_base.polar2cartesian (x_center, y_center, 
                                        arc_radius * 1.3, needle_angle)
        base_high = upd_base.polar2cartesian (x_center, y_center, 
                                     arc_radius * 0.7, needle_angle + 5)
        base_low = upd_base.polar2cartesian (x_center, y_center, 
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



