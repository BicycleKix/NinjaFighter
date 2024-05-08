import pygame
import sys

pygame.init()
pygame.joystick.init()

# Set up display
screen = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
pygame.display.set_caption('joystick example')

clock = pygame.time.Clock()

joystick_count = pygame.joystick.get_count()
controllers = []

# Initialize each joystick
for i in range(joystick_count):
    joystick = pygame.joystick.Joystick(i)
    joystick.init()
    controllers.append(joystick)
    print("Joystick", i + 1, ":", joystick.get_name())

running = True

colors = ['red', 'orange', 'yellow', 'green', 'blue', 'indigo', 'violet']

a = 0

x, y, i, j = 100, 100, 100, 100
r = 50

movement = [0, 0]
sizing = [0, 0]
radiusing = [0, 0]

while running:

    screen.fill((255, 255, 255))

    # if movement[0] > 0:
    #     x = min(x + movement[0], screen.get_width() - i)
    # else:
    #     x = max(0, x + movement[0])
    # if movement[1] > 0:
    #     y = min(y + movement[1], screen.get_height() - j)
    # else:
    #     y = max(0, y + movement[1])
    # if sizing[0] > 0:
    #     i = min(i + sizing[0], screen.get_width() - x)
    # else:
    #     i = max(0, i + sizing[0])
    # if sizing[1] > 0:
    #     j = min(j + sizing[1], screen.get_height() - y)
    # else:
    #     j = max(0, j + sizing[1])

    #pygame.draw.rect(screen, colors[a], (x, y, i, j))

    r = max(0, r + radiusing[0] + radiusing[1])
    r = min(min(screen.get_height()/2, screen.get_width()/2), r)

    pygame.draw.circle(screen, colors[a], (x, y), r)

    if movement[0] > 0:
        x = min(x + movement[0], screen.get_width() - r)
    else:
        x = max(r, x + movement[0])
    if movement[1] > 0:
        y = min(y + movement[1], screen.get_height() - r)
    else:
        y = max(r, y + movement[1])

    x = min(x, screen.get_width() - r)
    y = min(y, screen.get_height() - r)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                a = (a + 1) % len(colors)
            if event.button == 2:
                a = (a - 1) % len(colors)
        if event.type == pygame.JOYAXISMOTION:
            axis = event.axis
            axis_value = event.value

            if axis == 0:  # X-axis of left stick
                if abs(axis_value) > 0.1:
                    movement[0] = 8 * axis_value
                else:
                    movement[0] = 0
                    
            if axis == 1:  # Y-axis of left stick
                if abs(axis_value) > 0.1:
                    movement[1] = 8 * axis_value
                else:
                    movement[1] = 0

            if axis == 2:
                if abs(axis_value) > 0.1:
                    sizing[0] = 5 * axis_value
                else:
                    sizing[0] = 0

            if axis == 3:
                if abs(axis_value) > 0.1:
                    sizing[1] = 5 * axis_value
                else:
                    sizing[1] = 0

            if axis == 4:
                print('LT', axis_value)
                if axis_value > -0.95:
                    radiusing[0] = axis_value + 1
                else:
                    radiusing[0] = 0
            
            if axis == 5:
                print('RT', axis_value)
                if axis_value > -0.95:
                    radiusing[1] = - 1 - axis_value
                else:
                    radiusing[1] = 0

        if event.type == pygame.JOYBUTTONDOWN:
            print(event.button)
            if event.button == 1:
                a = (a + 1) % len(colors)
            if event.button == 0:
                a = (a - 1) % len(colors)

    clock.tick(60)
    pygame.display.update()


pygame.quit()
sys.exit()