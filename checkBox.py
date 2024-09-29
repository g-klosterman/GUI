import pygame
from UIElement import *

""" CheckBox class
Represents a text checkbox compatible with the Pygame engine.
Allows the user to input text into the game using keyboard input.

"""


class CheckBox(UIElement):

    # Colors indicate whether an checkbox is in focus or not
    _COLOR_ACTIVE_DEFAULT = pygame.Color('khaki2')
    _COLOR_INACTIVE_DEFAULT = pygame.Color('white')
    _COLOR_BORDER_DEFAULT = pygame.Color('black')
    _COLOR_TEXT_DEFAULT = pygame.Color('black')

    def __init__(self, pos, size):
        """
        Initialize a text checkbox to be placed in a Pygame environment and receive text input from the user.

        Returns:
            None
        """

        super().__init__()
        self.rect = pygame.Rect(pos, size)

        # Style parameters
        self.color_focused = UIElement._COLOR_FOCUSED_DEFAULT
        self.color_unfocused = UIElement._COLOR_UNFOCUSED_DEFAULT

        self.border_color = UIElement._COLOR_BORDER_DEFAULT
        self.text_color = UIElement._COLOR_VALUE_DEFAULT
        self.base_font = pygame.font.Font(None, 32)

        # Interaction parameters
        self.clickable = True
        self.typable = True

        # Value parameters
        self.checked = False

    def draw_self(self, surf):
        """
        Draw the checkbox on the given Surface.

        :param surf:    A pygame Surface on which to draw the checkbox
        :return:
        """

        # Draw a rectangle for the checkbox and a black frame around it
        back_color = self.color_unfocused
        if self.focused:
            back_color = self.color_focused
        pygame.draw.rect(surf, back_color, self.rect)
        pygame.draw.rect(surf, self.border_color, self.rect, width=2)

        # Make a text label with an X for a checkmark
        if self.checked:
            text_surface = self.base_font.render('X', True, self.text_color)

            # Render the text on the screen on top of the text box
            surf.blit(text_surface, (self.rect.x + 5, self.rect.y + 5))

    def handle_click(self):
        self.focus()
        self.toggle_checked()

        return UIElement.ReturnCode.HANDLED

    def handle_keypress(self, keypress_event):

        # Check for a Backspace or Delete
        if keypress_event.key == pygame.K_BACKSPACE or keypress_event.key == pygame.K_DELETE:
            self.checked = False

            return UIElement.ReturnCode.HANDLED

        # Check for a Tab
        elif keypress_event.key == pygame.K_TAB:

            self.defocus()   # Tab always deselects a text box
            return UIElement.ReturnCode.FOCUS_NEXT_ELEMENT

        # Check for an Enter/Return or Space
        elif keypress_event.key == pygame.K_RETURN or keypress_event.key == pygame.K_SPACE:
            self.toggle_checked()

            return UIElement.ReturnCode.HANDLED

        # Check for Escape
        elif keypress_event.key == pygame.K_ESCAPE:
            self.focus()   # Escape always deselects a text box
            return UIElement.ReturnCode.DEFOCUS_ME

        return UIElement.ReturnCode.COULD_NOT_HANDLE

    def toggle_checked(self):

        self.checked = ~self.checked
