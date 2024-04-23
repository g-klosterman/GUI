import pygame
import sys, math, random, time, os, shutil
from cameraClient import CameraClient
from inputbox import InputBox   # Do not delete, will need this later


# Generate a random RGB color
def random_color():
    levels = range(32, 256, 32)     # Possible levels for each color are form 32 to 256 in increments of 32
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

    def __init__(self, test, save_frame_rate, session_name):
        if test:
            ScanGUI.HOST = 'localhost'
        self.cam_client = CameraClient(ScanGUI.HOST, ScanGUI.PORT)

        # Set the screen size and name for the application
        pygame.init()
        self.screen = pygame.display.set_mode((ScanGUI.SCREEN_WIDTH, ScanGUI.SCREEN_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption('Scan & Score')

        ScanGUI.TEXT_FONT = pygame.font.SysFont('Arial', 30)  # AAAAAAAAAAAAAAAAAAAAAAHHHHHHHHHHHHH
        self.clock = pygame.time.Clock()

        # Robots
        self.QB = None
        self.WR1 = None
        self.WR2 = None

        self.save_frame_rate = save_frame_rate
        self.session_name = session_name

        self.reset_field()

        self.draw_text('Waiting for server...', ScanGUI.TEXT_FONT, 'white', self.screen.get_width() / 2, self.screen.get_height() / 2)
        pygame.display.flip()

    def reset_field(self):
        # Setting size and initial position of drawn rects to represent bots
        self.QB = pygame.rect.Rect(1000, 360, 51, 51)
        self.WR1 = pygame.rect.Rect(300, 200, 51, 51)
        self.WR2 = pygame.rect.Rect(300, 500, 51, 51)

    def startup(self):
        input1 = InputBox()

    def shutdown(self):
        pygame.quit()
        self.cam_client.close()

    def draw_text(self, text, font, text_col, x, y):
        # Function for text to be added on screen as an image
        img = font.render(text, True, text_col)
        self.screen.blit(img, (x, y))

    def run(self):
        try:
            self.cam_client.connect()
        except ConnectionRefusedError as e:
            raise e

        # Rect used for testing dragging and calculations of magnitude and angle
        rectangle = pygame.rect.Rect(0, 0, 51, 51)
        rectangle_dragging = False

        # Determine whether to record the session based on the given frame rate
        record = False
        frame_interval = math.inf
        if self.save_frame_rate > 0:
            frame_interval = 1 / self.save_frame_rate
            record = True

            # If the application needs to record, make an empty folder in which to save images
            if os.path.exists(self.session_name):
                shutil.rmtree(self.session_name)
            os.makedirs(self.session_name)

        # Get the start time of the session
        start = time.time()
        mark = start

        run = True
        while run:

            # Receive the points representing detected bots from the camera server
            points = self.cam_client.receive_points()

            pygame.display.get_window_size()

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

            for point in points:
                print('Point before transformation: ' + str(point))
                transformed_point = (point[0] * ScanGUI.SCALE_X, ScanGUI.SCREEN_HEIGHT - point[1] * ScanGUI.SCALE_Y)
                print('Point after transformation: ' + str(transformed_point))
                pygame.draw.circle(self.screen, 'yellow', transformed_point, 10)
                pygame.draw.circle(self.screen, 'black', transformed_point, 10, width=1)

                # Write cursor position
                x1, y1 = pygame.mouse.get_pos()
                # draw_text('(' + str(x1) + ", " + str(y1) + ')', TEXT_FONT, ('white'), 1250, 50)
                # Writes square position from center of shape
                x2, y2 = transformed_point[0], transformed_point[1]
                # draw_text('(' + str(x2) + ", " + str(y2) + ')', TEXT_FONT, ('white'), 1250, 100)
                # Write position of QB from center of shape
                x3, y3 = self.QB.x + 25, self.QB.y + 25
                # draw_text('(' + str(x3) + ", " + str(y3) + ')', TEXT_FONT, ('white'), 1250, 150)

                # draw line from center of rectangle to center of QB
                pygame.draw.line(self.screen, 'black', (x2, y2), (x3, y3), 3)

            # Write magnitude and angle from rectangle to QB
            if len(points) > 0:
                self.draw_text('(' + str(points[0][0]) + ", " + str(points[0][1]) + ')', ScanGUI.TEXT_FONT, 'black', 720, 640)

            self.clock.tick(ScanGUI.FPS)

            if record:
                # If the current time exceeds the time at which the next frame should be captured, save the current frame
                now = time.time()
                if now - mark >= 0:
                    mark = mark + frame_interval

                    pygame.image.save(self.screen, self.session_name + '/' + str(now) + '.jpg')

            pygame.display.flip()
