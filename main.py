from pygame.locals import *
import socket, pygame, time
#define variables
x = y = 0
screen = pygame.display.set_mode((430, 410))
targetRectangle = pygame.draw.rect(screen, (255, 0, 0), (176, 134, 7, 7))
pygame.display.flip()
#define smaller functions
  #define function to start pygame window
def startPygame():
  pygame.display.set_caption(option + " Tracking System")
  pygame.mouse.set_visible(True)
  screen.fill((255, 255, 255))
  targetRectangle = pygame.draw.rect(screen, (255, 0, 0), (176, 134, 7, 7))
  pygame.display.flip()
  #define function to update pygame window
def updateWindow():
  screen.fill((255, 255, 255))
  global targetRectangle
  global xPosition
  global yPosition
  targetRectangle = pygame.draw.rect(screen, (255, 0, 0), (xPosition, yPosition, 7, 7))
  pygame.display.flip()
#define main functions
def collectMouseData():
  startPygame()
  print "\n"
  print "mouse tracking system"
    #wait until a mouse button is clicked
  running = 1
  while running == 1:
    event = pygame.event.poll()
    if event.type == pygame.QUIT:
      c.send("quit")
      pygame.quit()
      running = 0
    #see if a mousebutton is down
    elif event.type == pygame.MOUSEBUTTONDOWN:
      xMouse = event.pos[0]
      yMouse = event.pos[1]
      #see if mouse click collides with targetRectangle
      if targetRectangle.collidepoint(xMouse, yMouse):
        global xPosition
        xPosition = event.pos[0]
        global yPosition
        yPosition = event.pos[1]
        updateWindow()
        global targetRectangle
        sendData(targetRectangle)