import math
import os
import shutil
import sys
import time

import pygame

from PycharmUI.UIElement import *
from PycharmUI.robot import Robot
from cameraClient import CameraClient


class ScanGUI:
    """
    ScanGUI class

    Handles the graphical user interface for the sideline display component of the Scan and Score capstone project.


    Requires Bonjour Print Services to be installed to resolve the domain name overheadcam. If Bonjour Print Services
    cannot be installed, set use_ip to True when initializing an object of this class.
    """

    # Rendering constants
    SIM_FPS = 60
    SCREEN_WIDTH = 1000
    SCREEN_HEIGHT = 500
    FIELD_LENGTH = 90   # Represented as the vertical axis on display, parallel to SCREEN_WIDTH
    FIELD_WIDTH = 46    # Represented as the vertical axis on display, parallel to SCREEN_HEIGHT

    SCALE_X = SCREEN_WIDTH / FIELD_LENGTH
    SCALE_Y = SCREEN_HEIGHT / FIELD_WIDTH

    TEXT_FONT = None

    pattern_assigments = {
        'X': '322',
        'Y': '98',
        'STAIR': 'INFINITY'
    }

    def __init__(self, test, session_name, use_ip=False):
        """
        Initialize a session of the GUI client. Set test to True to connect to a server at localhost or False to connect
        to the server running on a separately connected camera device.

        :param test:                Boolean indicator of whether this GUI session is a test
        :param session_name:        The name of the GUI session, to be used as a filename for recorded game footage
        :param use_ip:              (Optional) Use the IP address of the server instead of its hostname
        """

        self.cam_client = CameraClient(test, use_ip)
        self.config = None

        # Set the screen size and name for the application
        pygame.init()
        self.screen = pygame.display.set_mode((ScanGUI.SCREEN_WIDTH, ScanGUI.SCREEN_HEIGHT), pygame.RESIZABLE)
        self.field = pygame.Surface((ScanGUI.SCREEN_WIDTH, ScanGUI.SCREEN_HEIGHT))
        pygame.display.set_caption('Scan & Score')

        ScanGUI.TEXT_FONT = pygame.font.SysFont('Arial', 20)  # AAAAAAAAAAAAAAAAAAAAAAHHHHHHHHHHHHH
        self.clock = pygame.time.Clock()

        # Keep track of UI elements that may be interacted with in certain ways
        self.ui_elements = []
        self.active_ui_element = None

        # Recording parameters
        self.save_frame_rate = 0
        self.avg_frame_interval = math.inf
        self.session_name = session_name

        self.reset_field()

        self.draw_text_center(self.field, 'Waiting for server...', 'black', self.screen.get_width() / 2, self.screen.get_height() / 2)
        pygame.transform.scale(self.field, self.screen.get_size(), self.screen)
        pygame.display.flip()

    def reset_field(self):
        # Setting size and initial position of drawn rects to represent bots
        self.cursor = pygame.rect.Rect(ScanGUI.SCREEN_WIDTH / 2, ScanGUI.SCREEN_HEIGHT / 2, ScanGUI.SCREEN_HEIGHT / 20, ScanGUI.SCREEN_HEIGHT/ 20)
        self.field = pygame.Surface((ScanGUI.SCREEN_WIDTH, ScanGUI.SCREEN_HEIGHT))

        # Fill the screen with a green box and outline it with black and white lines
        self.field.fill((55, 155, 90))

        # Create vertical lines every 15 feet
        line_spacing = 15
        line_location = 0
        for i in range(int(ScanGUI.FIELD_LENGTH / line_spacing) - 1):
            line_location += line_spacing * ScanGUI.SCALE_X
            pygame.draw.line(self.field, 'white', (line_location, 0), (line_location, ScanGUI.SCREEN_HEIGHT),
                             width=20)
            self.draw_text(self.field, str(line_spacing * (i + 1)) + "'", 'black', line_location - ScanGUI.SCREEN_WIDTH / 50, 0.1 * ScanGUI.SCREEN_HEIGHT)
            self.draw_text(self.field, str(line_spacing * (i + 1)) + "'", 'black', ScanGUI.SCREEN_WIDTH * 49 / 50 - line_location, 0.9 * ScanGUI.SCREEN_HEIGHT)

        # Outline the field with white and black lines
        pygame.draw.rect(self.field, 'white', (0, 0, ScanGUI.SCREEN_WIDTH, ScanGUI.SCREEN_HEIGHT), width=20)
        pygame.draw.rect(self.field, 'black', (0, 0, ScanGUI.SCREEN_WIDTH, ScanGUI.SCREEN_HEIGHT), width=5)
        return

    def focus(self, ui_element):
        if ui_element is None:

            # Defocus the focused UI element
            if self.active_ui_element is not None:
                self.active_ui_element.defocus()
            self.active_ui_element = None

        else:

            # If the previously focused element is not the current one, defocus it
            if self.active_ui_element is not None and self.active_ui_element != ui_element:
                self.active_ui_element.defocus()
            self.active_ui_element = ui_element
            self.active_ui_element.focus()

    def handle_event(self, event):
        """
        Handle a given input event.

        :param event:   A pygame event
        :return:
        """

        event_handled = False

        # QUIT event occurs when the user clicks the X to close the app window
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:

            # Let's just treat the list of clickable UI elements like a queue. I'm sure this'll run faster than O(n^2)
            # (He doesn't know)
            for i in range(len(self.ui_elements)):

                # Get the head of the queue and immediately re-enqueue it at the tail
                ui_element = self.ui_elements.pop(0)
                self.ui_elements.append(ui_element)
                print(self.ui_elements)

                # If this is the element that was clicked, select it
                if ui_element.rect.collidepoint(event.pos):

                    # If the element can be focused, switch focus to it
                    if ui_element.focusable:

                        self.focus(ui_element)

                    # Register the click
                    self.active_ui_element.handle_click()
                    event_handled = True

                    # No need to keep checking elements after the clicked element has been found
                    break

            if not event_handled:
                self.focus(None)

        # Check if the event is a keyboard input and there is an active input box
        elif event.type == pygame.KEYDOWN:

            if self.active_ui_element is None:
                return False

            return_code = self.active_ui_element.handle_keypress(event)

            if return_code == UIElement.ReturnCode.FOCUS_NEXT_ELEMENT:

                # Select the next UI element
                self.focus(self.ui_elements.pop(0))
                self.ui_elements.append(self.active_ui_element)

            elif return_code == UIElement.ReturnCode.DEFOCUS_ME:

                self.focus(None)

            if return_code != UIElement.ReturnCode.COULD_NOT_HANDLE:
                event_handled = True

        return event_handled


    def startup(self):
        """

        :return:
        """

        input1 = CheckBox((100, 0), (100, 50))
        input2 = InputBox((100, 100), (100, 50))
        #input2.placeholder = ''
        robot = Robot((200, 200), (50, 50), 'receiver', '322')

        self.ui_elements.extend([input1, input2, robot])
        print(self.ui_elements)

        while True:

            # Process events, which consist of user inputs
            for event in pygame.event.get():

                self.handle_event(event)

            # Rendering
            mat = self.field.copy()

            for element in self.ui_elements:
                element.draw_self(mat)

            pygame.transform.scale(mat, self.screen.get_size(), self.screen)

            self.clock.tick(ScanGUI.SIM_FPS)
            pygame.display.flip()

        return

    def get_avg_frame_rate(self):
        return 1 / self.avg_frame_interval

    def shutdown(self):
        pygame.quit()
        self.cam_client.close()

    @staticmethod
    def draw_text(surf, text, text_col, x, y):
        # Function for text to be added on screen as an image
        img = ScanGUI.TEXT_FONT.render(text, True, text_col)
        surf.blit(img, (x, y))

    @staticmethod
    def draw_text_center(surf, text, text_col, x, y):

        img = ScanGUI.TEXT_FONT.render(text, True, text_col)

        new_x = x - img.get_width() / 2
        new_y = y - img.get_height() / 2
        surf.blit(img, (new_x, new_y))

    def run(self, connect_attempt_limit=1):


        # Render the startup screen
        #self.startup()

        self.reset_field()

        num_frames_saved = 0
        cumulative_frame_overshoot = 0

        # Determine whether to record the session based on the given frame rate
        record = False
        frame_interval = math.inf

        frame_rate = 4#self.config['FPS']

        if frame_rate > 0:
            frame_interval = 1 / frame_rate
            record = True

            # If the application is going to record, it needs a folder in which to save recorded frames
            # To be safe, first check if the desired folder already exists
            if os.path.exists(self.session_name):

                # Delete the folder and all of its contents
                shutil.rmtree(self.session_name)

            # Make the folder using the provided session name
            os.makedirs(self.session_name)

        # Get the start time of the session
        start = time.time()
        mark = start

        cursor_dragging = False
        offset_x = offset_y = 0

        run = True
        connected = False
        while run:

            # Attempt to connect to the camera server
            if not connected:
                try:
                    self.config = self.cam_client.connect()
                    connected = True
                    self.reset_field()
                # Handle the error that is raised when the server doesn't accept the connection
                except ConnectionRefusedError as e:

                    # Update the number of attempts left until the client gives up on making the connection
                    connect_attempt_limit -= 1

                    self.reset_field()
                    self.draw_text_center(self.field, 'Waiting for server. Number of attempts left: ' +
                                          str(connect_attempt_limit), 'black', self.screen.get_width() / 2,
                                          self.screen.get_height() / 2)

                    if connect_attempt_limit < 1:
                        break

            mat = self.field.copy()

            # Receive the points representing detected bots from the camera server
            bot_positions = []

            if connected:
                bot_positions = self.cam_client.receive_points()

            # Draw the cursor on the screen as a rectangle
            pygame.draw.rect(mat, 'blue', self.cursor)

            # Handle input events
            for event in pygame.event.get():

                # Exit the application upon clicking the OS's default app close button
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                # Handle the clicking and dragging of the cursor
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if self.cursor.collidepoint(event.pos):
                            cursor_dragging = True
                            mouse_x, mouse_y = event.pos
                            offset_x = self.cursor.x - mouse_x
                            offset_y = self.cursor.y - mouse_y

                # Handle the release of the left mouse button, stopping the dragging of the cursor
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        cursor_dragging = False

                elif event.type == pygame.MOUSEMOTION:
                    if cursor_dragging:
                        mouse_x, mouse_y = event.pos
                        self.cursor.x = mouse_x + offset_x
                        self.cursor.y = mouse_y + offset_y

            for bot_pattern in bot_positions:
                bot_name = bot_pattern
                if bot_pattern in self.pattern_assigments.keys():
                    bot_name = self.pattern_assigments[bot_pattern]

                bot_exists = False

                point = bot_positions[bot_pattern]
                if point is None:
                    continue

                if len(point) != 2:
                    continue

                print('Point before transformation: ' + str(point))
                transformed_point = (point[0] * ScanGUI.SCALE_X, ScanGUI.SCREEN_HEIGHT - point[1] * ScanGUI.SCALE_Y)
                print('Point after transformation: ' + str(transformed_point))

                # Check to see if the bot has already been instantiated in the simulation
                for ui_element in self.ui_elements:
                    if isinstance(ui_element, Robot):
                        if ui_element.name == bot_name:
                            bot = ui_element
                            bot.rect.x, bot.rect.y = transformed_point

                            bot_exists = True

                # If the bot hasn't been instantiated, get on that
                if not bot_exists:
                    bot = Robot(transformed_point, (50, 50), 'receiver', bot_name)
                    self.ui_elements.append(bot)

                #pygame.draw.circle(mat, 'orange', transformed_point, 10)
                #self.draw_text(mat, 'WR', 'black', transformed_point[0], transformed_point[1])
                #pygame.draw.circle(mat, 'black', transformed_point, 10, width=1)

                cursor_x = self.cursor.x - self.cursor.width / 2
                cursor_y = self.cursor.y + self.cursor.height / 2

                # draw line from center of rectangle to center of QB
                pygame.draw.line(mat, 'black', transformed_point, (cursor_x, cursor_y), 3)

            # Write magnitude and angle from the cursor to each of the bots
            '''if len(points) > 0:
                self.draw_text(mat, '(' + str(points[0][0]) + ", " + str(points[0][1]) + ')', 'black', 720, 400)'''

            for ui_element in self.ui_elements:
                ui_element.draw_self(mat)

            pygame.transform.scale(mat, self.screen.get_size(), self.screen)

            self.clock.tick(ScanGUI.SIM_FPS)
            pygame.display.flip()


            # Recording things
            if record and connected:

                # If the current time exceeds the time at which the next frame should be captured, save the current frame
                now = time.time()
                if now > mark:
                    # It is not guaranteed that the frame will be saved at the exact time it was supposed to
                    # Save the time overshoot cumulatively so it may be used to correct the video frame rate during the
                    # render stage
                    cumulative_frame_overshoot += now - mark
                    mark = now + frame_interval

                    pygame.image.save(mat, self.session_name + '/' + str(now) + '.jpg')
                    num_frames_saved += 1

                avg_frame_rate = self.save_frame_rate

                # Calculate the average actual framerate of the recorded video frames
                if num_frames_saved > 0:
                    avg_frame_overshoot = cumulative_frame_overshoot / num_frames_saved
                    self.avg_frame_interval = frame_interval + avg_frame_overshoot

        return connected
