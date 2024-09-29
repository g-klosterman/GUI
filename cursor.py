import pygame.event

import UIElement

class Cursor(UIElement):

    def __init__(self):
        self.clickable = True
        self.draggable = True


    def handle_click(self):



    def handle_keypress(self, keypress_event):
        """
        Handle a keypress while the UI element is focused.
        May be implemented to unconditionally return False if the UI element does not accept keyboard input
        :param keypress_event:  A Pygame event encapsulating a keypress
        :return:                Boolean indicating the success of the operation
        """
        pass