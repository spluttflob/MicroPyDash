""" @file axis_scaler.py
        This file contains a class which finds fairly "nice looking" locations
        for ticks and/or gridlines on the axes of a plot. 

    @author JR Ridgely, who modified it from stuff found at inneka.com blog

    @date 2020-Jan-26 This Pythonic version created, based on a Java class

    @copyright (c) 2020 by JR Ridgely and released under the Lesser GNU Public
        License, Version 3. This file contains material which was posted at
        inneka.com under what appears to be a restrictive copyright, though the
        material at that site was derived from a published book by Glassner, so
        it is not reasonable that the blog author has full copyright control of
        the displayed works and all derivatives. Furthermore, this program is
        highly modified from that displayed on the blog. Finally, no attempt is
        being made by the author of this version to profit from this program.
"""
import math


class AxisScaler:
    """ This class creates a "nice" scaling of ticks on an axis. 
    This class was modified (and made more Pythonic) from examples at
    https://inneka.com/programming/java/nice-label-algorithm-for-charts-with-minimum-ticks/
    """

    def __init__ (self, min_value, max_value, max_ticks=5):
        """ Instantiates a new instance of the AxisScaler class.
        @param min The minimum data point on the axis
        @param max The maximum data point on the axis
        @param max_tick_marks The maximum number of ticks we want on an axis
        """
        self.min_point = min_value
        self.max_point = max_value
        self.max_n_ticks = max_ticks

        self.calculate ()


    def calculate (self):
        """ Calculate and update values for tick spacing and nice minimum and 
        maximum data points on the axis.
        """
        self.vrange = self.niceNum (self.max_point - self.min_point, False)
        self.tickSpacing = \
            self.niceNum (self.vrange / (self.max_n_ticks - 1), True)
        self.niceMin = \
            math.floor (self.min_point / self.tickSpacing) * self.tickSpacing
        self.niceMax = \
            math.ceil (self.max_point / self.tickSpacing) * self.tickSpacing


    def niceNum (self, vrange, do_round = True):
        """ Returns a "nice" number approximately equal to #c vrange. Rounds 
        the number if @c round == @c True. Takes the ceiling if 
        @c do_round == @c False.
        @param vrange The data range
        @param do_round Whether to round the result
        @return a "nice" Number to be used for the data range
        """
        exponent = math.floor (math.log (vrange, 10))
        fraction = vrange / (10 ** exponent)

        if do_round:
            if fraction < 1.5:
                niceFraction = 1
            elif fraction < 3:
                niceFraction = 2
            elif fraction < 7:
                niceFraction = 5
            else:
                niceFraction = 10
        else:
            if fraction <= 1:
                niceFraction = 1
            elif fraction <= 2:
                niceFraction = 2
            elif fraction <= 5:
                niceFraction = 5
            else:
                niceFraction = 10

        return niceFraction * (10 ** exponent)


    def generate_ticks (self, min_point, max_point, max_ticks=None):
        """ This generator produces a set of tick locations over which the
        calling routine can iterate as it creates ticks and/or grid lines,
        as in <code>for tick_pos in scaler.generate_ticks (xmin, xmax):</code>
        @param min_point The minimum data point on the axis
        @param max_point The maximum data point on the axis
        @param max_ticks The maximum number of ticks which is OK, or @c None
               if we're using the value already set
        """
        self.min_point = min_point
        self.max_point = max_point
        if max_ticks is not None:
            self.max_n_ticks = max_ticks
        self.calculate ()

        tick_pos = self.niceMin
        while tick_pos <= self.niceMax:
            yield tick_pos
            tick_pos += self.tickSpacing


    @property
    def max_ticks (self):
        """ Get the maximum number of ticks with which we're comfortable.
        """
        return self.max_n_ticks

    @max_ticks.setter
    def max_ticks (self, num_ticks):
        """ Sets the maximum number of tick marks with which we're comfortable.
        @param num_ticks The maximum number of tick marks for the axis
        """
        self.max_n_ticks = num_ticks
        self.calculate ()


# =============================================================================

if __name__ == "__main__":

    def test_scaler (xmin, xmax, max_ticks):
        axie = AxisScaler (xmin, xmax, max_ticks=max_ticks)
        print ("Scale: {:g} to {:g} --> ".format (xmin, xmax), end="")
        for tick in axie.generate_ticks (xmin, xmax):
            print ("{:g},".format (tick), end="")
        print ("")

    test_scaler (0.0, 4.5, max_ticks=4)
    test_scaler (-100.0, 43.75, max_ticks=6)
    test_scaler (54.0, 64.5, max_ticks=10)
    test_scaler (-20.0, -10.0, max_ticks=5)
    test_scaler (0.0, 4444.5, max_ticks=7)
    test_scaler (-0.01, 400.5, max_ticks=5)


