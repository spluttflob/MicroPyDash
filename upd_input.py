""" @file upd_input.py
      This file contains input widgets for a MicroPython dashboard. 
        
      References for buttons: @c
      * https://randomnerdtutorials.com/esp32-esp8266-micropython-web-server/
      * https://stackoverflow.com/questions/2906582/
          how-to-create-an-html-button-that-acts-like-a-link

    @author JR Ridgely
    
    @date 2020-Feb-09 JRR Original file

    @copyright (c) 2020 by JR Ridgely and released under the LGPL V3.
"""


class Button:
    """ This class implements a pushbutton control to be implemented in HTML.
    When the button is pushed, the given callable is called.
    """

    ## A serial number for buttons, used to make a unique link for this one
    serial_number = 0

    ## The font size for all buttons
    font_size = 16

    ## The background color for all buttons on the page
    background_color = "#006060"

    ## The text color for all buttons on the page
    text_color = "white"

    ## The callable which sends characters to an HTML client
    sender = None


    def __init__ (self, callback, text): 
        """ Initialize a button object with the given text and optional colors.
        @param callback The function to be called when the button is pushed
        @param text The text to be displayed for the button
        """
        self.callback = callback
        self.text = text

        self.serial_number = Button.serial_number
        Button.serial_number += 1


    def buttons_present ():
        """ If any buttons have been created, return @c True; if no buttons
        have been created, return @c False. As a static method, this method
        doesn't have a @c self parameter.
        @returns @c True if any buttons are on the page, otherwise @c False
        """
        return Button.serial_number > 0


    def draw (self):
        """ Display this button by using the sender to display the HTML which
        implements the button.
        """
        self.send ('<a href="/?blah" class="button">{:s}</a>\n'.format (
                   self.text))


    def send (self, a_string=None):
        """ Send a string or a bytearray to whatever file or network port is
        used to get the data to a display device. If the data is a bunch of
        bytes, convert it to a string before sending it. 
        @param a_string The string or byte array to be sent
        """
        if a_string is None:
            print ("Blank string")
        else:
            if Button.sender is not None:
                if type (a_string) is str:
                    Button.sender (a_string)
                elif type (a_string) is bytes:
                    Button.sender (a_string.decode ('UTF-8'))   # Bytes to string


    @property
    def sender (self):
        """ What sends characters?
        """
        return Button.sender
    
    @sender.setter
    def sender (self, new_sender):
        """ Set the callable which sends characters to an HTML client.
        """
        Button.sender = new_sender



