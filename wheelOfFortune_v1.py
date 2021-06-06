# Patria Lim Yun Xuan U1921783K
# Module to create pygame window for spin the wheel to pick a random canteen

import pygame
import random


def start():
    # intialises the game
    pygame.init()

    # set screen width and height
    screen_width = 800
    screen_height = 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    screen_rect = screen.get_rect()  # gets rectangular area of the surface

    # creates the header: title and icon of screen
    icon = pygame.image.load("color-wheel.png")  # image obtained from flaticons.com
    pygame.display.set_caption("NTU Canteens 'Spin the wheel!'")
    pygame.display.set_icon(icon)

    # creates a text object
    def text_objects(text, font):
        text_surface = font.render(text, True, (0, 0, 0))
        return text_surface, text_surface.get_rect()

    # function to input text
    def message_display(text, pos_tuple, font_size):
        text_size = pygame.font.Font('freesansbold.ttf', font_size)
        text_surf, text_rect = text_objects(text, text_size)
        text_rect.center = pos_tuple
        screen.blit(text_surf, text_rect)

    # loads image
    wheel_img = pygame.image.load('WheelOfFortune.png').convert()  # created using Adobe Illustrator

    # creates object to track time
    clock = pygame.time.Clock()

    # randomise the starting point
    angle = random.randint(0, 365)

    # boolean states
    default_spin_rate = False
    spin_rate_2 = False
    spin_rate_3 = False
    spin_rate_4 = False
    running = True

    # time placeholder
    time1 = 0

    # game loop
    while running:
        # returns timing at this point (changes every while loop)
        time2 = pygame.time.get_ticks()
        # background colour
        screen.fill((255, 255, 255))
        # optional: limits the frames per second so that the wheel will not rotate too fast
        clock.tick(60)
        # drawing rotated wheel image onto screen
        rotated_image = pygame.transform.rotate(wheel_img, angle)
        image_rect = wheel_img.get_rect(center=screen_rect.center)
        image_rect = rotated_image.get_rect(center=image_rect.center)
        screen.blit(rotated_image, image_rect)
        # drawing shapes
        pygame.draw.rect(screen, (255, 0, 0), (550, 300, 100, 10))  # rectangular part of 'stopper'
        pygame.draw.polygon(screen, (255, 0, 0), [(500, 305), (550, 300), (550, 310)])  # triangular part of 'stopper'
        spin_box = pygame.draw.rect(screen, (255, 246, 102), (250, 550, 150, 50))  # yellow spin rectangle
        stop_box = pygame.draw.rect(screen, (170, 39, 226), (400, 550, 150, 50))  # pink stop rectangle
        # printing text
        message_display("SPIN", (325, 575), 30)
        message_display("STOP", (475, 575), 30)
        message_display("CLICK HERE:", (400, 540), 15)

        for event in pygame.event.get():
            # closes the window when the close button is pressed
            if event.type == pygame.QUIT:
                running = False
            # when mouse button is pressed down
            if event.type == pygame.MOUSEBUTTONDOWN:
                # '1' is the left mouse button
                if event.button == 1:
                    # collects coordinates of mouse cursor
                    x, y = event.pos
                    # checks if the coordinates are within the rectangular box
                    # spin box is clicked
                    if spin_box.collidepoint(x, y):
                        # restore all boolean states to start state
                        default_spin_rate = True  # flips switch to start spinning
                        spin_rate_2 = False
                        spin_rate_3 = False
                        spin_rate_4 = False
                        # re-randomises the starting point
                        angle = random.randint(0, 365)
                    # stop box is clicked
                    if stop_box.collidepoint(x, y):
                        # disable initial spin rate
                        default_spin_rate = False
                        # flips on the switch to slow down the wheel
                        spin_rate_2 = True
                        print('\nPatriaBot: You have stopped the wheel...3...')
                        time1 = time2

        # initial spin rate
        if default_spin_rate:
            angle += 40

        # this loop is triggered:
        if spin_rate_2:
            # slows down the angle by 5 degrees less per frame rate
            angle += 10
            # loop through until the timing is sufficient
            if time2 - time1 >= 1000:
                print('2...')
                # updates time1 to take on new timing at this point
                time1 = time2
                # disables this spin rate
                spin_rate_2 = False
                # enables next spin rate
                spin_rate_3 = True

        # gradual slow down makes wheel more realistic
        if spin_rate_3:
            angle += 5
            if time2 - time1 >= 1000:
                print('1...')
                time1 = time2
                spin_rate_3 = False
                spin_rate_4 = True

        if spin_rate_4:
            angle += 2.5
            if time2 - time1 >= 1000:
                spin_rate_4 = False
                print('\nPatriaBot: Here is your lucky choice for today. Press close(X) button to continue the menu.')

        pygame.display.update()
