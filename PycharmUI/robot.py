from PycharmUI.UIElement import UIElement
import pygame


class Robot(UIElement):

    def __init__(self, pos, size, bot_type, name):
        super().__init__(pos, size)
        self.bot_type = bot_type
        self.name = name

        self.image = pygame.transform.scale(pygame.image.load('assets/' + str(self.name) + '.png'), (50, 50))

    def handle_click(self):
        pass

    def handle_keypress(self, keypress_event):
        pass

    def draw_self(self, surf):
        """
        Draw the Robot on the given Surface.

        :param surf:    A pygame Surface on which to draw the Robot
        :return:
        """

        text_surface = self.base_font.render(self.name, True, self.text_color)

        # Draw a rectangle for the input box and a black frame around it
        #back_color = self.color_unfocused
        #if self.focused:
            #back_color = self.color_focused
        #pygame.draw.rect(surf, back_color, self.rect)
        #pygame.draw.rect(surf, self.border_color, self.rect, width=2)

        surf.blit(self.image, self.rect)

        # Render the text on the screen on top of the input box
        surf.blit(text_surface, (self.rect.x + 5, self.rect.y + 5))
