""" @file upd_plot.py
        This file contains a plotting widget for use with the MicroPython
        dashboard. 

    @author JR Ridgely
    
    @date 2020-Jan-25 JRR Original file, based somewhat on the meter

    @copyright (c) 2020 by JR Ridgely and released under the LGPL V3.
"""

import upd_base
import axis_scaler
import plot_buffer


class Trace (plot_buffer.PlotBuffer):
    """ This class extends a circular buffer to also hold information about a
    data trace on the plot such as line and/or marker type and color. 
    """

    def __init__ (self, size, color="#00F0F0", lines=False, markers=True,
                  type_code="f"):
        """ Initialize the trace object. In addition to setting up a buffer for
        the data (as long as size is true), record the style of the trace.
        @param size The size of the buffer in which this object stores data; if
               given as @c None or zero, no buffer is created
        @param color The color in which lines or markers will be shown
        @param lines Whether lines will be drawn between data points
        @param markers Whether markers will be drawn at each data point
        @param type_code An @c array.array code for the type of data stored
        """
        super ().__init__ (size, type_code)

        self.color = color
        self.lines = lines
        self.markers = markers



# -----------------------------------------------------------------------------

class Plot (upd_base.SVG_item):
    """ This class implements a panel meter like display on an HTML page.
    The meter is drawn using SVG graphics.
    """

    def __init__ (self, pos_x, pos_y, width, height, title="Plot", units = "", 
                  traces=1, buffer_size=100, border=False, grid=True,
                  min_x=0.0, max_x=100.0, min_y=-1.0, max_y=1.0, 
                  x_label="Time", y_label="Something", autoscale=True,
                  background_color="#181818", grid_color="#505050", 
                  trace_color="#FFFF00"):
        """  Create a plotter object. 
        @param pos_x The X coordinate in pixels of the upper left corner
        @param pos_y The Y coordinate in pixels of the upper left corner
        @param width The width on the screen
        @param height The height on the screen
        @param title A title to show what's measured and hopefully units
        @param units A string indicating the units of the measurand
        @param traces The number of data traces to be initially displayed
        @param min_x The initial X axis minimum
        @param max_x The initial X axis maximum
        @param min_y The initial Y axis minimum
        @param max_y The initial Y axis maximum
        @param border Whether or not to draw a border rectangle
        @param x_label Text displayed along the X axis
        @param y_label Text displayed along the Y axis
        @param grid_color The color for gridlines on the plot
        @param background_color The color of the plot area background
        @param trace_color The color of the first data trace
        """
        super ().__init__ (pos_x, pos_y, width, height, border)

        self.title = title
        self.units = units
        self.min_x = min_x
        self.max_x = max_x
        self.min_y = min_y
        self.max_y = max_y
        self.autoscale = autoscale
        self.x_label = x_label
        self.y_label = y_label
        self.background_color = background_color
        self.grid = grid
        self.grid_color = grid_color
        self.trace_color = trace_color
        self.traces = traces

#        # Allocate arrays for the horizontal axis and vertical axes
#        self.data = (1 + traces) * [Trace (buffer_size, 'f')]

        # Compute sizes of internal components
        self.compute_sizes ()

        # Create an axis scaler object to figure out where to put ticks
        self.ticker = axis_scaler.AxisScaler (self.min_x, self.max_x,
                                              max_ticks=5)


    def compute_sizes (self):
        """ Use the current values of box width and height to compute the sizes
        of the text and plot axes inside.
        """
        # abx_ means axes box; mgn_left, mgn_top, mgn_bot margins
        self.abx_left = self.width * 10 // 100
        self.abx_top = self.height * 10 // 100
        self.abx_width = (self.width - self.abx_left) * 96 // 100
        self.abx_height = self.height - self.abx_top - self.abx_left

        # Text sizes are scaled with respect to box size
        self.title_size = self.height * 7 // 100
        self.ax_label_size = self.height * 5 // 100
        self.tick_label_size = self.height * 4 // 100


    def x2pixels (self, x):
        """ Convert an X coordinate in the plotted units (time and force units,
        or whatever) into a pixel coordinate of a screen position.
        @param x The X coordinate to be converted
        @returns The pixel coordinate at which the point should be plotted
        """
        return int ((x - self.min_x) * self.abx_width \
                    / (self.max_x - self.min_x)) + self.abx_left


    def y2pixels (self, y):
        """ Convert an X coordinate in the plotted units (time and force units,
        or whatever) into a pixel coordinate of a screen position.
        @param y The Y coordinate to be converted
        @returns The pixel coordinate at which the point should be plotted
        """
        return self.abx_top + self.abx_height - int ((y - self.min_y) 
                                * self.abx_height / (self.max_y - self.min_y))


    def draw_grid (self, gridlines=True):
        """ Compute attractive locations for grid lines and draw the lines on
        the plot.
        @param gridlines Whether to draw grid lines; if @c False grid not shown
        """
        # The vertical grid lines are drawn at each X position
        y_of_x_nums = self.abx_top + self.abx_height + self.tick_label_size
        for x_tick in self.ticker.generate_ticks (self.min_x, self.max_x, 
                                                  max_ticks=7):
            pix = self.x2pixels (x_tick)
            if gridlines:
                self.draw_line (pix, self.abx_top + self.abx_height, 
                            pix, self.abx_top, color=self.grid_color, width=1)
            # Always draw tick labels
            self.draw_text ("{:g}".format (x_tick), pix, y_of_x_nums, 
                            anchor='middle', size=self.tick_label_size)

        for y_tick in self.ticker.generate_ticks (self.min_y, self.max_y, 
                                                  max_ticks=5):
            pix = self.y2pixels (y_tick)
            if gridlines:
                self.draw_line (self.abx_left, pix, 
                                self.abx_left + self.abx_width, pix,
                                color=self.grid_color, width=1)
            self.draw_text ("{:g}".format (y_tick), 
                            self.abx_left - 2, pix, anchor='end', 
                            baseline="middle", size=self.tick_label_size)


    def draw (self):
        """ Draw the plot box by creating its SVG image.
        @param sender A callable which sends strings to a file or web browser
        """
        if self.autoscale:
            self.autoscale_plot ()

        self.header ()

        # Draw a box around the plot area and highlight (lowlight?) the area
        self.send ('<rect x="{:d}" y="{:d}" width="{:d}" height="{:d}" '.format (
                   self.abx_left, self.abx_top,
                   self.abx_width, self.abx_height))
        self.send ('style="stroke:{:s};stroke-width:2;fill:{:s}" />\n'.format (
                   self.grid_color, self.background_color))

        # Draw the plot title and the axis labels
        self.draw_text (self.title, self.width // 2, self.title_size * 10 // 9, 
                        anchor='middle', size=self.title_size)
        self.draw_text (self.x_label, self.width // 2, self.height - 2,
                        anchor='middle', size=self.ax_label_size)
        self.draw_text (self.y_label, 1, self.height // 2,
                        anchor='middle', baseline="hanging", 
                        size=self.ax_label_size, angle=270)

        # Draw ticks and tick labels on the axes
        self.draw_grid (self.grid)

        # Plot the data (finally)
        self.plot_data ()

        self.footer ()


    def add_data (self, data):
        """ Add a set of data at one X coordinate to the plot. There may be one
        or more Y coordinates; each will represent a trace. The number of Y
        data must match the number of traces in the plot.
        @param data An iterable of data, for example [time, speed, velocity]
        """
        if len (data) != self.traces + 1:
            raise ValueError ("Wrong number of data for plot")

        for index in range (len (self.data)):
            self.data[index].put (data[index])


    def set_data (self, data_source):
        """ Tell the plotter to use the given source of data for subsequent 
        plotting. The source must be a list (or tuple, @a etc.) of items, each 
        item being an iterable (array, list, @a etc.) representing X or Y axis
        data. Element 0 is X axis data; elements 1 and higher each represent a
        trace to be plotted. The number of data items must be the number of
        traces for which this plotter is configured plus one.
        """
        if len (data_source) != self.traces + 1:
            raise ValueError ("Need {:d} plot traces plus X-axis".format (
                              self.traces))

        self.data = data_source


    def autoscale_plot (self):
        """ This method looks through the data and scales the plot axes to fit
        it. 
        """
        if self.data:
            # Scale the X axis with the minimum and maximum of the first array
            min_val, max_val = self.auto_one (self.data[0])
            if min_val is not None and max_val is not None:
                self.min_x = min_val
                self.max_x = max_val
            self.autoscale_y ()


    def autoscale_y (self):
        """ This method autoscales the Y axis only. It can be useful when
        scrolling the time axis, which doesn't scroll the X axis.
        """
        if self.data:
            # Scale the Y axis to fit the most extreme Y data we can find
            min_val = None
            max_val = None
            for axis in self.data[1:]:
                temp_min, temp_max = self.auto_one (axis)
                if min_val is None or temp_min < min_val:
                    min_val = temp_min
                if max_val is None or temp_max > max_val:
                    max_val = temp_max
            if min_val is not None and max_val is not None:
                self.min_y = min_val
                self.max_y = max_val


    def auto_one (self, one_axis):
        """ This method looks through one axis (X or one of the Y traces) to
        find the minimum and maximum values.
        @param one_axis A single array of data with one X or Y axis's numbers
        @return A tuple containing the minimum and maximum values found or
                @c None if there's no data available
        """
        if one_axis:
            if type (one_axis) == Trace:
                max_val = one_axis.max_val
                min_val = one_axis.min_val
                if max_val is not None and min_val is not None:
                    return (min_val, max_val)
            else:
                return (min (one_axis), max (one_axis))
        return None


    def plot_data (self):
        """ Clear the plot area, then plot the given data. The number of traces
        in the data must match the number of traces on the plot.
        """
        # Go through this procedure for each trace in the set of traces
        for trace_num in range (1, self.traces + 1):

            # If the data are in regular arrays, there won't be color, etc.
            # data available so just assume something
            if type (self.data[0]) is not Trace:
                plot_color = "#20F0F0"
                plot_lines = True
                plot_markers = True
                plot_width = 1
            else:
                raise ValueError ("Need to get style from Trace")

            x_prev = None                # To draw line segments between points
            y_prev = None

            for x, y in zip (self.data[0], self.data[trace_num]):
                x_pixels = self.x2pixels (x)
                y_pixels = self.y2pixels (y)
                if x_prev is not None and plot_lines:
                    self.draw_line (x_prev, y_prev, x_pixels, y_pixels, 
                                    plot_color, plot_width)
                x_prev = x_pixels
                y_prev = y_pixels

                if plot_markers:
                    self.draw_circle (x_pixels, y_pixels, 3, color=plot_color,
                                      filled=True)




