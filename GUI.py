import pygame
import sys, math, socket, ast
from inputbox import InputBox
from pygame.locals import *

host = socket.gethostname()
port = 5000
client_socket = socket.socket()
client_socket.connect((host, port))

response = 'OK'
client_socket.send(response.encode())

pygame.init()

screen_width = 1440
screen_height = 720
FIELD_LENGTH = 90   # x
FIELD_WIDTH = 46    # y

# Setting screen size and name for application
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Scan & Score")
text_font = pygame.font.SysFont("Arial", 30)


def draw_text(text, font, text_col, x, y):
    # Function for text to be added on screen as an image
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


# Setting size and initial position of drawn rects to represent bots
QB = pygame.rect.Rect(1000, 360, 51, 51)
WR1 = pygame.rect.Rect(300, 200, 51, 51)
WR2 = pygame.rect.Rect(300, 500, 51, 51)

# Rect used for testing dragging and calculations of magnitude and angle
rectangle = pygame.rect.Rect(0, 0, 51, 51)
rectangle_dragging = False

FPS = 120
clock = pygame.time.Clock()

run = True
while run:

    first_packet = client_socket.recv(1024).decode()
    print(first_packet)

    num_packets = int(first_packet[0])
    data = first_packet[1:]
    points = ast.literal_eval(data)
    for i in range(num_packets - 1):
        packet = client_socket.recv(1024).decode()
        points.append(ast.literal_eval(packet))
    response = 'OK'
    client_socket.send(response.encode())

    # Fills Screen with a green box, outlines it with black and white lines
    screen.fill((55, 155, 90))
    pygame.draw.rect(screen, ('white'), (0, 0, 1440, 720), width=20)
    pygame.draw.rect(screen, ('black'), (0, 0, 1440, 720), width=5)

    # Creates vertical lines every 240 pixels to simulate hash marks and labels them for every 15 feet
    for i in range(5):
        pygame.draw.line(screen, ('white'), (240 * (i + 1), 5,), (240 * (i + 1), 714), width=20)
        feet = 15 * (i + 1)
        draw_text(str(feet) + "'", text_font, (0, 0, 0), 240 * (i + 1) - 42, 20)
        draw_text(str(feet) + "'", text_font, (0, 0, 0), 1398 - 240 * (i + 1), 665)

    # Draw squares on screen to represent robots
    pygame.draw.rect(screen, 'blue', QB)
    pygame.draw.rect(screen, 'red', WR1)
    pygame.draw.rect(screen, 'yellow', WR2)
    pygame.draw.rect(screen, 'purple', rectangle)

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
    # draw_text('(' + str(x1) + ", " + str(y1) + ')', text_font, ('white'), 1250, 50)
    # Writes square position from center of shape
    x2, y2 = rectangle.x + 25, rectangle.y + 25
    # draw_text('(' + str(x2) + ", " + str(y2) + ')', text_font, ('white'), 1250, 100)
    # Write position of QB from center of shape
    x3, y3 = QB.x + 25, QB.y + 25
    # draw_text('(' + str(x3) + ", " + str(y3) + ')', text_font, ('white'), 1250, 150)

    # draw line from center of rectangle to center of QB
    pygame.draw.line(screen, 'black', (x2, y2), (x3, y3), 3)

    for point in points:
        transformed_point = (point[0] * screen_width / FIELD_LENGTH, point[1] * screen_height / FIELD_WIDTH)
        print(transformed_point)
        pygame.draw.circle(screen, 'red', transformed_point, 5)

    # Write magnitude and angle from rectangle to QB
    magX = x3-x2
    magY = y3-y2
    mag1 = math.sqrt((magX * magX) + (magY * magY))
    theta1 = '%.2f' % (math.degrees(math.atan2(magY, magX)) % 360)
    draw_text('(' + str(magX) + ", " + str(theta1) + ')', text_font, ('white'), 1250, 50)

    # Convert  coordinate position to feet
    # feet = '%.2f' % (mag1 / 15.5)
    # draw_text('(' + str(feet) + ", " + str(theta1) + ')', text_font, ('white'), 1250, 100)

    clock.tick(FPS)

    pygame.display.flip()

pygame.quit()
client_socket.close()
