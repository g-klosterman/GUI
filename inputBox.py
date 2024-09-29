import pygame
from UIElement import *

""" InputBox class
Represents a text input box compatible with the Pygame engine.
Allows the user to input text into the game using keyboard input.

"""


class InputBox(UIElement):

    def __init__(self, pos, size):
        """
        Initialize a text input box to be placed in a Pygame environment and receive text input from the user.

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
        self.placeholder_color = self._COLOR_PLACEHOLDER_DEFAULT
        self.base_font = pygame.font.Font(None, 32)

        # Interaction parameters
        self.clickable = True
        self.typable = True

        # Value parameters
        self.text = ''
        self.placeholder = 'Give me a placeholder'

    def draw_self(self, surf):
        """
        Draw the input box on the given Surface.

        :param surf:    A pygame Surface on which to draw the input box
        :return:
        """

        # Make a text label with the input box's placeholder text
        text_surface = self.base_font.render(self.placeholder, True, self.placeholder_color)

        # If there is text in the input box, replace the placeholder text with it
        if len(self.text) > 0:
            text_surface = self.base_font.render(self.text, True, self.text_color)

        # Adjust the width of the text box so longer input will not visually overflow
        self.rect.w = max(100, text_surface.get_width() + 10)

        # Draw a rectangle for the input box and a black frame around it
        back_color = self.color_unfocused
        if self.focused:
            back_color = self.color_focused
        pygame.draw.rect(surf, back_color, self.rect)
        pygame.draw.rect(surf, self.border_color, self.rect, width=2)

        # Render the text on the screen on top of the input box
        surf.blit(text_surface, (self.rect.x + 5, self.rect.y + 5))

    def handle_click(self):
        self.focus()

        return UIElement.ReturnCode.HANDLED

    def handle_keypress(self, keypress_event):

        # Check for a Backspace
        if keypress_event.key == pygame.K_BACKSPACE:

            # Drop the last character from the input box's contents
            self.text = self.text[:-1]
            return UIElement.ReturnCode.HANDLED

        # Check for a Tab
        elif keypress_event.key == pygame.K_TAB:

            self.defocus()   # Tab always deselects a text box
            return UIElement.ReturnCode.FOCUS_NEXT_ELEMENT

        # Check for an Enter/Return
        elif keypress_event.key == pygame.K_RETURN:

            # Up to the programmer to determine if return should deselect the text box, so don't deactivate here
            return UIElement.ReturnCode.ENTER

        # Check for Escape
        elif keypress_event.key == pygame.K_ESCAPE:

            self.defocus()   # Escape always deselects a text box
            return UIElement.ReturnCode.DEFOCUS_ME

        # Check if the input key has an equivalent unicode character
        elif keypress_event.unicode:

            # Only allow printable input
            character = keypress_event.unicode
            if character.isprintable():
                self.text += keypress_event.unicode

                return UIElement.ReturnCode.HANDLED

        return UIElement.ReturnCode.COULD_NOT_HANDLE

    def toggle_focused(self):
        """
        Toggle the active state of the box.

        :return:    The active state of the box
        """

        self.focused = ~self.focused

        return self.focused
