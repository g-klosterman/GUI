import abc

from enum import Enum

import pygame


class UIElement(abc.ABC):

    _COLOR_FOCUSED_DEFAULT = pygame.Color('khaki2')
    _COLOR_UNFOCUSED_DEFAULT = pygame.Color('white')
    _COLOR_BORDER_DEFAULT = pygame.Color('black')
    _COLOR_VALUE_DEFAULT = pygame.Color('black')
    _COLOR_PLACEHOLDER_DEFAULT = pygame.Color(200, 200, 200)

    def __init__(self):
        self.focused = False
        self.clickable = False
        self.draggable = False
        self.typable = False
        self.focusable = True

    @abc.abstractmethod
    def handle_click(self):
        pass

    @abc.abstractmethod
    def handle_keypress(self, keypress_event):
        """
        Handle a keypress while the UI element is focused.
        May be implemented to unconditionally return False if the UI element does not accept keyboard input
        :param keypress_event:  A Pygame event encapsulating a keypress
        :return:                Boolean indicating the success of the operation
        """
        pass

    def defocus(self):
        """
        Deactivate the input box by changing its color to the inactive color.

        Returns:
            None
        """

        self.focused = False
        return self.focused

    def focus(self):
        """
        Activate the input box by changing its color to the active color.

        Returns:
            None
        """

        self.focused = True
        return self.focused

    def toggle_focused(self):
        """
        Toggle the active state of the box.

        :return:    The active state of the box
        """

        self.focused = ~self.focused

        return self.focused

    """
    ReturnCode enum
    Negative codes are for cases where an event cannot be handled.
    Positive codes indicate the calling event handler must take additional action.
    HANDLED indicates no further action is needed to handle the event.
    """
    class ReturnCode(Enum):
        HANDLED = 0
        FOCUS_NEXT_ELEMENT = 1
        ENTER = 2
        DEFOCUS_ME = 3
        COULD_NOT_HANDLE = -1

