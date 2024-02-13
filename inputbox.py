import pygame

# Colors indicate whether an input box is in focus or not
color_active = pygame.Color('khaki2')
color_inactive = pygame.Color('white')

""" InputBox class
Represents a text input box compatible with the Pygame engine.
Allows the user to input text into the game using keyboard input.

"""


class InputBox:

    def __init__(self, pos, size):
        """
        Initialize a text input box to be placed in a Pygame environment and receive text input from the user.

        Returns:
            None
        """

        self.rect = pygame.Rect(pos, size)
        self.active = False
        self.color = color_inactive
        self.text = ''
        self.placeholder = 'test'

    def activate(self):
        """
        Activate the input box by changing its color to the active color.

        Returns:
            None
        """

        self.color = color_active

    def deactivate(self):
        """
        Deactivate the input box by changing its color to the inactive color.

        Returns:
            None
        """

        self.color = color_inactive
