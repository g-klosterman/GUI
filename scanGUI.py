import pygame
import sys, math, random
from cameraClient import CameraClient
from inputbox import InputBox # Do not delete, will need this later


# Generate a random RGB color
def random_color():
    levels = range(32, 256, 32) # Possible levels for each color are form 32 to 256 in increments of 32
    return tuple(random.choice(levels) for _ in range(3))


class ScanGUI:

    # Server session constants
    HOST = 'overheadcam'
    PORT = 5000

    # Rendering constants
    FPS = 60
    SCREEN_WIDTH = 1440
    SCREEN_HEIGHT = 720
    FIELD_LENGTH = 90   # Represented as the vertical axis on display, parallel to SCREEN_WIDTH
    FIELD_WIDTH = 46    # Represented as the vertical axis on display, parallel to SCREEN_HEIGHT

    SCALE_X = SCREEN_WIDTH / FIELD_LENGTH
    SCALE_Y = SCREEN_HEIGHT / FIELD_WIDTH



    def __init__(self):
        self.cam_client = CameraClient(ScanGUI.HOST, ScanGUI.PORT)

        # Set the screen size and name for the application

        pygame.init()
        self.screen = pygame.display.set_mode((ScanGUI.SCREEN_WIDTH, ScanGUI.SCREEN_HEIGHT))
        pygame.display.set_caption('Scan & Score')

        ScanGUI.TEXT_FONT = pygame.font.SysFont('Arial', 30)  # AAAAAAAAAAAAAAAAAAAAAAHHHHHHHHHHHHH
        self.clock = pygame.time.Clock()

        # Robots
        self.QB = None
        self.WR1 = None
        self.WR2 = None

        self.reset_field()

    def reset_field(self):
        # Setting size and initial position of drawn rects to represent bots
        self.QB = pygame.rect.Rect(1000, 360, 51, 51)
        self.WR1 = pygame.rect.Rect(300, 200, 51, 51)
        self.WR2 = pygame.rect.Rect(300, 500, 51, 51)

    def draw_text(self, text, font, text_col, x, y):
        # Function for text to be added on screen as an image
        img = font.render(text, True, text_col)
        self.screen.blit(img, (x, y))

    def run(self):

        # Rect used for testing dragging and calculations of magnitude and angle
        rectangle = pygame.rect.Rect(0, 0, 51, 51)
        rectangle_dragging = False

        run = True
        while run:

            points = []
            # Receive the points representing detected bots from the camera server
            points = self.cam_client.receive_points()

            # Fill the screen with a green box and outline it with black and white lines
            self.screen.fill((55, 155, 90))
            pygame.draw.rect(self.screen, 'white', (0, 0, ScanGUI.SCREEN_WIDTH, ScanGUI.SCREEN_HEIGHT), width=20)
            pygame.draw.rect(self.screen, 'black', (0, 0, ScanGUI.SCREEN_WIDTH, ScanGUI.SCREEN_HEIGHT), width=5)

            # Create vertical lines every 15 feet
            line_spacing = 15
            line_location = 0
            for i in range(5):
                line_location += line_spacing * ScanGUI.SCALE_X
                pygame.draw.line(self.screen, 'white', (line_location, 5), (line_location, ScanGUI.SCREEN_HEIGHT - 5), width=20)
                self.draw_text(str(line_spacing * (i + 1)) + "'", ScanGUI.TEXT_FONT, 'black', line_location - 42, 20)
                self.draw_text(str(line_spacing * (i + 1)) + "'", ScanGUI.TEXT_FONT, 'black', 1398 - line_location, 665)

            # Draw squares on screen to represent robots
            pygame.draw.rect(self.screen, 'blue', self.QB)
            pygame.draw.rect(self.screen, 'red', self.WR1)
            pygame.draw.rect(self.screen, 'yellow', self.WR2)
            pygame.draw.rect(self.screen, 'purple', rectangle)

            # Event for dragging purple square on screen
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if rectangle.collidepoint(event.pos):
                            rectangle_dragging = True
                            mouse_x, mouse_y = event.pos
                            offset_x = rectangle.x - mouse_x
                            offset_y = rectangle.y - mouse_y

                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        rectangle_dragging = False

                elif event.type == pygame.MOUSEMOTION:
                    if rectangle_dragging:
                        mouse_x, mouse_y = event.pos
                        rectangle.x = mouse_x + offset_x
                        rectangle.y = mouse_y + offset_y

            # Write cursor position
            x1, y1 = pygame.mouse.get_pos()
            # draw_text('(' + str(x1) + ", " + str(y1) + ')', TEXT_FONT, ('white'), 1250, 50)
            # Writes square position from center of shape
            x2, y2 = rectangle.x + 25, rectangle.y + 25
            # draw_text('(' + str(x2) + ", " + str(y2) + ')', TEXT_FONT, ('white'), 1250, 100)
            # Write position of QB from center of shape
            x3, y3 = self.QB.x + 25, self.QB.y + 25
            # draw_text('(' + str(x3) + ", " + str(y3) + ')', TEXT_FONT, ('white'), 1250, 150)

            # draw line from center of rectangle to center of QB
            pygame.draw.line(self.screen, 'black', (x2, y2), (x3, y3), 3)

            for point in points:
                print('Point before transformation: ' + str(point))
                transformed_point = (point[0] * ScanGUI.SCALE_X, point[1] * ScanGUI.SCALE_Y)
                print('Point after transformation: ' + str(transformed_point))
                pygame.draw.circle(self.screen, 'yellow', transformed_point, 10)
                pygame.draw.circle(self.screen, 'black', transformed_point, 10, width=1)

            # Write magnitude and angle from rectangle to QB
            magX = x3-x2
            magY = y3-y2
            mag1 = math.sqrt((magX * magX) + (magY * magY))
            theta1 = '%.2f' % (math.degrees(math.atan2(magY, magX)) % 360)
            self.draw_text('(' + str(mag1) + ", " + str(theta1) + ')', ScanGUI.TEXT_FONT, 'white', 1250, 50)

            # Convert  coordinate position to feet
            # feet = '%.2f' % (mag1 / 15.5)
            # draw_text('(' + str(feet) + ", " + str(theta1) + ')', TEXT_FONT, ('white'), 1250, 100)

            self.clock.tick(ScanGUI.FPS)

            pygame.display.flip()

        pygame.quit()
        self.cam_client.close()
