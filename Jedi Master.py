#----------------------------------------------------------------------------------------------------------------------------------------------------------#
#Herman Liao                                                                                                                                               #
#ICS2O1-02                                                                                                                                                 #
#Summative Project                                                                                                                                         #
#----------------------------------------------------------------------------------------------------------------------------------------------------------#
#Initial setup
import pygame, sys, math, random
from pygame.locals import*
from math import*
width = 1280
height = 960
pygame.init()
clock = pygame.time.Clock()
window = pygame.display.set_mode((width, height))
pygame.display.set_caption("Jedi Master")
FPS = 60

#---------------------------------------------------------------------Define functions---------------------------------------------------------------------
#Draw text so that the center is on center
def Draw_text(surface, colour, font, center, text):
    text_object = font.render(text, 1, colour)
    text_rect = text_object.get_rect()
    text_rect.center = (int(center[0]), int(center[1]))
    surface.blit(text_object, text_rect)

#Math and physics
    #Finds the direction from the start to the target, then returns a point on that line that is distance_from_start away from the start
def Point_to(start, target, distance_from_start):
    deltax = target[0] - start[0]
    deltay = target[1] - start[1]
    if deltax == deltay == 0:
        return [start[0] + distance_from_start, start[1]]
    distance = hypot(deltax, deltay)
    result = [start[0] + deltax / distance * distance_from_start, start[1] + deltay / distance * distance_from_start]
    return result

    #Rotates a list of points around a centre clockwise; radians is the amount of turning in radians
def Rotate_clockwise(pointlist, center, radians):
    new_pointlist = []
    for point in pointlist:
        deltax = point[0] - center[0]
        deltay = point[1] - center[1]
        radius = hypot(deltax, deltay)
        current_angle = atan2(deltay, deltax)
        new_angle = current_angle + radians
        new_point = (radius * cos(new_angle) + center[0], radius * sin(new_angle) + center[1])
        new_pointlist.append(new_point)
    return new_pointlist

    #Calculates the direction of a reflected ray, given the deflector's angle and the incident ray's angle
def Deflect(ray_direction, deflector_direction):
    normal = deflector_direction + pi / 2
    angle_of_incidence = normal - ray_direction
    new_ray_direction = normal + angle_of_incidence
    return new_ray_direction

    #Collision detection
        #Two lines, extension makes sure that the intersection is between the two x values and the two y values
def Do_lines_intersect(line1_direction, line1_point, line2_direction, line2_point, extension = [[0, 0], [0, 0]]):
    line1_slope = tan(line1_direction)
    line2_slope = tan(line2_direction)
    if line1_slope == line2_slope:
        y_intercept1 = line1_slope * -line1_point[0] + line1_point[1]
        y_intercept2 = line2_slope * -line2_point[0] + line2_point[1]
        if y_intercept1 == y_intercept2:
            return True
        else:
            return False
    elif line1_slope == "infinity":
        x = line1_point[0]
        line2_intercept = line2_slope * -line2_point[0] + line2_point[1]
        y = line2_slope * x + line2_intercept
    elif line2_slope == "infinity":
        x = line2_point[0]
        line1_intercept = line1_slope * -line1_point[0] + line1_point[1]
        y = line1_slope * x + line1_intercept
    else:
        line1_intercept = line1_slope * -line1_point[0] + line1_point[1]
        line2_intercept = line2_slope * -line2_point[0] + line2_point[1]
        x = (line2_intercept - line1_intercept) / (line1_slope - line2_slope)
        y = line1_slope * x + line1_intercept

    if extension[0] == extension[1]:
        return [x, y]
    elif extension[0][0] <= x <= extension[1][0] or extension[0][0] >= x >= extension[1][0]:
        if extension[0][1] <= y <= extension[1][1] or extension[0][1] >= y >= extension[1][1]:
            return [x, y]
        else:
            return False
    else:
        return False

        #Two circles
def Do_circles_intersect(circle1, circle2):
    distance_between_centres = hypot(circle1[0][0] - circle2[0][0], circle1[0][1] - circle2[0][1])
    if distance_between_centres <= circle1[1] + circle2[1]:
        return True
    else:
        return False

        #Line and circle, extend decides whether the line goes past the start and end points, returns all intersection points between the line and the circle's edge
def Do_line_and_circle_intersect(circle, linestart, lineend, extend = False):
    deltax = linestart[0] - lineend[0]
    deltay = linestart[1] - lineend[1]
    laser_direction = atan2(lineend[1] - linestart[1], lineend[0] - linestart[0])
    closest_point = Do_lines_intersect(atan2(deltay, deltax), linestart, atan2(-deltax, deltay), circle[0])
    if hypot(closest_point[0] - circle[0][0], closest_point[1] - circle[0][1]) <= circle[1]:
        if [circle[0][0], circle[0][1]] == [closest_point[0], closest_point[1]]:
            [x1, y1] = [circle[0][0] + cos(laser_direction + pi) * circle[1], circle[0][1] + sin(laser_direction + pi) * circle[1]]
            [x2, y2] = [circle[0][0] + cos(laser_direction) * circle[1], circle[0][1] + sin(laser_direction) * circle[1]]
            return_list = []
            if extend == True:
                return_list = [[x1, y1], [x2, y2]]
            else:
                if linestart[0] <= x1 <= lineend[0] or linestart[0] >= x1 >= lineend[0]:
                    if linestart[1] <= y1 <= lineend[1] or linestart[1] >= y1 >= lineend[1]:
                        return_list.append([x1, y1])
                if linestart[0] <= x2 <= lineend[0] or linestart[0] >= x2 >= lineend[0]:
                    if linestart[1] <= y2 <= lineend[1] or linestart[1] >= y2 >= lineend[1]:
                        return_list.append([x2, y2])
            if return_list == []:
                return False
            return return_list
        distance_to_closest = hypot(closest_point[0] - circle[0][0], closest_point[1] - circle[0][1])
        if distance_to_closest == circle[1]:
            if linestart[0] <= closest_point[0] <= lineend[0] or linestart[0] >= closest_point[0] >= lineend[0]:
                if linestart[0] <= closest_point[0] <= lineend[0] or linestart[0] >= closest_point[0] >= lineend[0]:
                    return [closest_point]
            return False
        closest_to_edge_distance = sqrt(circle[1] ** 2 - distance_to_closest ** 2)
        [x1, y1] = Point_to(closest_point, [closest_point[0] + cos(laser_direction), closest_point[1] + sin(laser_direction)], closest_to_edge_distance)
        [x2, y2] = Point_to(closest_point, [closest_point[0] + cos(laser_direction + pi) * 10000, closest_point[1] + sin(laser_direction + pi) * 10000], closest_to_edge_distance)
        return_list = []
        if extend == True:
            return_list = [[x1, y1], [x2, y2]]
        else:
            if linestart[0] <= x1 <= lineend[0] or linestart[0] >= x1 >= lineend[0]:
                if linestart[1] <= y1 <= lineend[1] or linestart[1] >= y1 >= lineend[1]:
                    return_list.append([x1, y1])
            if linestart[0] <= x2 <= lineend[0] or linestart[0] >= x2 >= lineend[0]:
                if linestart[1] <= y2 <= lineend[1] or linestart[1] >= y2 >= lineend[1]:
                    return_list.append([x2, y2])
        if return_list == []:
            return False
        return return_list
    else:
        return False

#In-game functions
#------------------------------------------------------------------------Pause game------------------------------------------------------------------------
def Pause_game():
    buttons = [Button([0, 0, 200, 50], "Quit to menu", small_font), Button([width / 2 - 250, height / 3, 500, 75], "Resume game", regular_font), Button([width / 2 - 250, height / 3 + 100, 500, 75], "Cheats", regular_font), Button([width / 2 - 250, height / 3 + 200, 500, 75], "Settings", regular_font)]
    selected_button = None
    mouse_down = False
    while True:
        window.fill((255, 255, 255))
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pause_game_key:
                    return None
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_down = True
                if event.button == 1:
                    for button in buttons:
                        if button.rect[0] <= mouse_pos[0] <= button.rect[0] + button.rect[2] and button.rect[1] <= mouse_pos[1] <= button.rect[1] + button.rect[3]:
                            button.pressed = True
                            selected_button = button
            if event.type == pygame.MOUSEBUTTONUP:
                mouse_down = False
                if event.button == 1:
                    if buttons[0].rect[0] <= mouse_pos[0] <= buttons[0].rect[0] + buttons[0].rect[2] and buttons[0].rect[1] <= mouse_pos[1] <= buttons[0].rect[1] + buttons[0].rect[3]:
                        buttons[0].pressed = False
                        if selected_button != None:
                            if selected_button == buttons[0]:
                                return "Menu"
                    elif buttons[1].rect[0] <= mouse_pos[0] <= buttons[1].rect[0] + buttons[1].rect[2] and buttons[1].rect[1] <= mouse_pos[1] <= buttons[1].rect[1] + buttons[1].rect[3]:
                        buttons[1].pressed = False
                        if selected_button != None:
                            if selected_button == buttons[1]:
                                return None
                    elif buttons[2].rect[0] <= mouse_pos[0] <= buttons[2].rect[0] + buttons[2].rect[2] and buttons[2].rect[1] <= mouse_pos[1] <= buttons[2].rect[1] + buttons[2].rect[3]:
                        buttons[2].pressed = False
                        if selected_button != None:
                            if selected_button == buttons[2]:
                                return "Cheats"
                    elif buttons[3].rect[0] <= mouse_pos[0] <= buttons[3].rect[0] + buttons[3].rect[2] and buttons[3].rect[1] <= mouse_pos[1] <= buttons[3].rect[1] + buttons[3].rect[3]:
                        buttons[3].pressed = False
                        if selected_button != None:
                            if selected_button == buttons[3]:
                                return "Settings"
                    else:
                        selected_button = None

        Draw_text(window, (0, 0, 0), large_font, [width / 2, height / 6], "Game Paused")
        for button in buttons:
            if selected_button == button and mouse_down == True:
                if button.rect[0] <= mouse_pos[0] <= button.rect[0] + button.rect[2] and button.rect[1] <= mouse_pos[1] <= button.rect[1] + button.rect[3]:
                    button.pressed = True
                else:
                    button.pressed = False
            button.display()

        pygame.display.flip()
        clock.tick(FPS)

#----------------------------------------------------------------------Choose settings----------------------------------------------------------------------
def Settings():
    selected_key = None
    buttons = [Button([0, 0, 100, 50], "Back", small_font), Button([width / 3 - 125, height / 3, 250, 50], "Music", small_font), Button([2 * width / 3 - 125, height / 3, 250, 50], "Sounds", small_font)]
    selected_button = None
    mouse_down = False
    new_keys = all_keys
    new_music_volume = music_volume
    new_sounds = sound_effects
    text = ""

    for key_number, key in enumerate(new_keys):
        if key == K_UP:
            key_string = "Up"
        elif key == K_DOWN:
            key_string = "Down"
        elif key == K_LEFT:
            key_string = "Left"
        elif key == K_RIGHT:
            key_string = "Right"
        elif key == K_RETURN:
            key_string = "Enter"
        elif key == K_BACKSPACE:
            key_string = "Backspace"
        else:
            key_string = chr(key)

        if key_number == 0:
            buttons.append(Button([58, 25 + height / 2, 350, 50], "Move up: " + key_string, small_font))
        if key_number == 1:
            buttons.append(Button([58, 100 + height / 2, 350, 50], "Move down: " + key_string, small_font))
        if key_number == 2:
            buttons.append(Button([58, 175 + height / 2, 350, 50], "Move left: " + key_string, small_font))
        if key_number == 3:
            buttons.append(Button([58, 250 + height / 2, 350, 50], "Move right: " + key_string, small_font))
        if key_number == 4:
            buttons.append(Button([465, 25 + height / 2, 350, 50], "Hand forward: " + key_string, small_font))
        if key_number == 5:
            buttons.append(Button([465, 100 + height / 2, 350, 50], "Hand backward: " + key_string, small_font))
        if key_number == 6:
            buttons.append(Button([465, 175 + height / 2, 350, 50], "Hand left: " + key_string, small_font))
        if key_number == 7:
            buttons.append(Button([465, 250 + height / 2, 350, 50], "Hand right: " + key_string, small_font))
        if key_number == 8:
            buttons.append(Button([872, 25 + height / 2, 350, 50], "Use lightsaber: " + key_string, small_font))
        if key_number == 9:
            buttons.append(Button([872, 100 + height / 2, 350, 50], "Use energy shield: " + key_string, small_font))
        if key_number == 10:
            buttons.append(Button([872, 175 + height / 2, 350, 50], "Use health pack: " + key_string, small_font))
        if key_number == 11:
            buttons.append(Button([872, 250 + height / 2, 350, 50], "Pause game: " + key_string, small_font))
    
    while True:
        window.fill((255, 255, 255))
        mouse_pos = pygame.mouse.get_pos()
        if music_channel.get_busy() == False and action == "Menu":
            music_channel.play(music, -1)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_down = True
                if event.button == 1:
                    for button in buttons:
                        if button.rect[0] <= mouse_pos[0] <= button.rect[0] + button.rect[2] and button.rect[1] <= mouse_pos[1] <= button.rect[1] + button.rect[3]:
                            button.pressed = True
                            selected_button = button
            if event.type == pygame.MOUSEBUTTONUP:
                mouse_down = False
                if event.button == 1:
                    for key_number, button in enumerate(buttons[3:]):
                        if button.rect[0] <= mouse_pos[0] <= button.rect[0] + button.rect[2] and button.rect[1] <= mouse_pos[1] <= button.rect[1] + button.rect[3]:
                            button.pressed = False
                            if selected_button != None:
                                if selected_button == button:
                                    selected_key = key_number + 3
                    if buttons[0].rect[0] <= mouse_pos[0] <= buttons[0].rect[0] + buttons[0].rect[2] and buttons[0].rect[1] <= mouse_pos[1] <= buttons[0].rect[1] + buttons[0].rect[3]:
                        buttons[0].pressed = False
                        if selected_button != None:
                            if selected_button == buttons[0]:
                                return new_keys, new_music_volume, new_sounds
                    if buttons[1].rect[0] <= mouse_pos[0] <= buttons[1].rect[0] + buttons[1].rect[2] and buttons[1].rect[1] <= mouse_pos[1] <= buttons[1].rect[1] + buttons[1].rect[3]:
                        buttons[1].pressed = False
                        if selected_button != None:
                            if selected_button == buttons[1]:
                                if new_music_volume == 1:
                                    new_music_volume = 0
                                    text = "Music will be turned off.  Press back to activate."
                                else:
                                    new_music_volume = 1
                                    text = "Music will be turned on.  Press back to activate."
                    if buttons[2].rect[0] <= mouse_pos[0] <= buttons[2].rect[0] + buttons[2].rect[2] and buttons[2].rect[1] <= mouse_pos[1] <= buttons[2].rect[1] + buttons[2].rect[3]:
                        buttons[2].pressed = False
                        if selected_button != None:
                            if selected_button == buttons[2]:
                                if new_sounds == True:
                                    new_sounds = False
                                    text = "Sound effects will be turned off.  Press back to activate."
                                else:
                                    new_sounds = True
                                    text = "Sound effects will be turned on.  Press back to activate."
                                        
                        else:
                            selected_button = None
            if event.type == KEYDOWN:
                if selected_key != None:
                    for key_number, key in enumerate(buttons):
                        if key == buttons[selected_key]:
                            new_keys[key_number - 3] = event.key
                    if event.key == K_UP:
                        key_string = "Up"
                    elif event.key == K_DOWN:
                        key_string = "Down"
                    elif event.key == K_LEFT:
                        key_string = "Left"
                    elif event.key == K_RIGHT:
                        key_string = "Right"
                    elif event.key == K_RETURN:
                        key_string = "Enter"
                    elif event.key == K_BACKSPACE:
                        key_string = "Backspace"
                    else:
                        key_string = chr(event.key)
                    if selected_key == 3:
                        text = "Move up is set to " + key_string
                        buttons[3].text = "Move up: " + key_string
                    if selected_key == 4:
                        text = "Move down is set to " + key_string
                        buttons[4].text = "Move down: " + key_string
                    if selected_key == 5:
                        text = "Move left is set to " + key_string
                        buttons[5].text = "Move left: " + key_string
                    if selected_key == 6:
                        text = "Move right is set to " + key_string
                        buttons[6].text = "Move right: " + key_string
                    if selected_key == 7:
                        text = "Move hand forward is set to " + key_string
                        buttons[7].text = "Hand forward: " + key_string
                    if selected_key == 8:
                        text = "Move hand backward is set to " + key_string
                        buttons[8].text = "Hand backward: " + key_string
                    if selected_key == 9:
                        text = "Move hand left is set to " + key_string
                        buttons[9].text = "Hand left: " + key_string
                    if selected_key == 10:
                        text = "Move hand right is set to " + key_string
                        buttons[10].text = "Hand right: " + key_string
                    if selected_key == 11:
                        text = "Weapon 1 is set to " + key_string
                        buttons[11].text = "Use lightsaber: " + key_string
                    if selected_key == 12:
                        text = "Weapon 2 is set to " + key_string
                        buttons[12].text = "Use energy shield: " + key_string
                    if selected_key == 13:
                        text = "Use health pack is set to " + key_string
                        buttons[13].text = "Use health pack: " + key_string
                    if selected_key == 14:
                        text = "Pause game is set to " + key_string
                        buttons[14].text = "Pause game: " + key_string
                    selected_key = None

        Draw_text(window, (0, 0, 0), large_font, [width / 2, height / 6], "Settings")
        Draw_text(window, (0, 0, 0), small_font, [width / 2, 5 * height / 6 + 50], text)
        if selected_key != None:
            pygame.draw.rect(window, (0, 0, 255), [buttons[selected_key].rect[0] - 5, buttons[selected_key].rect[1] - 5, 360, 60], 5)

        for button in buttons:
            if button == buttons[1]:
                if new_music_volume == 0:
                    button.text = "Music: Off"
                else:
                    button.text = "Music: On"
            if button == buttons[2]:
                if new_sounds == False:
                    button.text = "Sounds: Off"
                else:
                    button.text = "Sounds: On"
            if selected_button == button and mouse_down == True:
                if button.rect[0] <= mouse_pos[0] <= button.rect[0] + button.rect[2] and button.rect[1] <= mouse_pos[1] <= button.rect[1] + button.rect[3]:
                    button.pressed = True
                else:
                    button.pressed = False
            button.display()

        pygame.display.flip()
        clock.tick(FPS)

#------------------------------------------------------------------------Use Cheats------------------------------------------------------------------------
def Cheats():
    player_input = ""
    final_player_input = ""

    new_infinite_money = infinite_money     #"im rich": Grants infinite money
    new_god_mode = god_mode                 #"god mode": Infinite health and damage
    new_music_mix = music_mix               #"mixer.mix": Randomizes music
    new_vision = vision                     #"hyperopia": Draws a large circle around player to obstruct vision nearby vision
                                            #"myopia": Draws a ring and four rectangles around player to obstruct far vision
                                            #"glasses": Makes vision normal
                                            #"help": Lists all cheats
    new_wave = wave                         #"wave=" + #: Sets wave number to #
    text = []
    buttons = [Button([0, 0, 100, 50], "Back", small_font), Button([width / 2 - 75, height / 5 + 100, 150, 75], "Enter", small_font)]
    selected_button = None
    mouse_down = False
    while True:
        window.fill((255, 255, 255))
        mouse_pos = pygame.mouse.get_pos()
        if music_channel.get_busy() == False and action == "Menu":
            music_channel.play(music, -1)
            music_channel.set_volume(music_volume)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == 8:
                    if player_input != "":
                        player_input = player_input[0:-1]
                elif event.key == 13:
                    final_player_input = player_input
                    if final_player_input == "help":
                        text = ["All cheats:", "\"help\": Lists all cheat codes", "\"wave=#\": Sets the wave number to #", "\"im rich\": Activates infinite money", "\"god mode\": Activates god mode: Infinite player health and damage", "\"mixer.mix\": Randomizes all music", "\"hyperopia\": Gives player hyperopia (can only see far)", "\"myopia\": Gives player myopia (can only see close)", "\"glasses\": Gives player normal vision"]
                    elif final_player_input[0:5] == "wave=":
                        try:
                            new_wave = int(final_player_input[5:])
                            text = ["Wave number is set to " + str(new_wave) + "!"]
                        except ValueError:
                            text = ["Invalid code"]
                    elif final_player_input == "im rich":
                        if new_infinite_money == False:
                            new_infinite_money = True
                            text = ["You now have infinite money!"]
                        else:
                            new_infinite_money = False
                            text = ["You now have limited money!"]
                    elif final_player_input == "god mode":
                        if new_god_mode == False:
                            new_god_mode = True
                            text = ["You are now in god mode!"]
                        else:
                            new_god_mode = False
                            text = ["You are now mortal!"]
                    elif final_player_input == "mixer.mix":
                        if new_music_mix == False:
                            new_music_mix = True
                            text = ["Music is randomized!"]
                        else:
                            new_music_mix = False
                            text = ["Music is normal!"]
                    elif final_player_input == "hyperopia":
                        new_vision = "hyperopia"
                        text = ["You now have hyperopia!"]
                    elif final_player_input == "myopia":
                        new_vision = "myopia"
                        text = ["You now have myopia!"]
                    elif final_player_input == "glasses":
                        new_vision = "normal"
                        text = ["You now have normal vision!"]
                    else:
                        text = ["Invalid code"]
                    player_input = ""
                else:
                    player_input += chr(event.key)
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_down = True
                if event.button == 1:
                    for button in buttons:
                        if button.rect[0] <= mouse_pos[0] <= button.rect[0] + button.rect[2] and button.rect[1] <= mouse_pos[1] <= button.rect[1] + button.rect[3]:
                            button.pressed = True
                            selected_button = button
            if event.type == pygame.MOUSEBUTTONUP:
                mouse_down = False
                if event.button == 1:
                    if buttons[0].rect[0] <= mouse_pos[0] <= buttons[0].rect[0] + buttons[0].rect[2] and buttons[0].rect[1] <= mouse_pos[1] <= buttons[0].rect[1] + buttons[0].rect[3]:
                        buttons[0].pressed = False
                        if selected_button != None:
                            if selected_button == buttons[0]:
                                return new_infinite_money, new_god_mode, new_music_mix, new_vision, new_wave
                    elif buttons[1].rect[0] <= mouse_pos[0] <= buttons[1].rect[0] + buttons[1].rect[2] and buttons[1].rect[1] <= mouse_pos[1] <= buttons[1].rect[1] + buttons[1].rect[3]:
                        buttons[1].pressed = False
                        if selected_button != None:
                            if selected_button == buttons[1]:
                                final_player_input = player_input
                                if final_player_input == "help":
                                    text = ["All cheats:", "\"help\": Lists all cheat codes", "\"wave=#\": Sets the wave number to #", "\"im rich\": Activates infinite money", "\"god mode\": Activates god mode: Infinite player health and damage", "\"mixer.mix\": Randomizes all music", "\"hyperopia\": Gives player hyperopia (can only see far)", "\"myopia\": Gives player myopia (can only see close)", "\"glasses\": Gives player normal vision"]
                                elif final_player_input[0:5] == "wave=":
                                    try:
                                        new_wave = int(final_player_input[5:])
                                        text = ["Wave number is set to " + str(new_wave) + "!"]
                                    except ValueError:
                                        text = ["Invalid code"]
                                elif final_player_input == "im rich":
                                    if new_infinite_money == False:
                                        new_infinite_money = True
                                        text = ["You now have infinite money!"]
                                    else:
                                        new_infinite_money = False
                                        text = ["You now have limited money!"]
                                elif final_player_input == "god mode":
                                    if new_god_mode == False:
                                        new_god_mode = True
                                        text = ["You are now in god mode!"]
                                    else:
                                        new_god_mode = False
                                        text = ["You are now mortal!"]
                                elif final_player_input == "mixer.mix":
                                    if new_music_mix == False:
                                        new_music_mix = True
                                        text = ["Music is randomized!"]
                                    else:
                                        new_music_mix = False
                                        text = ["Music is normal!"]
                                elif final_player_input == "hyperopia":
                                    new_vision = "hyperopia"
                                    text = ["You now have hyperopia!"]
                                elif final_player_input == "myopia":
                                    new_vision = "myopia"
                                    text = ["You now have myopia!"]
                                elif final_player_input == "glasses":
                                    new_vision = "normal"
                                    text = ["You now have normal vision!"]
                                else:
                                    text = ["Invalid code"]
                                player_input = ""
                    else:
                        selected_button = None

        pygame.draw.rect(window, (0, 0, 0), [50, height / 5 - 25, width - 100, 50], 5)
        Draw_text(window, (0, 0, 0), small_font, [width / 2, height / 5], player_input)
        for line_number, line in enumerate(text):
            Draw_text(window, (0, 0, 0), small_font, [width / 2, 2 * height / 3 + 25 * line_number], line)
        for button in buttons:
            if selected_button == button and mouse_down == True:
                if button.rect[0] <= mouse_pos[0] <= button.rect[0] + button.rect[2] and button.rect[1] <= mouse_pos[1] <= button.rect[1] + button.rect[3]:
                    button.pressed = True
                else:
                    button.pressed = False
            button.display()

        pygame.display.flip()
        clock.tick(FPS)

#-----------------------------------------------------------------------Define classes----------------------------------------------------------------------
#-----------------------------------Enemies-----------------------------------
#A sniper enemy who fires lasers accurately
class Laser_sniper:
    def __init__(self, pos, direction, health, max_health, team):
        self.pos = pos
        self.direction = direction
        self.health = health * difficulty
        self.max_health = max_health * difficulty
        self.team = team
        self.reload = 0
        self.moving = False
    def move_shoot(self, target):
        self.moving = False
        last_pos = [self.pos[0], self.pos[1]]
        distance_to_target = hypot(self.pos[0] - target[0], self.pos[1] - target[1])
        self.direction = atan2(target[1] - self.pos[1], target[0] - self.pos[0])
        if distance_to_target > 750:
            self.pos = [self.pos[0] + cos(self.direction) * 3 * difficulty, self.pos[1] + sin(self.direction) * 3 * difficulty]
            if self.pos[0] < 25:
                self.pos[0] = 25
            if self.pos[0] > width - 25:
                self.pos[0] = width - 25
            if self.pos[1] < 25:
                self.pos[1] = 25
            if self.pos[1] > height - 25:
                self.pos[1] = height - 25
            if hypot(self.pos[0] - last_pos[0], self.pos[1] - last_pos[1]) >= 1:
                self.moving = True
        if distance_to_target < 250:
            self.pos = [self.pos[0] - cos(self.direction) * 3 * difficulty, self.pos[1] - sin(self.direction) * 3 * difficulty]
            if self.pos[0] < 25:
                self.pos[0] = 25
            if self.pos[0] > width - 25:
                self.pos[0] = width - 25
            if self.pos[1] < 25:
                self.pos[1] = 25
            if self.pos[1] > height - 25:
                self.pos[1] = height - 25
            if hypot(self.pos[0] - last_pos[0], self.pos[1] - last_pos[1]) >= 1:
                self.moving = True

        if self.moving == True:
            aim_offset = random.uniform(-25 * pi / 180, 25 * pi / 180)
        else:
            aim_offset = random.uniform(-1 * pi / 180, 1 * pi / 180)
        self.direction += aim_offset
        self.reload += 1
        if self.reload >= 120 / difficulty:
            lasers.append(Laser([self.pos[0] + cos(self.direction - aim_offset) * 75, self.pos[1] + sin(self.direction - aim_offset) * 75], [self.pos[0] + cos(self.direction) * 10000, self.pos[1] + sin(self.direction) * 10000], 3, 25 * difficulty, True, self.team))
            self.reload = 0
        self.direction -= aim_offset
    def display(self):
        if self.team == "red":
            colour = (255, 0, 0)
        if self.team == "green":
            colour = (0, 255, 0)
        if self.team == "blue":
            colour = (0, 0, 255)
        pygame.draw.polygon(window, (0, 0, 0), Rotate_clockwise([[int(self.pos[0]), int(self.pos[1] + 2)], [int(self.pos[0]), int(self.pos[1] - 2)], [int(self.pos[0] + 75), int(self.pos[1] - 2)], [int(self.pos[0] + 75), int(self.pos[1] + 2)]], self.pos, self.direction), 3)
        pygame.draw.circle(window, colour, [int(self.pos[0]), int(self.pos[1])], 25)
        pygame.draw.rect(window, (255, 0, 0), [int(self.pos[0] - 25), int(self.pos[1] - 35), 50, 5])
        pygame.draw.rect(window, (0, 255, 0), [int(self.pos[0] - 25), int(self.pos[1] - 35), self.health * 50 / self.max_health, 5])

#A rapid-fire laser gunner that only shoots when standing still
class Laser_gunner:
    def __init__(self, pos, direction, health, max_health, team):
        self.pos = pos
        self.direction = direction
        self.health = health * difficulty
        self.max_health = max_health * difficulty
        self.team = team
        self.reload = 0
        self.moving = False
    def move_shoot(self, target):
        self.moving = False
        last_pos = [self.pos[0], self.pos[1]]
        distance_to_target = hypot(self.pos[0] - target[0], self.pos[1] - target[1])
        self.direction = atan2(target[1] - self.pos[1], target[0] - self.pos[0])
        if distance_to_target > 500:
            self.pos = [self.pos[0] + cos(self.direction) * 3 * difficulty, self.pos[1] + sin(self.direction) * 3 * difficulty]
            if self.pos[0] < 25:
                self.pos[0] = 25
            if self.pos[0] > width - 25:
                self.pos[0] = width - 25
            if self.pos[1] < 25:
                self.pos[1] = 25
            if self.pos[1] > height - 25:
                self.pos[1] = height - 25
            if hypot(self.pos[0] - last_pos[0], self.pos[1] - last_pos[1]) >= 1:
                self.moving = True
        if distance_to_target < 150:
            self.pos = [self.pos[0] - cos(self.direction) * 3 * difficulty, self.pos[1] - sin(self.direction) * 3 * difficulty]
            if self.pos[0] < 25:
                self.pos[0] = 25
            if self.pos[0] > width - 25:
                self.pos[0] = width - 25
            if self.pos[1] < 25:
                self.pos[1] = 25
            if self.pos[1] > height - 25:
                self.pos[1] = height - 25
            if hypot(self.pos[0] - last_pos[0], self.pos[1] - last_pos[1]) >= 1:
                self.moving = True

        if self.moving == False:
            aim_offset = random.uniform(-2 * pi / 180, 2 * pi / 180)
            self.reload += 1
            self.direction += aim_offset
            if self.reload >= 1:
                lasers.append(Laser([self.pos[0] + cos(self.direction) * 75, self.pos[1] + sin(self.direction) * 75], [self.pos[0] + cos(self.direction) * 10000, self.pos[1] + sin(self.direction) * 10000], 1, 100 / 60 * difficulty, False, self.team))
                self.reload = 0
            self.direction -= aim_offset
    def display(self):
        if self.team == "red":
            colour = (255, 0, 0)
        if self.team == "green":
            colour = (0, 255, 0)
        if self.team == "blue":
            colour = (0, 0, 255)
        pygame.draw.polygon(window, (0, 0, 0), Rotate_clockwise([[int(self.pos[0]), int(self.pos[1] + 2)], [int(self.pos[0]), int(self.pos[1] - 2)], [int(self.pos[0] + 75), int(self.pos[1] - 2)], [int(self.pos[0] + 75), int(self.pos[1] + 2)]], self.pos, self.direction), 3)
        pygame.draw.circle(window, colour, [int(self.pos[0]), int(self.pos[1])], 25)
        pygame.draw.rect(window, (255, 0, 0), [int(self.pos[0] - 25), int(self.pos[1] - 35), 50, 5])
        pygame.draw.rect(window, (0, 255, 0), [int(self.pos[0] - 25), int(self.pos[1] - 35), self.health * 50 / self.max_health, 5])

#A gunman who fires bullets somewhat accurately
class Rifleman:
    def __init__(self, pos, direction, health, max_health, fire, team):
        self.pos = pos
        self.direction = direction
        self.health = health * difficulty
        self.max_health = max_health * difficulty
        self.fire = fire
        self.team = team
        self.ammunition = 10
        self.reload = 0
        self.moving = False
    def move_shoot(self, target):
        self.moving = False
        last_pos = [self.pos[0], self.pos[1]]
        distance_to_target = hypot(self.pos[0] - target[0], self.pos[1] - target[1])
        self.direction = atan2(target[1] - self.pos[1], target[0] - self.pos[0])
        if distance_to_target > 600:
            self.pos = [self.pos[0] + cos(self.direction) * 3 * difficulty, self.pos[1] + sin(self.direction) * 3 * difficulty]
            if self.pos[0] < 25:
                self.pos[0] = 25
            if self.pos[0] > width - 25:
                self.pos[0] = width - 25
            if self.pos[1] < 25:
                self.pos[1] = 25
            if self.pos[1] > height - 25:
                self.pos[1] = height - 25
            if hypot(self.pos[0] - last_pos[0], self.pos[1] - last_pos[1]) >= 1:
                self.moving = True
        if distance_to_target < 300:
            self.pos = [self.pos[0] - cos(self.direction) * 3 * difficulty, self.pos[1] - sin(self.direction) * 3 * difficulty]
            if self.pos[0] < 25:
                self.pos[0] = 25
            if self.pos[0] > width - 25:
                self.pos[0] = width - 25
            if self.pos[1] < 25:
                self.pos[1] = 25
            if self.pos[1] > height - 25:
                self.pos[1] = height - 25
            if hypot(self.pos[0] - last_pos[0], self.pos[1] - last_pos[1]) >= 1:
                self.moving = True

        if self.moving == True:
            aim_offset = random.uniform(-15 * pi / 180, 15 * pi / 180)
        else:
            aim_offset = random.uniform(-5 * pi / 180, 5 * pi / 180)
        self.direction += aim_offset
        self.fire += 1
        if self.reload == 0:
            if self.ammunition > 0:
                if self.fire >= 30 / difficulty:
                    bullets.append(Bullet([self.pos[0] + cos(self.direction) * 50, self.pos[1] + sin(self.direction) * 50], self.direction, 25, 20 * difficulty, self.team))
                    if sound_effects == True:
                        gunshot_sound.play()
                    self.fire = 0
                    self.ammunition -= 1
            else:
                self.reload = 180 / difficulty
        else:
            self.reload -= 1
            if self.reload == 0:
                self.ammunition = 10
        self.direction -= aim_offset
    def display(self):
        if self.team == "red":
            colour = (255, 0, 0)
        if self.team == "green":
            colour = (0, 255, 0)
        if self.team == "blue":
            colour = (0, 0, 255)
        pygame.draw.polygon(window, (0, 0, 0), Rotate_clockwise([[int(self.pos[0]), int(self.pos[1] + 3)], [int(self.pos[0]), int(self.pos[1] - 3)], [int(self.pos[0] + 50), int(self.pos[1] - 3)], [int(self.pos[0] + 50), int(self.pos[1] + 3)]], self.pos, self.direction), 3)
        pygame.draw.circle(window, colour, [int(self.pos[0]), int(self.pos[1])], 25)
        pygame.draw.rect(window, (255, 0, 0), [int(self.pos[0] - 25), int(self.pos[1] - 35), 50, 5])
        pygame.draw.rect(window, (0, 255, 0), [int(self.pos[0] - 25), int(self.pos[1] - 35), self.health * 50 / self.max_health, 5])

#A gunman who rapidly fires bullets, but inaccurately
class Machine_gunner:
    def __init__(self, pos, direction, health, max_health, fire, team):
        self.pos = pos
        self.direction = direction
        self.health = health * difficulty
        self.max_health = max_health * difficulty
        self.fire = fire
        self.team = team
        self.ammunition = 30
        self.reload = 0
        self.moving = False
    def move_shoot(self, target):
        self.moving = False
        last_pos = [self.pos[0], self.pos[1]]
        distance_to_target = hypot(self.pos[0] - target[0], self.pos[1] - target[1])
        self.direction = atan2(target[1] - self.pos[1], target[0] - self.pos[0])
        if distance_to_target > 400:
            self.pos = [self.pos[0] + cos(self.direction) * 3 * difficulty, self.pos[1] + sin(self.direction) * 3 * difficulty]
            if self.pos[0] < 25:
                self.pos[0] = 25
            if self.pos[0] > width - 25:
                self.pos[0] = width - 25
            if self.pos[1] < 25:
                self.pos[1] = 25
            if self.pos[1] > height - 25:
                self.pos[1] = height - 25
            if hypot(self.pos[0] - last_pos[0], self.pos[1] - last_pos[1]) >= 1:
                self.moving = True
        if distance_to_target < 200:
            self.pos = [self.pos[0] - cos(self.direction) * 3 * difficulty, self.pos[1] - sin(self.direction) * 3 * difficulty]
            if self.pos[0] < 25:
                self.pos[0] = 25
            if self.pos[0] > width - 25:
                self.pos[0] = width - 25
            if self.pos[1] < 25:
                self.pos[1] = 25
            if self.pos[1] > height - 25:
                self.pos[1] = height - 25
            if hypot(self.pos[0] - last_pos[0], self.pos[1] - last_pos[1]) >= 1:
                self.moving = True

        if self.moving == True:
            aim_offset = random.uniform(-15 * pi / 180, 15 * pi / 180)
        else:
            aim_offset = random.uniform(-7 * pi / 180, 7 * pi / 180)
        self.direction += aim_offset
        self.fire += 1
        if self.reload == 0:
            if self.ammunition > 0:
                if self.fire >= 6 / difficulty:
                    bullets.append(Bullet([self.pos[0] + cos(self.direction) * 50, self.pos[1] + sin(self.direction) * 50], self.direction, 20, 10 * difficulty, self.team))
                    if sound_effects == True:
                        gunshot_sound.play()
                    self.fire = 0
                    self.ammunition -= 1
            else:
                self.reload = 180 / difficulty
        else:
            self.reload -= 1
            if self.reload == 0:
                self.ammunition = 30
        self.direction -= aim_offset
    def display(self):
        if self.team == "red":
            colour = (255, 0, 0)
        if self.team == "green":
            colour = (0, 255, 0)
        if self.team == "blue":
            colour = (0, 0, 255)
        pygame.draw.polygon(window, (0, 0, 0), Rotate_clockwise([[int(self.pos[0]), int(self.pos[1] + 5)], [int(self.pos[0]), int(self.pos[1] - 5)], [int(self.pos[0] + 50), int(self.pos[1] - 5)], [int(self.pos[0] + 50), int(self.pos[1] + 5)]], self.pos, self.direction), 3)
        pygame.draw.circle(window, colour, [int(self.pos[0]), int(self.pos[1])], 25)
        pygame.draw.rect(window, (255, 0, 0), [int(self.pos[0] - 25), int(self.pos[1] - 35), 50, 5])
        pygame.draw.rect(window, (0, 255, 0), [int(self.pos[0] - 25), int(self.pos[1] - 35), self.health * 50 / self.max_health, 5])

#A soldier that slowly launches rockets, but only when standing still
class Rocket_launcher:
    def __init__(self, pos, direction, health, max_health, team):
        self.pos = pos
        self.direction = direction
        self.health = health * difficulty
        self.max_health = max_health * difficulty
        self.team = team
        self.reload = 0
        self.moving = False
    def move_shoot(self, target):
        self.moving = False
        last_pos = [self.pos[0], self.pos[1]]
        distance_to_target = hypot(self.pos[0] - target[0], self.pos[1] - target[1])
        self.direction = atan2(target[1] - self.pos[1], target[0] - self.pos[0])
        if distance_to_target > 750:
            self.pos = [self.pos[0] + cos(self.direction) * 2 * difficulty, self.pos[1] + sin(self.direction) * 2 * difficulty]
            if self.pos[0] < 25:
                self.pos[0] = 25
            if self.pos[0] > width - 25:
                self.pos[0] = width - 25
            if self.pos[1] < 25:
                self.pos[1] = 25
            if self.pos[1] > height - 25:
                self.pos[1] = height - 25
            if hypot(self.pos[0] - last_pos[0], self.pos[1] - last_pos[1]) >= 1:
                self.moving = True
        if distance_to_target < 250:
            self.pos = [self.pos[0] - cos(self.direction) * 2 * difficulty, self.pos[1] - sin(self.direction) * 2 * difficulty]
            if self.pos[0] < 25:
                self.pos[0] = 25
            if self.pos[0] > width - 25:
                self.pos[0] = width - 25
            if self.pos[1] < 25:
                self.pos[1] = 25
            if self.pos[1] > height - 25:
                self.pos[1] = height - 25
            if hypot(self.pos[0] - last_pos[0], self.pos[1] - last_pos[1]) >= 1:
                self.moving = True

        self.reload += 1
        if self.moving == False:
            aim_offset = random.uniform(-2 * pi / 180, 2 * pi / 180)
            self.direction += aim_offset
            if self.reload >= 300 / difficulty:
                rockets.append(Rocket([self.pos[0] + cos(self.direction) * 75, self.pos[1] + sin(self.direction) * 75], self.direction, 5, 75, "red"))
                self.reload = 0
            self.direction -= aim_offset
    def display(self):
        if self.team == "red":
            colour = (255, 0, 0)
        if self.team == "green":
            colour = (0, 255, 0)
        if self.team == "blue":
            colour = (0, 0, 255)
        pygame.draw.polygon(window, (0, 0, 0), Rotate_clockwise([[int(self.pos[0]), int(self.pos[1] + 7)], [int(self.pos[0]), int(self.pos[1] - 7)], [int(self.pos[0] + 75), int(self.pos[1] - 7)], [int(self.pos[0] + 75), int(self.pos[1] + 7)]], self.pos, self.direction), 3)
        pygame.draw.circle(window, colour, [int(self.pos[0]), int(self.pos[1])], 25)
        pygame.draw.rect(window, (255, 0, 0), [int(self.pos[0] - 25), int(self.pos[1] - 35), 50, 5])
        pygame.draw.rect(window, (0, 255, 0), [int(self.pos[0] - 25), int(self.pos[1] - 35), self.health * 50 / self.max_health, 5])

#---------------------------------Projectiles---------------------------------
#Bullet
class Bullet:
    def __init__(self, pos, direction, speed, damage, team):
        self.pos = pos
        self.direction = direction
        self.speed = speed * difficulty
        self.damage = damage
        self.team = team
        self.last_pos = pos
        self.health = 2
    def move(self):
        self.last_pos = [self.pos[0], self.pos[1]]
        self.pos[0] += cos(self.direction) * self.speed
        self.pos[1] += sin(self.direction) * self.speed
    def display(self):
        if self.team == "red":
            colour = (255, 0, 0)
        elif self.team == "green":
            colour = (0, 255, 0)
        elif self.team == "blue":
            colour = (0, 0, 255)
        pygame.draw.circle(window, colour, [int(self.pos[0]), int(self.pos[1])], 5)

#Laser
class Laser:
    def __init__(self, start_pos, end_pos, max_time, damage, penetrate, team):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.max_time = max_time
        self.damage = damage
        self.penetrate = penetrate
        self.team = team
        self.timer = 0
    def display(self):
        if self.team == "red":
            colour = (255, 0, 0)
        elif self.team == "green":
            colour = (0, 255, 0)
        elif self.team == "blue":
            colour = (0, 0, 255)
        pygame.draw.line(window, colour, self.start_pos, self.end_pos, 3)

class PD_laser:
    def __init__(self, start_pos, end_pos, damage, team):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.damage = damage
        self.team = team
        self.timer = 0
    def display(self):
        if self.team == "red":
            colour = (255, 0, 0)
        elif self.team == "green":
            colour = (0, 255, 0)
        elif self.team == "blue":
            colour = (0, 0, 255)
        pygame.draw.line(window, colour, self.start_pos, self.end_pos, 1)

#Rocket - cannot be deflected
class Rocket:
    def __init__(self, pos, direction, speed, damage, team):
        self.pos = pos
        self.direction = direction
        self.speed = speed * difficulty
        self.damage = damage
        self.team = team
        self.perimeter = Rotate_clockwise([[self.pos[0] - 10, self.pos[1] - 5], [self.pos[0] - 10, self.pos[1] + 5], [self.pos[0] + 10, self.pos[1] + 5], [self.pos[0] + 15, self.pos[1]], [self.pos[0] + 10, self.pos[1] - 5]], self.pos, self.direction)
        self.explode = False
        self.health = 10
    def move(self):
        self.pos[0] += cos(self.direction) * self.speed
        self.pos[1] += sin(self.direction) * self.speed
        self.direction += random.uniform(-3 * pi / 180, 3 * pi / 180)
        self.speed += 0.1 * difficulty
        self.perimeter = Rotate_clockwise([[self.pos[0] - 10, self.pos[1] - 5], [self.pos[0] - 10, self.pos[1] + 5], [self.pos[0] + 10, self.pos[1] + 5], [self.pos[0] + 15, self.pos[1]], [self.pos[0] + 10, self.pos[1] - 5]], self.pos, self.direction)
    def display(self):
        if self.team == "red":
            colour = (255, 0, 0)
        elif self.team == "green":
            colour = (0, 255, 0)
        elif self.team == "blue":
            colour = (0, 0, 255)
        pygame.draw.polygon(window, colour, Rotate_clockwise([[self.pos[0] - 10, self.pos[1] - 5], [self.pos[0] - 10, self.pos[1] + 5], [self.pos[0] + 10, self.pos[1] + 5], [self.pos[0] + 10, self.pos[1] - 5]], self.pos, self.direction))
        pygame.draw.polygon(window, (0, 0, 0), Rotate_clockwise([[self.pos[0] - 10, self.pos[1] - 5], [self.pos[0] - 10, self.pos[1] + 5], [self.pos[0] + 10, self.pos[1] + 5], [self.pos[0] + 10, self.pos[1] - 5]], self.pos, self.direction), 1)
        pygame.draw.polygon(window, colour, Rotate_clockwise([[self.pos[0] - 10, self.pos[1] - 10], [self.pos[0] - 10, self.pos[1] + 10], [self.pos[0], self.pos[1]]], self.pos, self.direction))
        pygame.draw.polygon(window, (0, 0, 0), Rotate_clockwise([[self.pos[0] - 10, self.pos[1] - 10], [self.pos[0] - 10, self.pos[1] + 10], [self.pos[0] + 5, self.pos[1]]], self.pos, self.direction), 1)
        pygame.draw.polygon(window, colour, Rotate_clockwise([[self.pos[0] + 10, self.pos[1] - 5], [self.pos[0] + 10, self.pos[1] + 5], [self.pos[0] + 15, self.pos[1]]], self.pos, self.direction))
        pygame.draw.polygon(window, (0, 0, 0), Rotate_clockwise([[self.pos[0] + 10, self.pos[1] - 5], [self.pos[0] + 10, self.pos[1] + 5], [self.pos[0] + 15, self.pos[1]]], self.pos, self.direction), 1)

#---------------------------------Shop Items---------------------------------
#Trip mine
class Mine:
    def __init__(self, pos, team):
        self.pos = pos
        self.team = team
        self.explode = False
        self.timer = -300
    def trigger(self):
        if self.timer < 0:
            self.timer += difficulty
        if self.timer == -difficulty and sound_effects == True:
            mine_beep.play()
        if self.explode == True:
            self.timer += difficulty
            if ((self.timer - 5) % 10 <= 0.25 or (self.timer - 5) % 10 >= 9.75) and sound_effects == True:
                mine_beep.play()
    def display(self):
        if self.team == "red":
            colour = (255, 0, 0)
        if self.team == "green":
            colour = (0, 255, 0)
        if self.team == "blue":
            colour = (0, 0, 255)
        pygame.draw.circle(window, (128, 128, 128), [int(self.pos[0]), int(self.pos[1])], 15)
        if (self.timer // 5 % 2 == 1 and self.timer >= 0) or -1 <= self.timer < 0:
            pygame.draw.circle(window, (255, 255, 255), [int(self.pos[0]), int(self.pos[1])], 5)
        else:
            pygame.draw.circle(window, colour, [int(self.pos[0]), int(self.pos[1])], 5)

#Point defence laser that shoots down projectiles
class Point_defence:
    def __init__(self, pos, direction, team):
        self.pos = pos
        self.direction = direction
        self.team = team
        self.health = 50
        self.timer = -450
        self.target = None
    def shoot(self):
        self.timer += difficulty
        if self.target != None:
            if self.timer >= 0:
                if self.target == "player":
                    self.direction = atan2(player_pos[1] - self.pos[1], player_pos[0] - self.pos[0])
                    if hypot(player_pos[0] - self.pos[0], player_pos[1] - self.pos[1]) <= 250:
                        pd_lasers.append(PD_laser(Rotate_clockwise([[self.pos[0] + 35, self.pos[1]]], self.pos, self.direction)[0], [player_pos[0] + cos(self.direction) * 10000, player_pos[1] + sin(self.direction) * 10000], 30 / 60, self.team))
                else:
                    self.direction = atan2(self.target.pos[1] - self.pos[1], self.target.pos[0] - self.pos[0])
                    if hypot(self.target.pos[0] - self.pos[0], self.target.pos[1] - self.pos[1]) <= 250:
                        pd_lasers.append(PD_laser(Rotate_clockwise([[self.pos[0] + 35, self.pos[1]]], self.pos, self.direction)[0], [self.target.pos[0] + cos(self.direction) * 10000, self.target.pos[1] + sin(self.direction) * 10000], 30 / 60, self.team))
    def display(self):
        if self.team == "red":
            colour = (255, 0, 0)
        if self.team == "green":
            colour = (0, 255, 0)
        if self.team == "blue":
            colour = (0, 0, 255)
        pygame.draw.circle(window, colour, [int(Rotate_clockwise([[self.pos[0] + 20, self.pos[1]]], self.pos, pi / 2)[0][0]), int(Rotate_clockwise([[self.pos[0] + 20, self.pos[1]]], self.pos, pi / 2)[0][1])], 7)
        pygame.draw.circle(window, colour, [int(Rotate_clockwise([[self.pos[0] + 20, self.pos[1]]], self.pos, 11 * pi / 6)[0][0]), int(Rotate_clockwise([[self.pos[0] + 20, self.pos[1]]], self.pos, 11 * pi / 6)[0][1])], 7)
        pygame.draw.circle(window, colour, [int(Rotate_clockwise([[self.pos[0] + 20, self.pos[1]]], self.pos, 7 * pi / 6)[0][0]), int(Rotate_clockwise([[self.pos[0] + 20, self.pos[1]]], self.pos, 7 * pi / 6)[0][1])], 7)
        pygame.draw.circle(window, (0, 0, 0), [int(Rotate_clockwise([[self.pos[0] + 20, self.pos[1]]], self.pos, pi / 2)[0][0]), int(Rotate_clockwise([[self.pos[0] + 20, self.pos[1]]], self.pos, pi / 2)[0][1])], 7, 3)
        pygame.draw.circle(window, (0, 0, 0), [int(Rotate_clockwise([[self.pos[0] + 20, self.pos[1]]], self.pos, 11 * pi / 6)[0][0]), int(Rotate_clockwise([[self.pos[0] + 20, self.pos[1]]], self.pos, 11 * pi / 6)[0][1])], 7, 3)
        pygame.draw.circle(window, (0, 0, 0), [int(Rotate_clockwise([[self.pos[0] + 20, self.pos[1]]], self.pos, 7 * pi / 6)[0][0]), int(Rotate_clockwise([[self.pos[0] + 20, self.pos[1]]], self.pos, 7 * pi / 6)[0][1])], 7, 3)
        pygame.draw.polygon(window, (128, 128, 128), Rotate_clockwise([[self.pos[0], self.pos[1] + 3], [self.pos[0], self.pos[1] - 3], [self.pos[0] + 20, self.pos[1] - 3], [self.pos[0] + 20, self.pos[1] + 3]], self.pos, pi / 2))
        pygame.draw.polygon(window, (128, 128, 128), Rotate_clockwise([[self.pos[0], self.pos[1] + 3], [self.pos[0], self.pos[1] - 3], [self.pos[0] + 20, self.pos[1] - 3], [self.pos[0] + 20, self.pos[1] + 3]], self.pos, 11 * pi / 6))
        pygame.draw.polygon(window, (128, 128, 128), Rotate_clockwise([[self.pos[0], self.pos[1] + 3], [self.pos[0], self.pos[1] - 3], [self.pos[0] + 20, self.pos[1] - 3], [self.pos[0] + 20, self.pos[1] + 3]], self.pos, 7 * pi / 6))
        pygame.draw.polygon(window, (0, 0, 0), Rotate_clockwise([[self.pos[0], self.pos[1] + 3], [self.pos[0], self.pos[1] - 3], [self.pos[0] + 20, self.pos[1] - 3], [self.pos[0] + 20, self.pos[1] + 3]], self.pos, pi / 2), 3)
        pygame.draw.polygon(window, (0, 0, 0), Rotate_clockwise([[self.pos[0], self.pos[1] + 3], [self.pos[0], self.pos[1] - 3], [self.pos[0] + 20, self.pos[1] - 3], [self.pos[0] + 20, self.pos[1] + 3]], self.pos, 11 * pi / 6), 3)
        pygame.draw.polygon(window, (0, 0, 0), Rotate_clockwise([[self.pos[0], self.pos[1] + 3], [self.pos[0], self.pos[1] - 3], [self.pos[0] + 20, self.pos[1] - 3], [self.pos[0] + 20, self.pos[1] + 3]], self.pos, 7 * pi / 6), 3)
        pygame.draw.polygon(window, (0, 0, 0), Rotate_clockwise([[self.pos[0], self.pos[1] + 2], [self.pos[0], self.pos[1] - 2], [self.pos[0] + 35, self.pos[1] - 2], [self.pos[0] + 35, self.pos[1] + 2]], self.pos, self.direction), 3)
        pygame.draw.circle(window, colour, [int(self.pos[0]), int(self.pos[1])], 15)
        pygame.draw.circle(window, (0, 0, 0), [int(self.pos[0]), int(self.pos[1])], 15, 3)

#------------------------------------Other------------------------------------
#Explosion
class Explosion:
    def __init__(self, pos, radius, damage):
        self.pos = pos
        self.radius = radius
        self.damage = damage
        self.timer = 0
        if sound_effects == True:
            explosion_sound.play()
    def display(self):
        pygame.draw.circle(window, (255, 0, 0), [int(self.pos[0]), int(self.pos[1])], self.radius)
        pygame.draw.circle(window, (255, 128, 0), [int(self.pos[0]), int(self.pos[1])], int(2 * self.radius / 3))
        pygame.draw.circle(window, (255, 255, 0), [int(self.pos[0]), int(self.pos[1])], int(self.radius / 3))

#Button
class Button:
    def __init__(self, rect, text = "", font = pygame.font.SysFont("Courier New", 50)):
        self.rect = rect
        self.text = text
        self.font = font
        self.pressed = False
    def display(self):
        if self.pressed == True:
            pygame.draw.rect(window, (0, 255, 0), self.rect)
            pygame.draw.rect(window, (255, 0, 0), self.rect, 5)
            Draw_text(window, (255, 0, 0), self.font, [int(self.rect[0] + self.rect[2] / 2), int(self.rect[1] + self.rect[3] / 2)], self.text)
        if self.pressed == False:
            pygame.draw.rect(window, (255, 0, 0), self.rect)
            pygame.draw.rect(window, (0, 255, 0), self.rect, 5)
            Draw_text(window, (0, 255, 0), self.font, [int(self.rect[0] + self.rect[2] / 2), int(self.rect[1] + self.rect[3] / 2)], self.text)

#----------------------------------------------------------------------Define variables---------------------------------------------------------------------
    #Fonts
small_font = pygame.font.SysFont("Courier New", 25)
regular_font = pygame.font.SysFont("Courier New", 50)
large_font = pygame.font.SysFont("Courier New", 150)

    #Cheats
infinite_money = god_mode = music_mix = False
vision = "normal"

    #Other
action = "Menu"
music = True
music_volume = 1
sound_effects = True

    #Sounds
mario_introduction_music = pygame.mixer.Sound("C:\\Users\\2738490516\\Documents\\Python\\Sounds\\Mario Theme Song Introduction.ogg")
mario_loop_music = pygame.mixer.Sound("C:\\Users\\2738490516\\Documents\\Python\\Sounds\\Mario Theme Song Loop.ogg")
star_wars_music = pygame.mixer.Sound("C:\\Users\\2738490516\\Documents\\Python\\Sounds\\Star Wars Imperial March.ogg")
tetris_music = pygame.mixer.Sound("C:\\Users\\2738490516\\Documents\\Python\\Sounds\\Tetris Theme Song.ogg")
william_tell_music = pygame.mixer.Sound("C:\\Users\\2738490516\\Documents\\Python\\Sounds\\William Tell Overture Finale.ogg")
all_music = [mario_loop_music, star_wars_music, tetris_music, william_tell_music]
music_channel = pygame.mixer.Channel(0)

mario_death_sound = pygame.mixer.Sound("C:\\Users\\2738490516\\Documents\\Python\\Sounds\\Mario Theme Song Death.ogg")
explosion_sound = pygame.mixer.Sound("C:\\Users\\2738490516\\Documents\\Python\\Sounds\\Explosion.ogg")
gunshot_sound = pygame.mixer.Sound("C:\\Users\\2738490516\\Documents\\Python\\Sounds\\Gunshot.ogg")
mine_beep = pygame.mixer.Sound("C:\\Users\\2738490516\\Documents\\Python\\Sounds\\Mine Beep.ogg")

    #Keys
up_key = K_w
down_key = K_s
left_key = K_a
right_key = K_d

hand_forward_key = K_UP
hand_backward_key = K_DOWN
hand_left_key = K_LEFT
hand_right_key = K_RIGHT

weapon_1_key = K_1
weapon_2_key = K_2
health_pack_key = K_e
mine_key = K_q

pause_game_key = K_p

all_keys = [up_key, down_key, left_key, right_key, hand_forward_key, hand_backward_key, hand_left_key, hand_right_key, weapon_1_key, weapon_2_key, health_pack_key, pause_game_key]

#----------------------------------------------------------------------Full game loop----------------------------------------------------------------------
while True:
#-------------------------------------------------------------------------Main menu-------------------------------------------------------------------------
    if action == "Menu":
#Player
        player_pos = [width / 2, height / 2]
        player_move_direction = 0
        player_speed = 0
        player_health = 100
        player_maxhealth = 100

    #Player hand - used to determine where player holds weapons
        hand_direction = pi / 2
        hand_distance = 40
        player_hand = [width / 2, height / 2 - hand_distance]
        up = down = left = right = False
        hand_forward = hand_backward = hand_left = hand_right = False

#Weapon 1: Lightsaber
#Weapon 2: Shield
        player_weapon = 1
        player_team = "blue"
        lightsaber_damage = 5
        shield_angle = 45
        health_packs = 0
        trip_mines = 10
        pd_turrets = 10

#Other
        wave = 1
        difficulty = 1
        money = 0
        score = 0
        total_time = 0

#Turns on music if enabled
        if music_mix == True:
            music = random.choice(all_music)
        else:
            music = mario_loop_music
        if music == mario_loop_music:
            music_channel.play(mario_introduction_music)
        else:
            music_channel.play(music)
        music_channel.set_volume(music_volume)
        buttons = [Button([width / 2 - 250, height / 3, 500, 75], "Play game", regular_font), Button([0, 0, 100, 50], "Quit", small_font), Button([width / 2 - 250, height / 3 + 100, 500, 75], "Cheats", regular_font), Button([width / 2 - 250, height / 3 + 200, 500, 75], "Settings", regular_font)]
        selected_button = None
        mouse_down = False
        while action == "Menu":
            window.fill((255, 255, 255))
            mouse_pos = pygame.mouse.get_pos()
            if music_channel.get_busy() == False:
                music_channel.play(music, -1)
                music_channel.set_volume(music_volume)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_down = True
                    if event.button == 1:
                        for button in buttons:
                            if button.rect[0] <= mouse_pos[0] <= button.rect[0] + button.rect[2] and button.rect[1] <= mouse_pos[1] <= button.rect[1] + button.rect[3]:
                                button.pressed = True
                                selected_button = button
                if event.type == pygame.MOUSEBUTTONUP:
                    mouse_down = False
                    if event.button == 1:
                        if buttons[0].rect[0] <= mouse_pos[0] <= buttons[0].rect[0] + buttons[0].rect[2] and buttons[0].rect[1] <= mouse_pos[1] <= buttons[0].rect[1] + buttons[0].rect[3]:
                            buttons[0].pressed = False
                            if selected_button != None:
                                if selected_button == buttons[0]:
                                    money = 100
                                    action = "Difficulty"
                        elif buttons[1].rect[0] <= mouse_pos[0] <= buttons[1].rect[0] + buttons[1].rect[2] and buttons[1].rect[1] <= mouse_pos[1] <= buttons[1].rect[1] + buttons[1].rect[3]:
                            buttons[1].pressed = False
                            if selected_button != None:
                                if selected_button == buttons[1]:
                                    pygame.quit()
                                    sys.exit()
                        elif buttons[2].rect[0] <= mouse_pos[0] <= buttons[2].rect[0] + buttons[2].rect[2] and buttons[2].rect[1] <= mouse_pos[1] <= buttons[2].rect[1] + buttons[2].rect[3]:
                            buttons[2].pressed = False
                            if selected_button != None:
                                if selected_button == buttons[2]:
                                    infinite_money, god_mode, music_mix, vision, wave = Cheats()
                        elif buttons[3].rect[0] <= mouse_pos[0] <= buttons[3].rect[0] + buttons[3].rect[2] and buttons[3].rect[1] <= mouse_pos[1] <= buttons[3].rect[1] + buttons[3].rect[3]:
                            buttons[3].pressed = False
                            if selected_button != None:
                                if selected_button == buttons[3]:
                                    all_keys, music_volume, sound_effects = Settings()
                                    [up_key, down_key, left_key, right_key, hand_forward_key, hand_backward_key, hand_left_key, hand_right_key, weapon_1_key, weapon_2_key, health_pack_key, pause_game_key] = all_keys
                                    music_channel.set_volume(music_volume)
                        else:
                            selected_button = None

            Draw_text(window, (0, 0, 0), large_font, [width / 2, height / 6], "Jedi Master")
            for button in buttons:
                if selected_button == button and mouse_down == True:
                    if button.rect[0] <= mouse_pos[0] <= button.rect[0] + button.rect[2] and button.rect[1] <= mouse_pos[1] <= button.rect[1] + button.rect[3]:
                        button.pressed = True
                    else:
                        button.pressed = False
                button.display()

            pygame.display.flip()
            clock.tick(FPS)

#-------------------------------------------------------------------Difficulty selection-------------------------------------------------------------------
#Each difficulty is assigned a value.  When a difficulty is selected, then enemy health, enemy damage, and game speed are multiplied by this value
    if action == "Difficulty":
        buttons = [Button([width / 2 - 250, height / 3, 500, 75], "Easiest", regular_font), Button([width / 2 - 250, height / 3 + 100, 500, 75], "Easy", regular_font), Button([width / 2 - 250, height / 3 + 200, 500, 75], "Normal", regular_font), Button([width / 2 - 250, height / 3 + 300, 500, 75], "Difficult", regular_font), Button([0, 0, 100, 50], "Menu", small_font)]
        selected_button = None
        mouse_down = False
        while action == "Difficulty":
            window.fill((255, 255, 255))
            mouse_pos = pygame.mouse.get_pos()
#Turns on music if enabled
            if music_channel.get_busy() == False:
                music_channel.play(music, -1)
                music_channel.set_volume(music_volume)
#Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_down = True
                    if event.button == 1:
                        for button in buttons:
                            if button.rect[0] <= mouse_pos[0] <= button.rect[0] + button.rect[2] and button.rect[1] <= mouse_pos[1] <= button.rect[1] + button.rect[3]:
                                button.pressed = True
                                selected_button = button
                if event.type == pygame.MOUSEBUTTONUP:
                    mouse_down = False
                    if event.button == 1:
                        if buttons[0].rect[0] <= mouse_pos[0] <= buttons[0].rect[0] + buttons[0].rect[2] and buttons[0].rect[1] <= mouse_pos[1] <= buttons[0].rect[1] + buttons[0].rect[3]:
                            buttons[0].pressed = False
                            if selected_button != None:
                                if selected_button == buttons[0]:
                                    difficulty = 0.5
                                    money = 100
                                    action = "Play game"
                        elif buttons[1].rect[0] <= mouse_pos[0] <= buttons[1].rect[0] + buttons[1].rect[2] and buttons[1].rect[1] <= mouse_pos[1] <= buttons[1].rect[1] + buttons[1].rect[3]:
                            buttons[1].pressed = False
                            if selected_button != None:
                                if selected_button == buttons[1]:
                                    difficulty = 0.75
                                    money = 100
                                    action = "Play game"
                        elif buttons[2].rect[0] <= mouse_pos[0] <= buttons[2].rect[0] + buttons[2].rect[2] and buttons[2].rect[1] <= mouse_pos[1] <= buttons[2].rect[1] + buttons[2].rect[3]:
                            buttons[2].pressed = False
                            if selected_button != None:
                                if selected_button == buttons[2]:
                                    difficulty = 1
                                    money = 100
                                    action = "Play game"
                        elif buttons[3].rect[0] <= mouse_pos[0] <= buttons[3].rect[0] + buttons[3].rect[2] and buttons[3].rect[1] <= mouse_pos[1] <= buttons[3].rect[1] + buttons[3].rect[3]:
                            buttons[3].pressed = False
                            if selected_button != None:
                                if selected_button == buttons[3]:
                                    difficulty = 2
                                    money = 100
                                    action = "Play game"
                        elif buttons[4].rect[0] <= mouse_pos[0] <= buttons[4].rect[0] + buttons[4].rect[2] and buttons[4].rect[1] <= mouse_pos[1] <= buttons[4].rect[1] + buttons[4].rect[3]:
                            buttons[4].pressed = False
                            if selected_button != None:
                                if selected_button == buttons[4]:
                                    action = "Menu"
                        else:
                            selected_button = None

            Draw_text(window, (0, 0, 0), large_font, [width / 2, height / 6], "Difficulty")
            for button in buttons:
                if selected_button == button and mouse_down == True:
                    if button.rect[0] <= mouse_pos[0] <= button.rect[0] + button.rect[2] and button.rect[1] <= mouse_pos[1] <= button.rect[1] + button.rect[3]:
                        button.pressed = True
                    else:
                        button.pressed = False
                button.display()

            pygame.display.flip()
            clock.tick(FPS)

#----------------------------------------------------------------------Main game loop----------------------------------------------------------------------
    if action == "Play game":
#Reset all wave settings
        timer = -600
        enemy_add_timer = 0
        bullets = []
        lasers = []
        pd_lasers = []
        deflects = []
        rockets = []
        explosions = []

    #enemies is the list of enemies on the screen, and remaining_enemies is the list of enemies that will be added later in the wave
        enemies = []
        remaining_enemies = []

        mines = []
        turrets = []

        potential_targets = ["player", enemies, turrets, [bullets, rockets]]
#Turns on music if enabled
        if music_mix == True:
            music = random.choice(all_music)
        else:
            music = star_wars_music
        if music == mario_loop_music:
            music_channel.play(mario_introduction_music)
        else:
            music_channel.play(music, -1)
        music_channel.set_volume(music_volume)

#Adds enemies to the list of remaining enemies
        for i in range(wave + 4):
            remaining_enemies.append(Rifleman([random.randint(25, width - 25), random.randint(25, height - 25)], 0, 100 * (wave // 10 * 0.1 + 1), 100 * (wave // 10 * 0.1 + 1), 0, "red"))
        for i in range(wave // 2):
            remaining_enemies.append(Machine_gunner([random.randint(25, width - 25), random.randint(25, height - 25)], 0, 100 * (wave // 10 * 0.1 + 1), 100 * (wave // 10 * 0.1 + 1), 0, "red"))
        for i in range(wave // 3):
            remaining_enemies.append(Laser_sniper([random.randint(25, width - 25), random.randint(25, height - 25)], 0, 100 * (wave // 10 * 0.1 + 1), 100 * (wave // 10 * 0.1 + 1), "red"))
        for i in range(wave // 4):
            remaining_enemies.append(Laser_gunner([random.randint(25, width - 25), random.randint(25, height - 25)], 0, 100 * (wave // 10 * 0.1 + 1), 100 * (wave // 10 * 0.1 + 1), "red"))
        for i in range(wave // 5):
            remaining_enemies.append(Rocket_launcher([random.randint(25, width - 25), random.randint(25, height - 25)], 0, 100 * (wave // 10 * 0.1 + 1), 100 * (wave // 10 * 0.1 + 1), "red"))

        while action == "Play game":
            window.fill((255, 255, 255))
            mouse_pos = pygame.mouse.get_pos()
            if music == mario_loop_music and music_channel.get_busy() == False:
                music_channel.play(mario_loop_music, -1)
                music_channel.set_volume(music_volume)
            timer += difficulty
            enemy_add_timer += difficulty

#-----------------------------------Events-----------------------------------
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == up_key:
                        up = True
                        down = False
                    if event.key == down_key:
                        down = True
                        up = False
                    if event.key == left_key:
                        left = True
                        right = False
                    if event.key == right_key:
                        right = True
                        left = False
                    if event.key == hand_forward_key:
                        hand_forward = True
                        hand_backward = False
                    if event.key == hand_backward_key:
                        hand_backward = True
                        hand_forward = False
                    if event.key == hand_left_key:
                        hand_left = True
                        hand_right = False
                    if event.key == hand_right_key:
                        hand_right = True
                        hand_left = False
                    if event.key == weapon_1_key:
                        player_weapon = 1
                    if event.key == weapon_2_key:
                        player_weapon = 2
                    if event.key == pause_game_key:
                        action = "Pause"
                    if event.key == mine_key and trip_mines > 0:
                        turrets.append(Point_defence([player_pos[0], player_pos[1]], 0, player_team))
                        trip_mines -= 1
                    if event.key == health_pack_key and health_packs > 0:
                        player_health += 50
                        if player_health > player_maxhealth:
                            player_health = player_maxhealth
                        health_packs -= 1
                if event.type == pygame.KEYUP:
                    if event.key == up_key:
                        up = False
                        if left == False and right == False and down == False:
                            player_speed = 0
                    if event.key == down_key:
                        down = False
                        if left == False and right == False and up == False:
                            player_speed = 0
                    if event.key == left_key:
                        left = False
                        if up == False and down == False and right == False:
                            player_speed = 0
                    if event.key == right_key:
                        right = False
                        if up == False and down == False and left == False:
                            player_speed = 0
                    if event.key == hand_forward_key:
                        hand_forward = False
                    if event.key == hand_backward_key:
                        hand_backward = False
                    if event.key == hand_left_key:
                        hand_left = False
                    if event.key == hand_right_key:
                        hand_right = False

#---------------------------------Game logic---------------------------------
#Check if game is paused
            if action == "Pause":
                music_channel.pause()
                while action == "Pause":
                    pause_result = Pause_game()
                    if pause_result == "Menu":
                        action = "Menu"
                    if pause_result == "Cheats":
                        infinite_money, god_mode, music_mix, vision, wave = Cheats()
                        action = "Pause"
                    if pause_result == "Settings":
                        all_keys, music_volume, sound_effects = Settings()
                        [up_key, down_key, left_key, right_key, hand_forward_key, hand_backward_key, hand_left_key, hand_right_key, weapon_1_key, weapon_2_key, health_pack_key, pause_game_key] = all_keys
                        music_channel.set_volume(music_volume)
                        action = "Pause"
                    if pause_result == None:
                        music_channel.unpause()
                        action = "Play game"

#Player movement
            if up == True:
                if left == True:
                    player_move_direction = -3 * pi / 4
                elif right == True:
                    player_move_direction = -pi / 4
                else:
                    player_move_direction = -pi / 2
            elif down == True:
                if left == True:
                    player_move_direction = 3 * pi / 4
                elif right == True:
                    player_move_direction = pi / 4
                else:
                    player_move_direction = pi / 2
            elif left == True:
                player_move_direction = pi
            elif right == True:
                player_move_direction = 0
            if up == True or down == True or left == True or right == True:
                if player_weapon == 2:
                    player_speed = 4
                else:
                    player_speed = 5
            player_pos[0] += cos(player_move_direction) * player_speed * difficulty
            player_pos[1] += sin(player_move_direction) * player_speed * difficulty

#Move the player's hand
            player_hand = [player_pos[0], player_pos[1] + hand_distance]
            player_hand = Rotate_clockwise([player_hand], player_pos, hand_direction + pi / 2)[0]
            if player_weapon == 1:
                if hand_left == True:
                    hand_direction -= pi / 36 * difficulty
                if hand_right == True:
                    hand_direction += pi / 36 * difficulty
                if hand_forward == True:
                    if hand_distance < 50:
                        hand_distance += 2 * difficulty
                        player_hand = Point_to(player_pos, player_hand, hand_distance)
                if hand_backward == True:
                    if hand_distance > 30:
                        hand_distance -= 2 * difficulty
                        player_hand = Point_to(player_pos, player_hand, hand_distance)
            elif player_weapon == 2:
                player_hand = Point_to(player_pos, mouse_pos, 40)
                hand_direction = atan2(mouse_pos[1] - player_pos[1], mouse_pos[0] - player_pos[0])
                hand_distance = 40

#Make sure that the player's body is on the screen
            if player_pos[0] - 25 < 0:
                player_pos[0] = 25
            if player_pos[0] + 25 > width:
                player_pos[0] = width - 25
            if player_pos[1] - 25 < 0:
                player_pos[1] = 25
            if player_pos[1] + 25 > height:
                player_pos[1] = height - 25

#Update lightsaber variables for collision detection
            if player_weapon == 1:
                lightsaber_end = Point_to(player_hand, mouse_pos, 100)
                lightsaber_direction = atan2(player_hand[1] - mouse_pos[1], player_hand[0] - mouse_pos[0])

#Spawn enemies
            if (enemy_add_timer >= 600 or (enemies == [] and timer >= 0)) and remaining_enemies != []:
                adding_enemies = []
                spawn_line_direction = atan2(-player_pos[0] + width / 2, player_pos[1] - height / 2)
                if wave <= 0:
                    wave_offset = wave
                    wave = 0
                for i in range((wave + 10) // 10):
                    if len(remaining_enemies) < (wave + 10) // 10:
                        adding_enemies.extend(remaining_enemies)
                        remaining_enemies = []
                        break
                    enemy = random.choice(remaining_enemies)
                    adding_enemies.append(enemy)
                    remaining_enemies.remove(enemy)
                for enemy in adding_enemies:
                    while (enemy.pos[1] - height / 2 > tan(spawn_line_direction) * (enemy.pos[0] - width / 2) and player_pos[1] - height / 2 > tan(spawn_line_direction) * (player_pos[0] - width / 2)) or (enemy.pos[1] - height / 2 < tan(spawn_line_direction) * (enemy.pos[0] - width / 2) and player_pos[1] - height / 2 < tan(spawn_line_direction) * (player_pos[0] - width / 2)):
                        enemy.pos = [random.randint(25, width - 25), random.randint(25, height - 25)]
                    enemies.append(enemy)
                enemy_add_timer = 0
                if wave == 0:
                    wave += wave_offset

#Enemy movement, collision detection, and property updates - lasers are not included because some dissapear on the same frame that they are created on
            for enemy in enemies[:]:
                if Do_line_and_circle_intersect([enemy.pos, 25], player_hand, lightsaber_end, False) != False and player_weapon == 1:
                    if god_mode == True and enemy in enemies:
                        if type(enemy) == Rifleman:
                            money += 10
                            score += 100 * ((wave + 10) // 10)
                        if type(enemy) == Machine_gunner:
                            money += 17
                            score += 170 * ((wave + 10) // 10)
                        if type(enemy) == Laser_sniper:
                            money += 26
                            score += 260 * ((wave + 10) // 10)
                        if type(enemy) == Laser_gunner:
                            money += 41
                            score += 410 * ((wave + 10) // 10)
                        if type(enemy) == Rocket_launcher:
                            money += 59
                            score += 590 * ((wave + 10) // 10)
                        enemies.remove(enemy)
                    else:
                        enemy.health -= lightsaber_damage
                if enemy.health <= 0 and enemy in enemies:
                    if type(enemy) == Rifleman:
                        money += 10
                        score += 100 * ((wave + 10) // 10)
                    if type(enemy) == Machine_gunner:
                        money += 17
                        score += 170 * ((wave + 10) // 10)
                    if type(enemy) == Laser_sniper:
                        money += 26
                        score += 260 * ((wave + 10) // 10)
                    if type(enemy) == Laser_gunner:
                        money += 41
                        score += 410 * ((wave + 10) // 10)
                    if type(enemy) == Rocket_launcher:
                        money += 59
                        score += 590 * ((wave + 10) // 10)
                    enemies.remove(enemy)
                if enemy.team == "red":
                    enemy.move_shoot([player_pos[0], player_pos[1]])

#Bullet movement, deflection, collision detection and property updates
            for bullet in bullets[:]:
                bullet.move()
                if (not 5 < bullet.pos[0] < width - 5 or not 5 < bullet.pos[1] < height - 5) and bullet in bullets:
                    bullets.remove(bullet)
                    continue
                for enemy in enemies:
                    if Do_circles_intersect([bullet.pos, 5], [enemy.pos, 25]) and bullet.team != enemy.team and bullet in bullets:
                        enemy.health -= bullet.damage
                        bullets.remove(bullet)
                        break
                if not bullet in bullets:
                    continue
                if bullet.health <= 0 and bullet in bullets:
                    bullets.remove(bullet)
                    continue
                    

                direction_from_last_pos = atan2(bullet.last_pos[1] - bullet.pos[1], bullet.last_pos[0] - bullet.pos[0])
                bullet_edge_points = Do_line_and_circle_intersect([bullet.pos, 5], bullet.pos, [bullet.pos[0] + cos(direction_from_last_pos + pi / 2), bullet.pos[1] + sin(direction_from_last_pos + pi / 2)], True)
                last_bullet_edge_points = Do_line_and_circle_intersect([bullet.last_pos, 5], bullet.last_pos, [bullet.last_pos[0] + cos(direction_from_last_pos + pi / 2), bullet.last_pos[1] + sin(direction_from_last_pos + pi / 2)], True)
                if bullet.team != player_team:
                    deflection_point = None
                    player_contact_point = None
                    if player_weapon == 1:
                        if Do_line_and_circle_intersect([bullet.pos, 5], player_hand, lightsaber_end, False):
                            bullet.pos = Do_lines_intersect(direction_from_last_pos, bullet.last_pos, lightsaber_direction, player_hand)
                            bullet.direction = Deflect(bullet.direction, lightsaber_direction + pi / 2)
                            bullet.team = player_team
                        elif Do_lines_intersect(direction_from_last_pos, bullet_edge_points[0], lightsaber_direction, player_hand, [player_hand, lightsaber_end]) != False:
                            if Do_lines_intersect(direction_from_last_pos, bullet_edge_points[0], lightsaber_direction, player_hand, [bullet_edge_points[0], last_bullet_edge_points[0]]) != False:
                                bullet.pos = Do_lines_intersect(direction_from_last_pos, bullet.last_pos, lightsaber_direction, player_hand)
                                bullet.direction = Deflect(bullet.direction, lightsaber_direction + pi / 2)
                                bullet.team = player_team
                        elif Do_lines_intersect(direction_from_last_pos, bullet_edge_points[1], lightsaber_direction, player_hand, [player_hand, lightsaber_end]) != False:
                            if Do_lines_intersect(direction_from_last_pos, bullet_edge_points[1], lightsaber_direction, player_hand, [bullet_edge_points[1], last_bullet_edge_points[1]]) != False:
                                bullet.pos = Do_lines_intersect(direction_from_last_pos, bullet.last_pos, lightsaber_direction, player_hand)
                                bullet.direction = Deflect(bullet.direction, lightsaber_direction + pi / 2)
                                bullet.team = player_team

                    if player_weapon == 2:
                        shield_bullet_direction = atan2(bullet.pos[1] - player_pos[1], bullet.pos[0] - player_pos[0])
                        if Do_line_and_circle_intersect([player_pos, 50], last_bullet_edge_points[0], bullet_edge_points[0], False) != False and bullet.team != player_team:
                            intersections = Do_line_and_circle_intersect([player_pos, 50], last_bullet_edge_points[0], bullet_edge_points[0], False)
                            bullet_shield_intersections = Do_line_and_circle_intersect([player_pos, 50], last_bullet_edge_points[0], bullet_edge_points[0], False)
                            shield_bullet_direction -= hand_direction
                            shield_bullet_direction = (shield_bullet_direction + pi) % (2 * pi) - pi
                            if -shield_angle * pi / 180 <= shield_bullet_direction <= shield_angle * pi / 180:
                                if len(bullet_shield_intersections) == 2:
                                    if hypot(bullet.last_pos[0] - bullet_shield_intersections[0][0], bullet.last_pos[0] - bullet_shield_intersections[0][1]) <= hypot(bullet.last_pos[0] - bullet_shield_intersections[1][0], bullet.last_pos[0] - bullet_shield_intersections[1][1]):
                                        closer_intersection = bullet_shield_intersections[0]
                                    else:
                                        closer_intersection = bullet_shield_intersections[1]
                                elif len(bullet_shield_intersections) == 1:
                                    closer_intersection = bullet_shield_intersections[0]
                                bullet.pos = closer_intersection
                                shield_direction = atan2(-player_pos[0] + bullet.pos[0], player_pos[1] - bullet.pos[1])
                                bullet.direction = Deflect(bullet.direction, shield_direction) + pi
                                bullet.team = player_team

                    if Do_line_and_circle_intersect([player_pos, 25], bullet_edge_points[0], last_bullet_edge_points[0], False) != False and bullet.team != player_team and bullet in bullets:
                        player_health -= bullet.damage
                        bullets.remove(bullet)
                        continue
                    if Do_line_and_circle_intersect([player_pos, 25], bullet_edge_points[1], last_bullet_edge_points[1], False) != False and bullet.team != player_team and bullet in bullets:
                        player_health -= bullet.damage
                        bullets.remove(bullet)
                        continue

#Laser deflection, collision detection and property updates - includes laser and enemy collision detection
            for laser in lasers[:]:
                laser_direction = atan2(laser.end_pos[1] - laser.start_pos[1], laser.end_pos[0] - laser.start_pos[0])
                deflection_intersection = None
                player_intersection = None
                if player_weapon == 1:
                    if Do_lines_intersect(laser_direction, laser.start_pos, lightsaber_direction, player_hand) == True:
                        if hypot(laser.start_pos[0] - player_hand[0], laser.start_pos[1] - player_hand[1]) < hypot(laser.start_pos[0] - lightsaber_end[0], laser.start_pos[1] - lightsaber_end[1]):
                            deflection_intersection = player_hand
                        else:
                            deflection_intersection = lightsaber_end
                    else:
                        if Do_lines_intersect(laser_direction, laser.start_pos, lightsaber_direction, player_hand, [player_hand, lightsaber_end]) != False and laser.team != player_team:
                            if Do_lines_intersect(laser_direction, laser.start_pos, lightsaber_direction, player_hand, [laser.start_pos, laser.end_pos]) != False:
                                deflection_intersection = Do_lines_intersect(laser_direction, laser.start_pos, lightsaber_direction, player_hand)

                if player_weapon == 2:
                    laser_shield_intersections = Do_line_and_circle_intersect([player_pos, 50], laser.start_pos, laser.end_pos, False)
                    if laser_shield_intersections != False:
                        for point in laser_shield_intersections[:]:
                            point_angle = atan2(point[1] - player_pos[1], point[0] - player_pos[0])
                            point_angle -= hand_direction
                            point_angle = (point_angle + pi) % (2 * pi) - pi
                            if not -shield_angle * pi / 180 <= point_angle <= shield_angle * pi / 180:
                                laser_shield_intersections.remove(point)
                        if len(laser_shield_intersections) == 2:
                            if hypot(laser_shield_intersections[0][0] - laser.start_pos[0], laser_shield_intersections[0][1] - laser.start_pos[1]) <= hypot(laser_shield_intersections[1][0] - laser.start_pos[0], laser_shield_intersections[1][1] - laser.start_pos[1]):
                                closer_intersection = laser_shield_intersections[0]
                            else:
                                closer_intersection = laser_shield_intersections[1]
                            deflection_intersection = closer_intersection
                        elif len(laser_shield_intersections) == 1:
                            closer_intersection = laser_shield_intersections[0]
                            deflection_intersection = closer_intersection

                laser_player_intersections = Do_line_and_circle_intersect([player_pos, 25], laser.start_pos, laser.end_pos, False)
                if laser_player_intersections != False:
                    if len(laser_player_intersections) == 2:
                        if hypot(laser.start_pos[0] - laser_player_intersections[0][0], laser.start_pos[1] - laser_player_intersections[0][1]) <= hypot(laser.start_pos[0] - laser_player_intersections[1][0], laser.start_pos[1] - laser_player_intersections[1][1]):
                            player_intersection = laser_player_intersections[0]
                        else:
                            player_intersection = laser_player_intersections[1]
                    else:
                        player_intersection = laser_player_intersections[0]

                if deflection_intersection != None and player_intersection != None:
                    if hypot(laser.start_pos[0] - deflection_intersection[0], laser.start_pos[1] - deflection_intersection[1]) <= hypot(laser.start_pos[0] - player_intersection[0], laser.start_pos[1] - player_intersection[1]):
                        if player_weapon == 1:
                            laser.end_pos = deflection_intersection
                            deflects.append(Laser(laser.end_pos, [laser.end_pos[0] + cos(Deflect(laser_direction, lightsaber_direction) + pi) * 10000, laser.end_pos[1] + sin(Deflect(laser_direction, lightsaber_direction) + pi) * 10000], 1, laser.damage, laser.penetrate, player_team))
                        elif player_weapon == 2:
                            shield_direction = atan2(-player_pos[0] + closer_intersection[0], player_pos[1] - closer_intersection[1])
                            laser.end_pos = deflection_intersection
                            deflects.append(Laser(laser.end_pos, [laser.end_pos[0] + cos(Deflect(laser_direction, shield_direction) + pi) * 10000, laser.end_pos[1] + sin(Deflect(laser_direction, shield_direction) + pi) * 10000], 1, laser.damage, laser.penetrate, player_team))
                    else:
                        player_health -= laser.damage
                        if laser.penetrate == False:
                            laser.end_pos = player_intersection
                elif deflection_intersection != None:
                    if player_weapon == 1:
                        laser.end_pos = deflection_intersection
                        deflects.append(Laser(laser.end_pos, [laser.end_pos[0] + cos(Deflect(laser_direction, lightsaber_direction) + pi) * 10000, laser.end_pos[1] + sin(Deflect(laser_direction, lightsaber_direction) + pi) * 10000], 1, laser.damage, laser.penetrate, player_team))
                    elif player_weapon == 2:
                        shield_direction = atan2(-player_pos[0] + closer_intersection[0], player_pos[1] - closer_intersection[1])
                        laser.end_pos = deflection_intersection
                        deflects.append(Laser(laser.end_pos, [laser.end_pos[0] + cos(Deflect(laser_direction, shield_direction) + pi) * 10000, laser.end_pos[1] + sin(Deflect(laser_direction, shield_direction) + pi) * 10000], 1, laser.damage, laser.penetrate, player_team))
                elif player_intersection != None:
                    player_health -= laser.damage
                    if laser.penetrate == False:
                        laser.end_pos = player_intersection

#Laser and enemy collision detection
            for laser in deflects:
                for enemy in enemies:
                    enemy_laser_intersections = Do_line_and_circle_intersect([enemy.pos, 25], laser.start_pos, laser.end_pos, False)
                    if enemy_laser_intersections != False:
                        if laser.penetrate == False:
                            if len(enemy_laser_intersections) == 2:
                                if hypot(enemy_laser_intersections[0][0] - laser.start_pos[0], enemy_laser_intersections[0][1] - laser.start_pos[1]) <= hypot(enemy_laser_intersections[1][0] - laser.start_pos[0], enemy_laser_intersections[1][1] - laser.start_pos[1]):
                                    closer_intersection = enemy_laser_intersections[0]
                                else:
                                    closer_intersection = enemy_laser_intersections[1]
                            elif len(enemy_laser_intersections) == 1:
                                closer_intersection = enemy_laser_intersections[0]
                            laser.end_pos = closer_intersection
                        enemy.health -= laser.damage

#Rocket movement, collision detection and property updates
            for rocket in rockets[:]:
                rocket.move()
                if rocket.health <= 0:
                    rocket.explode = True

                for point_number, point in enumerate(rocket.perimeter):
                    rocket_touching_player = False
                    if point[0] <= 100 or point[0] >= width or point[1] <= 100 or point[1] >= height:
                        if rocket in rockets:
                            rockets.remove(rocket)
                            break
                    if point_number == 4:
                        line = [point, rocket.perimeter[0]]
                    else:
                        line = [point, rocket.perimeter[point_number + 1]]
                    if Do_line_and_circle_intersect([player_pos, 25], line[0], line[1], False):
                        rocket.explode = True
                        rocket_touching_player = True
                    if hypot(player_pos[0] - line[0][0], player_pos[1] - line[0][1]) <= 25:
                        rocket.explode = True
                        rocket_touching_player = True
                    if player_weapon == 1:
                        if Do_lines_intersect(atan2(line[0][1] - line[1][1], line[0][0] - line[1][0]), line[0], lightsaber_direction, player_hand, [player_hand, lightsaber_end]):
                            if Do_lines_intersect(atan2(line[0][1] - line[1][1], line[0][0] - line[1][0]), line[0], lightsaber_direction, player_hand, [line[0], line[1]]):
                                rocket.explode = True
                    if player_weapon == 2:
                        rocket_shield_intersection = Do_line_and_circle_intersect([player_pos, 50], line[0], line[1], False)
                        if rocket_shield_intersection != False:
                            point_angle = atan2(point[1] - player_pos[1], point[0] - player_pos[0])
                            point_angle -= hand_direction
                            point_angle = (point_angle + pi) % (2 * pi) - pi
                            if -shield_angle * pi / 180 <= point_angle <= shield_angle * pi / 180:
                                rocket.explode = True
                    for laser in lasers:
                        if Do_lines_intersect(atan2(line[0][1] - line[1][1], line[0][0] - line[1][0]), line[0], atan2(laser.start_pos[1] - laser.end_pos[1], laser.start_pos[0] - laser.end_pos[0]), laser.start_pos, [laser.start_pos, laser.end_pos]) and laser.team != rocket.team:
                            if Do_lines_intersect(atan2(line[0][1] - line[1][1], line[0][0] - line[1][0]), line[0], atan2(laser.start_pos[1] - laser.end_pos[1], laser.start_pos[0] - laser.end_pos[0]), laser.start_pos, [line[0], line[1]]):
                                rocket.explode = True
                    for laser in deflects:
                        if Do_lines_intersect(atan2(line[0][1] - line[1][1], line[0][0] - line[1][0]), line[0], atan2(laser.start_pos[1] - laser.end_pos[1], laser.start_pos[0] - laser.end_pos[0]), laser.start_pos, [laser.start_pos, laser.end_pos]) and laser.team != rocket.team:
                            if Do_lines_intersect(atan2(line[0][1] - line[1][1], line[0][0] - line[1][0]), line[0], atan2(laser.start_pos[1] - laser.end_pos[1], laser.start_pos[0] - laser.end_pos[0]), laser.start_pos, [line[0], line[1]]):
                                rocket.explode = True
                    for laser in pd_lasers:
                        if Do_lines_intersect(atan2(line[0][1] - line[1][1], line[0][0] - line[1][0]), line[0], atan2(laser.start_pos[1] - laser.end_pos[1], laser.start_pos[0] - laser.end_pos[0]), laser.start_pos, [laser.start_pos, laser.end_pos]) and laser.team != rocket.team:
                            if Do_lines_intersect(atan2(line[0][1] - line[1][1], line[0][0] - line[1][0]), line[0], atan2(laser.start_pos[1] - laser.end_pos[1], laser.start_pos[0] - laser.end_pos[0]), laser.start_pos, [line[0], line[1]]):
                                rocket.explode = True
                    for bullet in bullets[:]:
                        if Do_line_and_circle_intersect([bullet.pos, 5], line[0], line[1], False) and bullet.team != rocket.team:
                            bullets.remove(bullet)
                            rocket.explode = True
                if rocket.explode == True:
                    if rocket in rockets:
                        rockets.remove(rocket)
                    if rocket_touching_player == True:
                        player_health -= rocket.damage
                    explosions.append(Explosion(rocket.pos, 150, 25))

#Mine triggers
            for mine in mines[:]:
                mine.trigger()
                if hypot(mine.pos[0] - player_pos[0], mine.pos[1] - player_pos[1]) <= 100 and mine.timer >= 0 and mine.team != player_team:
                    mine.explode = True
                for enemy in enemies:
                    if hypot(mine.pos[0] - enemy.pos[0], mine.pos[1] - enemy.pos[1]) <= 100 and mine.timer >= 0 and mine.team != enemy.team:
                        mine.explode = True
                if mine.timer >= 30:
                    explosions.append(Explosion(mine.pos, 150, 25))
                    mines.remove(mine)

#Point defence turrets
            for turret in turrets:
                if type(turret) == Point_defence:
                    if turret.target == None or (not turret.target in potential_targets[1] and not turret.target in potential_targets[2] and not turret.target in potential_targets[3][0] and not turret.target in potential_targets[3][1]) or hypot(turret.target.pos[0] - turret.pos[0], turret.target.pos[1] - turret.pos[1]) > 250 or turret.target.team == turret.team:
                        closest_target = None
                        turret.target = None
                        if player_team != turret.team:
                            closest_target = "player"
                        for enemy_number, enemy in enumerate(enemies):
                            if enemy.team != turret.team:
                                if enemy_number == 0:
                                    closest_target = enemy
                                else:
                                    if hypot(closest_target.pos[0] - turret.pos[0], closest_target.pos[1] - turret.pos[1]) >= hypot(enemy.pos[0] - turret.pos[0], enemy.pos[1] - turret.pos[1]):
                                        closest_target = enemy
                        for bullet_number, bullet in enumerate(bullets):
                            if bullet.team != turret.team:
                                if bullet_number == 0:
                                    closest_target = bullet
                                else:
                                    if hypot(closest_target.pos[0] - turret.pos[0], closest_target.pos[1] - turret.pos[1]) >= hypot(bullet.pos[0] - turret.pos[0], bullet.pos[1] - turret.pos[1]):
                                        closest_target = bullet
                        for rocket_number, rocket in enumerate(rockets):
                            if rocket.team != turret.team:
                                if rocket_number == 0:
                                    closest_target = rocket
                                else:
                                    if hypot(closest_target.pos[0] - turret.pos[0], closest_target.pos[1] - turret.pos[1]) >= hypot(rocket.pos[0] - turret.pos[0], rocket.pos[1] - turret.pos[1]):
                                        closest_target = rocket
                        if closest_target != None:
                            if closest_target == "player":
                                if hypot(player_pos[0] - turret.pos[0], player_pos[1] - turret.pos[1]) <= 250:
                                    turret.target = closest_target
                            else:
                                if hypot(closest_target.pos[0] - turret.pos[0], closest_target.pos[1] - turret.pos[1]) <= 250:
                                    turret.target = closest_target
                turret.shoot()

#Point defence lasers
            for laser in pd_lasers:
                laser_direction = atan2(laser.end_pos[1] - laser.start_pos[1], laser.end_pos[0] - laser.start_pos[0])
                if laser.team != player_team:
                    deflection_intersection = None
                    player_intersection = None
                    if player_weapon == 1:
                        if Do_lines_intersect(laser_direction, laser.start_pos, lightsaber_direction, player_hand) == True:
                            if hypot(laser.start_pos[0] - player_hand[0], laser.start_pos[1] - player_hand[1]) < hypot(laser.start_pos[0] - lightsaber_end[0], laser.start_pos[1] - lightsaber_end[1]):
                                deflection_intersection = player_hand
                            else:
                                deflection_intersection = lightsaber_end
                        else:
                            if Do_lines_intersect(laser_direction, laser.start_pos, lightsaber_direction, player_hand, [player_hand, lightsaber_end]) != False and laser.team != player_team:
                                if Do_lines_intersect(laser_direction, laser.start_pos, lightsaber_direction, player_hand, [laser.start_pos, laser.end_pos]) != False:
                                    deflection_intersection = Do_lines_intersect(laser_direction, laser.start_pos, lightsaber_direction, player_hand)

                    if player_weapon == 2:
                        laser_shield_intersections = Do_line_and_circle_intersect([player_pos, 50], laser.start_pos, laser.end_pos, False)
                        if laser_shield_intersections != False:
                            for point in laser_shield_intersections[:]:
                                point_angle = atan2(point[1] - player_pos[1], point[0] - player_pos[0])
                                point_angle -= hand_direction
                                point_angle = (point_angle + pi) % (2 * pi) - pi
                                if not -shield_angle * pi / 180 <= point_angle <= shield_angle * pi / 180:
                                    laser_shield_intersections.remove(point)
                            if len(laser_shield_intersections) == 2:
                                if hypot(laser_shield_intersections[0][0] - laser.start_pos[0], laser_shield_intersections[0][1] - laser.start_pos[1]) <= hypot(laser_shield_intersections[1][0] - laser.start_pos[0], laser_shield_intersections[1][1] - laser.start_pos[1]):
                                    closer_intersection = laser_shield_intersections[0]
                                else:
                                    closer_intersection = laser_shield_intersections[1]
                                deflection_intersection = closer_intersection
                            elif len(laser_shield_intersections) == 1:
                                closer_intersection = laser_shield_intersections[0]
                                deflection_intersection = closer_intersection

                    laser_player_intersections = Do_line_and_circle_intersect([player_pos, 25], laser.start_pos, laser.end_pos, False)
                    if laser_player_intersections != False:
                        if len(laser_player_intersections) == 2:
                            if hypot(laser.start_pos[0] - laser_player_intersections[0][0], laser.start_pos[1] - laser_player_intersections[0][1]) <= hypot(laser.start_pos[0] - laser_player_intersections[1][0], laser.start_pos[1] - laser_player_intersections[1][1]):
                                player_intersection = laser_player_intersections[0]
                            else:
                                player_intersection = laser_player_intersections[1]
                        else:
                            player_intersection = laser_player_intersections[0]

                    if deflection_intersection != None and player_intersection != None:
                        if hypot(laser.start_pos[0] - deflection_intersection[0], laser.start_pos[1] - deflection_intersection[1]) <= hypot(laser.start_pos[0] - player_intersection[0], laser.start_pos[1] - player_intersection[1]):
                            if player_weapon == 1:
                                laser.end_pos = deflection_intersection
                                deflects.append(PD_laser(laser.end_pos, [laser.end_pos[0] + cos(Deflect(laser_direction, lightsaber_direction) + pi) * 10000, laser.end_pos[1] + sin(Deflect(laser_direction, lightsaber_direction) + pi) * 10000], laser.damage, player_team))
                            elif player_weapon == 2:
                                shield_direction = atan2(-player_pos[0] + closer_intersection[0], player_pos[1] - closer_intersection[1])
                                laser.end_pos = deflection_intersection
                                deflects.append(PD_laser(laser.end_pos, [laser.end_pos[0] + cos(Deflect(laser_direction, shield_direction) + pi) * 10000, laser.end_pos[1] + sin(Deflect(laser_direction, shield_direction) + pi) * 10000], laser.damage, player_team))
                        else:
                            player_health -= laser.damage
                            laser.end_pos = player_intersection
                    elif deflection_intersection != None:
                        if player_weapon == 1:
                            laser.end_pos = deflection_intersection
                            deflects.append(PD_laser(laser.end_pos, [laser.end_pos[0] + cos(Deflect(laser_direction, lightsaber_direction) + pi) * 10000, laser.end_pos[1] + sin(Deflect(laser_direction, lightsaber_direction) + pi) * 10000], laser.damage, player_team))
                        elif player_weapon == 2:
                            shield_direction = atan2(-player_pos[0] + closer_intersection[0], player_pos[1] - closer_intersection[1])
                            laser.end_pos = deflection_intersection
                            deflects.append(PD_laser(laser.end_pos, [laser.end_pos[0] + cos(Deflect(laser_direction, shield_direction) + pi) * 10000, laser.end_pos[1] + sin(Deflect(laser_direction, shield_direction) + pi) * 10000],laser.damage, player_team))
                    elif player_intersection != None:
                        player_health -= laser.damage
                        laser.end_pos = player_intersection
                
                for enemy in enemies:
                    if enemy.team != laser.team:
                        enemy_laser_intersections = Do_line_and_circle_intersect([enemy.pos, 25], laser.start_pos, laser.end_pos, False)
                        if enemy_laser_intersections != False:
                            if len(enemy_laser_intersections) == 2:
                                if hypot(enemy_laser_intersections[0][0] - laser.start_pos[0], enemy_laser_intersections[0][1] - laser.start_pos[1]) <= hypot(enemy_laser_intersections[1][0] - laser.start_pos[0], enemy_laser_intersections[1][1] - laser.start_pos[1]):
                                    closer_intersection = enemy_laser_intersections[0]
                                else:
                                    closer_intersection = enemy_laser_intersections[1]
                            elif len(enemy_laser_intersections) == 1:
                                closer_intersection = enemy_laser_intersections[0]
                            laser.end_pos = closer_intersection
                            enemy.health -= laser.damage

                for bullet in bullets:
                    if bullet.team != laser.team:
                        bullet_laser_intersections = Do_line_and_circle_intersect([bullet.pos, 25], laser.start_pos, laser.end_pos, False)
                        if bullet_laser_intersections != False:
                            if len(bullet_laser_intersections) == 2:
                                if hypot(bullet_laser_intersections[0][0] - laser.start_pos[0], bullet_laser_intersections[0][1] - laser.start_pos[1]) <= hypot(bullet_laser_intersections[1][0] - laser.start_pos[0], bullet_laser_intersections[1][1] - laser.start_pos[1]):
                                    closer_intersection = bullet_laser_intersections[0]
                                else:
                                    closer_intersection = bullet_laser_intersections[1]
                            elif len(bullet_laser_intersections) == 1:
                                closer_intersection = bullet_laser_intersections[0]
                            laser.end_pos = closer_intersection
                            bullet.health -= laser.damage

                for rocket in rockets:
                    damage_rocket = False
                    if rocket.team != laser.team:
                        for point_number, point in enumerate(rocket.perimeter):
                            if point_number == 4:
                                line = [point, rocket.perimeter[0]]
                            else:
                                line = [point, rocket.perimeter[point_number]]

                            if Do_lines_intersect(atan2(line[0][1] - line[1][1], line[0][0] - line[1][0]), point, laser_direction, laser.start_pos, [line[0], line[1]]) != False:
                                if Do_lines_intersect(atan2(line[0][1] - line[1][1], line[0][0] - line[1][0]), point, laser_direction, laser.start_pos, [laser.start_pos, laser.end_pos]) != False:
                                    damage_rocket = True
                    if damage_rocket == True:
                        rocket.health -= laser.damage

#Explosion collision detection and property updates
            for explosion in explosions[:]:
                explosion.timer += 1
                if explosion.timer == 1:
                    if Do_circles_intersect([explosion.pos, explosion.radius], [player_pos, 25]):
                        player_health -= explosion.damage
                        if Do_circles_intersect([explosion.pos, 2 * explosion.radius / 3], [player_pos, 25]):
                            player_health -= explosion.damage
                            if Do_circles_intersect([explosion.pos, explosion.radius / 3], [player_pos, 25]):
                                player_health -= explosion.damage
                for enemy in enemies:
                    if explosion.timer == 1:
                        if Do_circles_intersect([explosion.pos, explosion.radius], [enemy.pos, 25]):
                            enemy.health -= explosion.damage
                            if Do_circles_intersect([explosion.pos, 2 * explosion.radius / 3], [enemy.pos, 25]):
                                enemy.health -= explosion.damage
                                if Do_circles_intersect([explosion.pos, explosion.radius / 3], [enemy.pos, 25]):
                                    enemy.health -= explosion.damage
                if explosion.timer >= 11:
                    explosions.remove(explosion)

#-------------------------------Draw everything-------------------------------
#Draw rockets
            for bullet in bullets:
                bullet.display()

#Draw lasers, excluding deflected ones
            for laser in lasers:
                laser.display()
                laser.timer += 1
                if laser.timer == laser.max_time:
                    lasers.remove(laser)

            for laser in pd_lasers:
                laser.display()
                pd_lasers.remove(laser)

#Draw rockets
            for rocket in rockets:
                rocket.display()

#Draw explosions
            for explosion in explosions:
                explosion.display()

#Draw enemies
            for enemy in enemies:
                enemy.display()

#Draw deflected lasers
            for laser in deflects[:]:
                laser.display()
                deflects.remove(laser)

            for mine in mines:
                mine.display()

            for turret in turrets:
                turret.display()

#Draw player, health, hand, and weapon
            if god_mode == True:
                player_health = player_maxhealth
            if player_weapon == 1:
                pygame.draw.line(window, (0, 0, 255), player_hand, lightsaber_end, 3)
            if player_weapon == 2:
                pygame.draw.arc(window, (0, 0, 255), [player_pos[0] - 50, player_pos[1] - 50, 2 * 50, 2 * 50], -hand_direction - shield_angle * pi / 180, -hand_direction + shield_angle * pi / 180, 3)
            pygame.draw.circle(window, (0, 0, 0), (int(player_pos[0]), int(player_pos[1])), 25)
            pygame.draw.circle(window, (0, 0, 0), (int(player_hand[0]), int(player_hand[1])), 10, 5)
            pygame.draw.rect(window, (255, 0, 0), [player_pos[0] - 25, player_pos[1] - 35, 50, 5])
            pygame.draw.rect(window, (0, 255, 0), [player_pos[0] - 25, player_pos[1] - 35, player_health * 50 / player_maxhealth, 5])
            pygame.draw.rect(window, (0, 0, 0), [player_pos[0] - 25, player_pos[1] - 35, 50, 5], 1)

#Draw vision obstructors if there are cheats enabling them
            if vision == "hyperopia":
                pygame.draw.circle(window, (0, 0, 0), [int(player_pos[0]), int(player_pos[1])], 250)
            elif vision == "myopia":
                pygame.draw.circle(window, (0, 0, 0), [int(player_pos[0]), int(player_pos[1])], 500, 250)
                pygame.draw.rect(window, (0, 0, 0), [int(player_pos[0] - 2250), int(player_pos[1] - 2250), 2000, 4500])
                pygame.draw.rect(window, (0, 0, 0), [int(player_pos[0] - 2250), int(player_pos[1] - 2250), 4500, 2000])
                pygame.draw.rect(window, (0, 0, 0), [int(player_pos[0] + 250), int(player_pos[1] - 2250), 2000, 4500])
                pygame.draw.rect(window, (0, 0, 0), [int(player_pos[0] - 2250), int(player_pos[1] + 250), 4500, 2000])

#Draw text onto screen
            if timer <= 0:
                Draw_text(window, (0, 0, 0), small_font, [width / 2, 25], "Wave begins in: " + str(round(-timer / 60, 2)) + "s")
            else:
                Draw_text(window, (0, 0, 0), small_font, [width / 2, 25], str(round(timer / 60, 2)) + "s")
                Draw_text(window, (0, 0, 0), small_font, [75, 25], "Wave: " + str(wave))
                Draw_text(window, (0, 0, 0), small_font, [175, 50], "Remaining enemies: " + str(len(remaining_enemies) + len(enemies)))

            Draw_text(window, (0, 0, 0), small_font, [width - 100, 25], "Score: " + str(score))
            Draw_text(window, (0, 0, 0), small_font, [width - 100, 50], "Money: " + str(money))

#Check if all enemies are defeated
            if enemies == [] and remaining_enemies == []:
                action = "Shop"
                music_channel.stop()
                total_time += timer

#Check if player is dead
            if player_health <= 0:
                player_health = 0
                action = "Dead"
                music_channel.stop()
                total_time += timer
                break

            pygame.display.flip()
            clock.tick(FPS)

#-------------------------------------------------------------------------Item Shop-------------------------------------------------------------------------
    if action == "Shop":
        player_pos = [width / 2, height / 2]
        player_move_direction = 0
        player_speed = 0

        hand_direction = pi / 2
        hand_distance = 40
        player_hand = [width / 2, height / 2 - hand_distance]
        up = down = left = right = False
        hand_forward = hand_backward = hand_left = hand_right = False

        selected_item = None
        itme_cost = 0

        player_weapon = 1
        bullets = []
        lasers = []
        deflects = []
        rockets = []

        enemies = []

        potential_items = []

#The shop works by creating a list of potential items, then selecting 12 randomly out of that list to be purchasable
        for i in range(0, 200 - player_maxhealth, 10):
            potential_items.append("+Maximum health")

        for i in range(15 - lightsaber_damage):
            potential_items.append("+Lightsaber damage")

        for i in range(0, 90 - shield_angle, 5):
            potential_items.append("+Shield angle")

        for i in range(12):
            potential_items.append("Health pack")

        for i in range(12):
            potential_items.append("Trip mine")

        items = []
        for i in range(12):
            item = random.choice(potential_items)
            items.append(item)

        buttons = [Button([width - 550, height - 100, 500, 75], "Next wave", regular_font), Button([0, 0, 200, 50], "Quit to menu", small_font), Button([50, height - 100, 125, 75], "Buy", regular_font)]
        for item_number, item in enumerate(items):
            row = item_number // 3
            if (item_number + 1) % 3 == 0:
                column = 2
            elif (item_number + 1) % 3 == 1:
                column = 1
            elif (item_number + 1) % 3 == 2:
                column = 0
            buttons.append(Button([(column + 1) * 95 + column * 300, (row + 1) * 25 + row * 50 + height / 4, 300, 50], item, small_font))
        while action == "Shop":
            window.fill((255, 255, 255))
            mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_down = True
                    if event.button == 1:
                        for button in buttons:
                            if button.rect[0] <= mouse_pos[0] <= button.rect[0] + button.rect[2] and button.rect[1] <= mouse_pos[1] <= button.rect[1] + button.rect[3]:
                                button.pressed = True
                                selected_button = button
                if event.type == pygame.MOUSEBUTTONUP:
                    mouse_down = False
                    if event.button == 1:
                        for item_number, button in enumerate(buttons[3:]):
                            if button.rect[0] <= mouse_pos[0] <= button.rect[0] + button.rect[2] and button.rect[1] <= mouse_pos[1] <= button.rect[1] + button.rect[3]:
                                button.pressed = False
                                if selected_button != None:
                                    if selected_button == button:
                                        selected_item = item_number + 3
                        if buttons[0].rect[0] <= mouse_pos[0] <= buttons[0].rect[0] + buttons[0].rect[2] and buttons[0].rect[1] <= mouse_pos[1] <= buttons[0].rect[1] + buttons[0].rect[3]:
                            buttons[0].pressed = False
                            if selected_button != None:
                                if selected_button == buttons[0]:
                                    player_health = player_maxhealth
                                    action = "Play game"
                                    wave += 1
                        if buttons[1].rect[0] <= mouse_pos[0] <= buttons[1].rect[0] + buttons[1].rect[2] and buttons[1].rect[1] <= mouse_pos[1] <= buttons[1].rect[1] + buttons[1].rect[3]:
                            buttons[1].pressed = False
                            if selected_button != None:
                                if selected_button == buttons[1]:
                                    action = "Menu"
                        if buttons[2].rect[0] <= mouse_pos[0] <= buttons[2].rect[0] + buttons[2].rect[2] and buttons[2].rect[1] <= mouse_pos[1] <= buttons[2].rect[1] + buttons[2].rect[3]:
                            buttons[2].pressed = False
                            if selected_button != None:
                                if selected_button == buttons[2]:
                                    if selected_item != None and (money >= item_cost or infinite_money == True):
                                        if buttons[selected_item].text == "+Maximum health":
                                            player_health += 10
                                            player_maxhealth += 10
                                        if buttons[selected_item].text == "+Lightsaber damage":
                                            lightsaber_damage += 1
                                        if buttons[selected_item].text == "+Shield angle":
                                            shield_angle += 5
                                        if buttons[selected_item].text == "Health pack":
                                            health_packs += 1
                                        if buttons[selected_item].text == "Trip mine":
                                            trip_mines += 1
                                        buttons.remove(buttons[selected_item])
                                        selected_item = None
                                        if infinite_money == False:
                                            money -= item_cost
                        else:
                            selected_button = None

            Draw_text(window, (0, 0, 0), small_font, [width / 2, height / 10 + 50], "Money: " + str(money))
            Draw_text(window, (0, 0, 0), regular_font, [width / 2, height / 10], "Shop")

#Item descriptions
            if selected_item != None:
                pygame.draw.rect(window, (0, 0, 255), [buttons[selected_item].rect[0] - 5, buttons[selected_item].rect[1] - 5, 310, 60], 5)
                if buttons[selected_item].text == "+Maximum health":
                    item_cost = 50
                    if money >= item_cost or infinite_money == True:
                        colour = (0, 128, 0)
                    else:
                        colour = (255, 0, 0)
                    Draw_text(window, colour, small_font, [width / 2, 2 * height / 3], "Increases maximum health by 10.")
                if buttons[selected_item].text == "+Lightsaber damage":
                    item_cost = 25
                    if money >= item_cost or infinite_money == True:
                        colour = (0, 128, 0)
                    else:
                        colour = (255, 0, 0)
                    Draw_text(window, colour, small_font, [width / 2, 2 * height / 3], "Increases damage per frame of lightsaber by 1 (+60 dps).")
                if buttons[selected_item].text == "+Shield angle":
                    item_cost = 35
                    if money >= item_cost or infinite_money == True:
                        colour = (0, 128, 0)
                    else:
                        colour = (255, 0, 0)
                    Draw_text(window, colour, small_font, [width / 2, 2 * height / 3], "Increases the angle of the shield by 10 degrees.")
                if buttons[selected_item].text == "Health pack":
                    item_cost = 20
                    if money >= item_cost or infinite_money == True:
                        colour = (0, 128, 0)
                    else:
                        colour = (255, 0, 0)
                    Draw_text(window, colour, small_font, [width / 2, 2 * height / 3], "Heals up to 50 health per use.")
                if buttons[selected_item].text == "Trip mine":
                    item_cost = 30
                    if money >= item_cost or infinite_money == True:
                        colour = (0, 128, 0)
                    else:
                        colour = (255, 0, 0)
                    Draw_text(window, colour, small_font, [width / 2, 2 * height / 3], "Sets up for 5 seconds, then blows up any enemies who get too close.")
                Draw_text(window, colour, small_font, [width / 2, 2 * height / 3 + 50], "Cost: " + str(item_cost))

            for button in buttons:
                if selected_button == button and mouse_down == True:
                    if button.rect[0] <= mouse_pos[0] <= button.rect[0] + button.rect[2] and button.rect[1] <= mouse_pos[1] <= button.rect[1] + button.rect[3]:
                        button.pressed = True
                    else:
                        button.pressed = False
                button.display()

            pygame.display.flip()
            clock.tick(FPS)

#------------------------------------------------------------------------Player dies-----------------------------------------------------------------------
    if action == "Dead":
        selected_button = None
        mouse_down = False
        buttons = [Button([0, 0, 200, 50], "Quit to menu", small_font)]
        if sound_effects == True:
            mario_death_sound.play()
        while action == "Dead":
            window.fill((255, 255, 255))
            mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_down = True
                    if event.button == 1:
                        for button in buttons:
                            if button.rect[0] <= mouse_pos[0] <= button.rect[0] + button.rect[2] and button.rect[1] <= mouse_pos[1] <= button.rect[1] + button.rect[3]:
                                button.pressed = True
                                selected_button = button
                if event.type == pygame.MOUSEBUTTONUP:
                    mouse_down = False
                    if event.button == 1:
                        if buttons[0].rect[0] <= mouse_pos[0] <= buttons[0].rect[0] + buttons[0].rect[2] and buttons[0].rect[1] <= mouse_pos[1] <= buttons[0].rect[1] + buttons[0].rect[3]:
                            buttons[0].pressed = False
                            if selected_button != None:
                                if selected_button == buttons[0]:
                                    action = "Menu"
                        else:
                            selected_button = None

#Calculate total score
            Draw_text(window, (255, 0, 0), large_font, [width / 2, height / 3], "You died!")
            Draw_text(window, (0, 128, 0), regular_font, [width / 2, 2 * height / 3 - 125], "Enemy death score: " + str(score))
            Draw_text(window, (0, 128, 0), regular_font, [width / 2, 2 * height / 3 - 75], "Wave bonus: " + str(wave * 100))
            Draw_text(window, (0, 128, 0), regular_font, [width / 2, 2 * height / 3 - 25], "Time bonus: " + str(int(total_time / 60 * 10)))
            Draw_text(window, (0, 128, 0), regular_font, [width / 2, 2 * height / 3 + 25], "Money bonus: " + str(money * 10))
            Draw_text(window, (0, 128, 0), regular_font, [width / 2, 2 * height / 3 + 75], "Difficulty multiplier: " + str(difficulty))
            Draw_text(window, (0, 0, 255), regular_font, [width / 2, 2 * height / 3 + 125], "Total score: " + str((score + wave * 100 + int(total_time / 60 * 10) + money * 10) * difficulty))
            for button in buttons:
                if selected_button == button and mouse_down == True:
                    if button.rect[0] <= mouse_pos[0] <= button.rect[0] + button.rect[2] and button.rect[1] <= mouse_pos[1] <= button.rect[1] + button.rect[3]:
                        button.pressed = True
                    else:
                        button.pressed = False
                button.display()

            pygame.display.flip()
            clock.tick(FPS)
