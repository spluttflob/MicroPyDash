""" @file plot_trace.py
        This file contains classes which manage traces (sets of data from which
        lines and/or collections of markers can be drawn) on plots.  One class,
        @c PlotTrace, manages style data and keeps a reference to an iterable
        containing data. Another class, @c PlotBuffer, implements a circular 
        buffer which allows data to be read in the way that would be needed to 
        plot the data -- this is handy for implementing scrolling plots. 

    @author jr
    
    @date Sat Jan 25 20:22:00 2020
        
"""
import array


class PlotTrace:
    """ This class holds information about a data trace on a plot such as line
    and/or marker type, color, and a reference to an iterable holding data. 
    """
    ## A set of colors to be automatically assigned if trace colors aren't
    #  explicitly called out. 
    TRACE_COLORS = ("yellow", "cyan", "red", "green", "#7070FF")

    ## A serial number for traces, used to select automatically assigned colors
    serial_number = 0

    def __init__ (self, data=None, color=None, lines=False, markers=True,
                  line_width=2, marker_size=3):
        """ Initialize the trace object. In addition to setting up a buffer for
        the data (as long as size is true), record the style of the trace.
        @param data An iterable (@c list, @c array.array, @c PlotBuffer, 
               @a etc.) holding data for this trace
        @param color The color in which lines or markers will be shown
        @param lines Whether lines will be drawn between data points
        @param markers Whether markers will be drawn at each data point
        @param line_width The width of lines to be drawn
        @param marker_size The radius of marker dots to be drawn
        """
        self.color = PlotTrace.TRACE_COLORS[PlotTrace.serial_number 
                                            % len (PlotTrace.TRACE_COLORS)]
        PlotTrace.serial_number += 1

        self.lines = lines
        self.markers = markers
        self.line_width = line_width
        self.marker_size = marker_size

        self.the_data = data


    def scrolling (self, size, type_code="f"):
        """ If this plot trace is going to be used for a real-time scrolling
        plot, create a @c PlotBuffer to hold the data as it arrives.
        @param size The size of the buffer which will hold data, or @c None if
               we're turning off the plot buffer for some reason
        """
        if size is None:
            self.the_data = None
        else:
            self.the_data = PlotBuffer (size, type_code)


    def put (self, data):
        """ Put data into the plot buffer associated with this trace. There 
        must @a be a plot buffer of the sort used to make scrolling plots; 
        static plots won't use this method.
        """
        self.the_data.put (data)


    @property
    def data (self):
        """ This method returns the iterable which holds the Y coordinates of
        data to be plotted in this trace.
        @return The iterable with this trace's Y data, or @c None if there 
                isn't any
        """
        return self.the_data

    
    @data.setter
    def data (self, data):
        """ This method configures the given iterable as holding the data of
        this plot trace. If plotting a static plot from existing arrays, just
        set each trace X, Y0, Y1, @a etc. using this method. If making a
        scrolling plot, the use of @c class @c PlotBuffer is recommended.
        """
        self.the_data = data


# -----------------------------------------------------------------------------

class PlotBuffer:
    """ This class implements a circular buffer whose data can be read as 
    needed to generate real-time plots. It also keeps track of maximum and 
    minimum data to help with autoscaling. 
    """

    def __init__ (self, size, type_code="f"):
        """ Initialize the plot buffer, including creation of an @c array.array
        which holds the data and indices with which to read and write it.
        @param size The number of elements in the buffer
        @param type_code An @c array.array code for the type of data stored
        """
        # If a nonzero size is specified, create the data array
        if size is not None and size > 0:
            self.data = array.array (type_code, [0 for x in range (size)])
        else:
            self.data = None

        self.size = size
        self.index_put = 0
        self.index_get = 0
        self.count = 0
        self.max_val = None
        self.min_val = None


    def put (self, value):
        """ Put an item into the buffer. Old data will be overwritten if the
        buffer is full. If there is no buffer, just keep track of the minimum
        and maximum values.
        @param value The item to be entered into the buffer. It must be
               convertible into the correct data type
        """
        # Set the maximum and/or minimum values as necessary
        if self.max_val is None or value > self.max_val:
            self.max_val = value
        if self.min_val is None or value < self.min_val:
            self.min_val = value

        # If there's no buffer, bail out now
        if not self.data:
            return

        # Insert data and move the write pointer to the next location
        self.data[self.index_put] = value
        self.index_put = (self.index_put + 1) % self.size

        # In case of overflow, move the read pointer
        if self.count >= self.size:
            self.index_get = (self.index_get + 1) % self.size
        else:
            self.count += 1


    def get (self):
        """ Read an item from the buffer, moving the read pointer so as to
        empty that item from the buffer. 
        @return The item which was read, or @c None if the buffer is empty
        """
        if not self.data or self.count <= 0:       # No buffer or it's empty
            return None
        else:
            self.count -= 1
            value = self.data[self.index_get]
            self.index_get = (self.index_get + 1) % self.size
            return value


    def __iter__ (self):
        """ This generator allows all the data which is in the buffer to be
        read from it.
        """
        if not self.data:
            return

        index_get = self.index_get
        for count in range (self.count):
            value = self.data[index_get]
            index_get = (index_get + 1) % self.size
            yield value


    @property
    def max_value (self):
        """ Returns the maximum value in the buffer, or @c None if it's empty.
        @return The value of the largest number in the buffer
        """
        return self.max_val


    @property
    def min_value (self):
        """ Returns the minimum value in the buffer, or @c None if it's empty.
        @return The value of the smallest number in the buffer
        """
        return self.min_val


    def __len__ (self):
        """ This overloaded length operator tells how many items are currently
        available in the buffer.
        @return The number of items available in the buffer
        """
        return self.count


#    def __getitem__ (self, index):
#        """ This overloaded index operator returns the index-th item from the
#        set of items available in the buffer. If one asks for an item whose
#        index doesn't represent an available item, an @c IndexError is raised.
#        @param index The index of the item to be retreived (but not removed)
#        """
#        raise NameError ("Implemementing [] is on the TODO list")


# =============================================================================

if __name__ == "__main__":

    buffy = PlotBuffer (5, type_code='h')        # Kind of obvious

    for count in range (20):
        print (buffy.data, " --> [", buffy.count, "]  ", end="")
        for value in buffy.peek_all ():
            print (value, " ", end="")
        print ("")
        buffy.put (count + 1)
    print ("")

    for count in range (10):
        print (buffy.data, " --> ", buffy.get (), " | ", end="")
        for value in buffy.generate_points ():
            print (value, " ", end="")
        print ("")

