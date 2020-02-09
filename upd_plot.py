""" @file upd_plot.py
        This file contains a plotting widget for use with the MicroPython
        dashboard. The widget can draw static plots, where a set of arrays of
        X and Y data are plotted. It can also draw scrolling plots, where data
        is given as sets of points, each at one time (the X coordinate), and
        buffers are used to save recent points and throw away old points when
        the buffers become full. 

    @author JR Ridgely
    
    @date 2020-Jan-25 JRR Original file, based somewhat on the meter

    @copyright (c) 2020 by JR Ridgely and released under the LGPL V3.
"""

import upd_base
import axis_scaler
import plot_trace


class Plot (upd_base.SVG_item):
    """ This class implements a static or scrolling plot display on an HTML 
    page. The plot is drawn using SVG graphics using minimal resources. The 
    plot can be static or scrolling. A static plot is drawn once, showing all 
    the data given in a set of arrays; a scrolling plot is given data one by 
    one, adding the most recent data to the plot and throwing out the oldest 
    data if the plot arrays are full.

    @b Static @b Plots
    To create a static plot, create the plot object with parameter @c scrolling
    unset or equal to @c None; fill some arrays with data and pass the arrays
    to the plot's @b set_data() method. When the dashboard is redrawn, the plot
    will display the given data:
    @code
    plot0 = upd_plot.Plot (0, 0, 420, 320, title="It's a Plot", 
                                   num_traces=2)
    dash.add_widget (plot0)
    ...
    x_data = [t / 55 for t in range (120)]
    x_scaled = [t * 200 for t in x_data]
    y0_data = [x * x - x * x * x / 2.1 for x in x_data]
    y1_data = [math.sin (6.283 * t) for t in x_data]
    plot0.set_data (x_scaled, [y0_data, y1_data])
    ...
    @endcode

    @b Scrolling @b Plots
    To create a scrolling plot, create the plot object with parameter 
    @c scrolling equal to an integer which is the number of points in the plot
    buffer. Then periodically pass data points, one @a x coordinate at a time,
    to the plot, by calling @c add_data(). 
    @code
    # Code snippet coming when I've got this thing working
    @endcode
    """

    def __init__ (self, pos_x, pos_y, width, height, title="Plot",
                  num_traces=1, border=False,
                  min_x=0.0, max_x=100.0, min_y=-1.0, max_y=1.0, 
                  x_label="Time", y_label="Something", autoscale=True,
                  background_color="#181818", grid_color="#505050", 
                  scrolling=None):
        """  Create a plotter object. 
        @param pos_x The X coordinate in pixels of the upper left corner
        @param pos_y The Y coordinate in pixels of the upper left corner
        @param width The width on the screen
        @param height The height on the screen
        @param title A title to show what's measured and hopefully units
        @param num_traces The number of data traces to be displayed
        @param border Whether or not to draw a border rectangle
        @param min_x The initial X axis minimum
        @param max_x The initial X axis maximum
        @param min_y The initial Y axis minimum
        @param max_y The initial Y axis maximum
        @param x_label Text displayed along the X axis
        @param y_label Text displayed along the Y axis
        @param autoscale Whether to automatically scale the axes to the data
        @param grid_color The color for gridlines on the plot, or @c None if no
               grid lines are to be drawn
        @param background_color The color of the plot area background
        @param grid_color The color of the grid lines, or @c None for no grid
        @param scrolling The number of points to hold in the plot data buffers
               which are used to make a scrolling (usually real-time) plot
        """
        super ().__init__ (pos_x, pos_y, width, height, border)

        self.title = title
        self.min_x = min_x
        self.max_x = max_x
        self.min_y = min_y
        self.max_y = max_y
        self.autoscale = autoscale
        self.x_label = x_label
        self.y_label = y_label
        self.background_color = background_color
        self.grid_color = grid_color
        self.scrolling = scrolling

        # Create plot traces using default parameters that can be changed later
        self.xdata = None
        self.traces = [plot_trace.PlotTrace () for count in range (num_traces)]

        # Check if we need to create scrolling buffers
        if scrolling is not None:
            self.xdata = plot_trace.PlotBuffer (int (self.scrolling), 'f')
            for trace in self.traces:
                trace.the_data = plot_trace.PlotBuffer (int (self.scrolling), 
                                                        'f')

        # Compute sizes of internal components
        self.compute_sizes ()

        # Create an axis scaler object to figure out where to put ticks
        self.ticker = axis_scaler.AxisScaler (self.min_x, self.max_x,
                                              max_ticks=5)


    def add_data (self, x_coord, y_coords):
        """ Add a set of data at one X coordinate to a scrolling plot. There 
        may be one or more Y coordinates; each will represent a trace. The 
        number of Y data must match the number of traces in the plot. This 
        method must not be used for static (non-scrolling) plots.
        @param x_coord One point of X data
        @param y_coords An iterable containing one or more points of Y data,
               one point per trace
        """
        self.xdata.put (x_coord)
        for y_coord, trace in zip (y_coords, self.traces):
            trace.put (y_coord)


    def set_data (self, xdata_source, ydata_sources):
        """ Tell the plotter to use the given source of data for subsequent 
        plotting. There must be one iterable which supplies X data and an 
        iterable of Y data items, each of those Y data items being an iterable
        itself. The number of elements in the ydata_sources iterable must match
        the number of traces in the plot. 
        @param xdata_source An iterable containing the X coordinates of points
        @param ydata_source An iterable (such as a list) of iterables, each of
               which has Y coordinates for one trace in the plot
        """
        # Set X data from the first element in the list
        self.xdata = xdata_source

        # Set Y data from each element after that
        for (source, trace) in zip (ydata_sources, self.traces):
            trace.data = source


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


    def draw_grid (self):
        """ Compute attractive locations for grid lines and draw the lines on
        the plot, unless @c self.grid_color is @c None, in which case show tick
        labels (the numbers) but no grid lines. 
        """
        # The vertical grid lines are drawn at each X position
        y_of_x_nums = self.abx_top + self.abx_height + self.tick_label_size
        for x_tick in self.ticker.generate_ticks (self.min_x, self.max_x, 
                                                  max_ticks=7):
            pix = self.x2pixels (x_tick)
            if self.grid_color is not None:
                self.draw_line (pix, self.abx_top + self.abx_height, 
                            pix, self.abx_top, color=self.grid_color, width=1)
            # Always draw tick labels
            self.draw_text ("{:g}".format (x_tick), pix, y_of_x_nums, 
                            anchor='middle', size=self.tick_label_size)

        for y_tick in self.ticker.generate_ticks (self.min_y, self.max_y, 
                                                  max_ticks=5):
            pix = self.y2pixels (y_tick)
            if self.grid_color is not None:
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
            self.autoscale_x ()
            self.autoscale_y ()

        self.header ()

        # Draw a box around the plot area and highlight (or low-light) the area
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
        self.draw_grid ()

        # Plot the data (finally)
        self.plot_data ()

        self.footer ()


    def autoscale_x (self):
        """ This method looks through the X data and scales the X axis to fit. 
        """
        if self.xdata and len (self.xdata) > 1:
            # Scale the X axis with the minimum and maximum of the X array.
            # We need to re-scale when new data is added to the scrolling plot,
            # as otherwise the plot will always begin at zero
            min_val, max_val = self.find_extremes (self.xdata, all_new=True)
            if min_val is not None and max_val is not None:
                self.min_x = min_val
                self.max_x = max_val


    def autoscale_y (self):
        """ This method autoscales the Y axis only. It can be useful when
        scrolling the time axis, which doesn't scroll the X axis.
        """
        if self.traces and len (self.xdata) > 1:
            # Scale the Y axis to fit the most extreme Y data we can find
            min_val = None
            max_val = None
            for axis in self.traces:
                extrema = self.find_extremes (axis.data)
                if extrema is not None:
                    temp_min, temp_max = extrema
                    if min_val is None or temp_min < min_val:
                        min_val = temp_min
                    if max_val is None or temp_max > max_val:
                        max_val = temp_max
            if min_val is not None and max_val is not None:
                self.min_y = min_val
                self.max_y = max_val


    def find_extremes (self, one_axis, all_new=False):
        """ This method looks through one axis (X or one of the Y traces) to
        find the minimum and maximum values.
        @param one_axis A single array of data with one X or Y axis's numbers
        @param all_new Whether to ignore old values for extremes and find the
               minimum and maximum of current data, not all data ever
        @return A tuple containing the minimum and maximum values found or
                @c None if there's no data available
        """
        if one_axis:
            if type (one_axis) == plot_trace.PlotBuffer:
                if all_new:
                    return (min (one_axis.data), max (one_axis.data))
                else:
                    max_val = one_axis.max_val
                    min_val = one_axis.min_val
                    if max_val is not None and min_val is not None:
                        return (min_val, max_val)
            else:
                return (min (one_axis), max (one_axis))
        return None


    def plot_data (self):
        """ Clear the plot area, then plot the previously given data. 
        """
        # Go through this procedure for each trace in the set of traces
        for trace in self.traces:

            x_prev = None                # To draw line segments between points
            y_prev = None

            for x, y in zip (self.xdata, trace.data):
                x_pixels = self.x2pixels (x)
                y_pixels = self.y2pixels (y)
                if x_prev is not None and trace.lines:
                    self.draw_line (x_prev, y_prev, x_pixels, y_pixels, 
                                    trace.color, trace.line_width)
                x_prev = x_pixels
                y_prev = y_pixels

                if trace.markers:
                    self.draw_circle (x_pixels, y_pixels, trace.marker_size, 
                                      color=trace.color, filled=True)




