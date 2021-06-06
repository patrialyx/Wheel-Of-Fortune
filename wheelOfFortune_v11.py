
#######################################################################################################################
#                                                 IMPORTED MODULES                                                    #
#######################################################################################################################

import pygame
from PIL import Image
import time
import pandas as pd
import re
from spellchecker import SpellChecker
import wheelOfFortune_v1


#######################################################################################################################
#                                               PROVIDED FUNCTIONS                                                    #
#######################################################################################################################

# load dataset for keyword dictionary - provided
def load_stall_keywords(data_location="new_canteen_coordinates.xlsx"):
    # get list of canteens and stalls
    canteen_data = pd.read_excel(data_location, trim_ws=True)
    canteens = canteen_data['Canteen'].unique()
    canteens = sorted(canteens, key=str.lower)

    stalls = canteen_data['Stall'].unique()
    stalls = sorted(stalls, key=str.lower)

    keywords = {}
    for canteen in canteens:
        keywords[canteen] = {}

    copy = canteen_data.copy()
    copy.drop_duplicates(subset="Stall", inplace=True)
    stall_keywords_intermediate = copy.set_index('Stall')['Keywords'].to_dict()
    stall_canteen_intermediate = copy.set_index('Stall')['Canteen'].to_dict()

    for stall in stalls:
        stall_keywords = stall_keywords_intermediate[stall]
        stall_canteen = stall_canteen_intermediate[stall]
        keywords[stall_canteen][stall] = stall_keywords

    return keywords


# load dataset for price dictionary - provided
def load_stall_prices(data_location="new_canteen_coordinates.xlsx"):
    # get list of canteens and stalls
    canteen_data = pd.read_excel(data_location, trim_ws=True)
    canteens = canteen_data['Canteen'].unique()
    canteens = sorted(canteens, key=str.lower)

    stalls = canteen_data['Stall'].unique()
    stalls = sorted(stalls, key=str.lower)

    prices = {}
    for canteen in canteens:
        prices[canteen] = {}

    copy = canteen_data.copy()
    copy.drop_duplicates(subset="Stall", inplace=True)
    stall_prices_intermediate = copy.set_index('Stall')['Price'].to_dict()
    stall_canteen_intermediate = copy.set_index('Stall')['Canteen'].to_dict()

    for stall in stalls:
        stall_price = stall_prices_intermediate[stall]
        stall_canteen = stall_canteen_intermediate[stall]
        prices[stall_canteen][stall] = stall_price

    return prices


# load dataset for location dictionary - provided
def load_canteen_location(data_location="new_canteen_coordinates.xlsx"):
    # get list of canteens
    canteen_data = pd.read_excel(data_location, trim_ws=True)
    canteens = canteen_data['Canteen'].unique()
    canteens = sorted(canteens, key=str.lower)

    # get dictionary of {canteen:[x,y],}
    canteen_locations = {}
    for canteen in canteens:
        copy = canteen_data.copy()
        copy.drop_duplicates(subset="Canteen", inplace=True)
        canteen_locations_intermediate = copy.set_index('Canteen')['Location'].to_dict()
    for canteen in canteens:
        canteen_locations[canteen] = [int(canteen_locations_intermediate[canteen].split(',')[0]),
                                      int(canteen_locations_intermediate[canteen].split(',')[1])]

    return canteen_locations


# get user's location with the use of PyGame - provided
def get_user_location_interface():
    # get image dimensions
    image_location = 'NTUcampus.jpg'
    pin_location = 'pin.png'
    screen_title = "NTU Map"
    image = Image.open(image_location)
    image_width_original, image_height_original = image.size
    scaled_width = image_width_original
    scaled_height = image_height_original
    pinIm = pygame.image.load(pin_location)
    pinIm_scaled = pygame.transform.scale(pinIm, (60, 60))
    # initialize pygame
    pygame.init()
    # set screen height and width to that of the image
    screen = pygame.display.set_mode([image_width_original, image_height_original])
    # set title of screen
    pygame.display.set_caption(screen_title)
    # read image file and rescale it to the window size
    screenIm = pygame.image.load(image_location)

    # add the image over the screen object
    screen.blit(screenIm, (0, 0))
    # will update the contents of the entire display window
    pygame.display.flip()

    # loop for the whole interface remain active
    while True:
        # checking if input detected
        pygame.event.pump()
        event = pygame.event.wait()
        # closing the window
        if event.type == pygame.QUIT:
            pygame.display.quit()
            mouseX_scaled = None
            mouseY_scaled = None
            break
        # resizing the window
        elif event.type == pygame.VIDEORESIZE:
            screen = pygame.display.set_mode(
                event.dict['size'], pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE)
            screen.blit(pygame.transform.scale(screenIm, event.dict['size']), (0, 0))
            scaled_height = event.dict['h']
            scaled_width = event.dict['w']
            pygame.display.flip()
        # getting coordinate
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # get outputs of Mouseclick event handler
            (mouseX, mouseY) = pygame.mouse.get_pos()
            # paste pin on correct position
            screen.blit(pinIm_scaled, (mouseX - 25, mouseY - 45))
            pygame.display.flip()
            # return coordinates to original scale
            mouseX_scaled = int(mouseX * 1000 / scaled_width)
            mouseY_scaled = int(mouseY * 800 / scaled_height)
            # delay to prevent message box from dropping down
            time.sleep(0.2)
            break

    pygame.quit()
    pygame.init()
    return mouseX_scaled, mouseY_scaled


#####################################################################################################################
#                                                EXCEL SHEET CHANGES                                                #
#####################################################################################################################
canteen_stall_keywords = load_stall_keywords("new_canteen_coordinates.xlsx")
canteen_stall_prices = load_stall_prices("new_canteen_coordinates.xlsx")
canteen_locations = load_canteen_location("new_canteen_coordinates.xlsx")


#######################################################################################################################
#                                               IMPLEMENTED FUNCTIONS                                                 #
# --------------------------------------------------------------------------------------------------------------------#
# Author: Patria Lim Yun Xuan   Date: 12 April 2020    Time: 1815                                                     #
#######################################################################################################################
def search_by_keyword(keywords):
    """
    Keyword-based Search Function
    Search for all canteen stalls that match with 1,2...n user-inputted keywords and
    sort them into sets that match with 1,2...n keywords respectively.

    Parameters:
    keywords(string): cuisine/food type, separated by any special character, including space
    i.e.'chicken rice'

    Returns:
    lst_of_sets(list of sets of strings): List of sets. Each set consists of all the stalls
    and their corresponding canteens that matches with n keywords.
     i.e. [{'canteen_name - stall_name', 'canteen_name - stall_name',...}, {...}, set()]
    """

    # special input 'mm' allows user to exit to main menu anytime
    while keywords != 'mm':

        keyword_input_set = set(re.findall(r'\w+', keywords))
        misspelled = SpellChecker().unknown(list(keyword_input_set))

        for word in misspelled:
            keyword_input_set.remove(word)
            keyword_input_set.add(SpellChecker().correction(word))
            print(
                "\nPatriaBot: '%s' seems to be misspelled. Were you perhaps looking for '%s'? "
                "I'll try looking for %s instead." % (word, SpellChecker().correction(word),
                                                      SpellChecker().correction(word)))

        lst_of_strings = []

        for keyword in keyword_input_set:
            counter = 0
            for canteen_name, stall_dictionary in canteen_stall_keywords.items():
                for stall_name, stall_attributes in stall_dictionary.items():
                    stall_attributes_list = stall_attributes.lower().split(', ')
                    if keyword.lower() in stall_attributes_list:
                        lst_of_strings.append(canteen_name + ' - ' + stall_name)
                        counter += 1

            if counter == 0:
                print("\nPatriaBot: The keyword '%s' does not exist. Please try another keyword." % keyword)

        return [set([canteen_and_stall for canteen_and_stall in lst_of_strings if
                     lst_of_strings.count(canteen_and_stall) == n + 1]) for n in range(len(keyword_input_set))]
    else:
        main()
        exit()


def search_by_price(keywords):
    """
    Price-based Search Procedure
    On top of searching canteen stalls by user-inputted keywords, for every set of n matching keywords,
    this function arranges the canteen stalls in each set by price, from cheapest to most expensive.

    Parameters: (same as search_by_keyword function)
    keywords(string): cuisine/food type, separated by any special character, including space i.e.'chicken rice'
    """

    lst_of_sets = search_by_keyword(keywords)
    sorted_lst_of_lsts = []

    for n in reversed(range(len(lst_of_sets))):
        lst = [['\n%d canteen(s) match %d keyword(s):' % ((len(lst_of_sets[n])), n + 1), '', 0]]

        for canteen_and_stall in lst_of_sets[n]:  
            canteen_stall_list = canteen_and_stall.split(' - ')
            stall_price = canteen_stall_prices[canteen_stall_list[0]][canteen_stall_list[1]]
            canteen_stall_list.append(stall_price)
            lst.append(canteen_stall_list)

        sorted_lst = sorted(lst, key=lambda x: x[2])
        sorted_lst_of_lsts.append(sorted_lst)

    for lst in sorted_lst_of_lsts:
        print((lst.pop(0))[0])

        for canteen_stall_price in lst:
            print(lst.index(canteen_stall_price) + 1, ')', canteen_stall_price[0], '-', canteen_stall_price[1],
                  '- $', canteen_stall_price[2])


def search_nearest_canteens(user_locations, k):
    """
    Location-based Search Procedure
    Calculates the total distance of two inputted user-coordinates to all NTU canteens and sorts canteens by
    ascending distance from both users (shortest distance first).

    Parameters:
    user_locations(ls of tuples): [user A location, user B location]
    k: number of canteens to display
    """
    userA_location = user_locations[0]
    userB_location = user_locations[1]

    ls = [(euclidean_distance(userA_location)[n][0] + euclidean_distance(userB_location)[n][0],
           euclidean_distance(userA_location)[n][0], euclidean_distance(userB_location)[n][0],
           euclidean_distance(userB_location)[n][1]) for n in range(len(canteen_locations))]

    k_nearest_canteens = sorted(ls)[:k]

    for element in k_nearest_canteens:
        print(k_nearest_canteens.index(element) + 1, ')', '%s \nDistance away from you: %.2fm\nDistance away from your '
                                                          'friend: %.2fm' % (element[3], element[1], element[2]))


######################################################################################################################
#                                               ASSISTING FUNCTIONS                                                  #
######################################################################################################################
def search_again():
    """
    Loop searches
    Boolean function to ask if user wants to perform the sane search again

    Parameters:
    None

    Returns:
    Boolean value
    """
    valid = True
    repeat = False

    while valid:
        repeat = input('\nPatriaBot: Would you like to search again?(Y/N)\n\n|ENTER (Y/N):')
        if repeat in ['Y', 'y']:
            repeat = True
            valid = False
        elif repeat in ['N', 'n']:
            main()
            valid = False
        else:
            print('\nPatriaBot: Input entered was invalid. Please enter \'Y\' or \'N\'.')

    return repeat


def euclidean_distance(user_location):
    """
    Euclidean distance
    Find euclidean distance between canteen and user location.

    Parameters:
    user_location(tuple): coordinates of user location

    Returns:
    [(euclidean distance, canteen), ...] (list): list of tuples of distance from user and its corresponding canteen
    """
    return [(((user_location[0] - coordinates[0]) ** 2 + (user_location[1] - coordinates[1]) ** 2) ** 0.5, canteen_name)
            for canteen_name, coordinates in canteen_locations.items()]


######################################################################################################################
#                                                MAIN PROCEDURE                                                      #
######################################################################################################################

# edited display format for increased user-friendliness
def main():
    """main procedure to select different kinds of searches"""
    print("\n============ WELCOME TO NTU'S ============")
    print("======= 'WHERE TO EAT' CANTEEN APP =======")
    print("\n---------F&B Recommendation Menu----------\n")
    print("     Option 1 -- Display Data")
    print("     Option 2 -- Keyword-based Search")
    print("     Option 3 -- Price-based Search")
    print("     Option 4 -- Location-based Search")
    print("     Option 5 -- Wheel of Food Randomiser")
    print("     Option 6 -- Exit Program\n")
    print("==========================================")

    # to be changed whenever number of options is changed
    number_of_options = 6

    # PatriaBot Intro Questions
    option = input(
        "\nPatriaBot: Would you like to do a keyword-based search (ENTER '2'), a price-based search (ENTER '3'), a "
        "location-based search (ENTER '4'), or spin the Wheel of Food Randomiser (ENTER '5')? [Note:"
        " To view possible input keywords, ENTER '1'. To exit application, ENTER '6'.]\n\n|ENTER OPTION:")

    # catch Type / Out of Range errors
    while (not option.isdigit()) or int(option) > number_of_options or int(option) < 0:
        print('\nPatriaBot: You have selected an invalid option. Please try again.')
        option = input(
            "\nPatriaBot: Would you like to do a keyword-based search (ENTER '2'), a price-based search (ENTER '3'), "
            "or a location-based search (ENTER '4')? or spin the Wheel of Food Randomiser (ENTER '5')? "
            "[Note: To view possible input keywords, ENTER '1'. To exit application, ENTER '6'.] \n\n|ENTER OPTION:")

    option = int(option)

    if option == 1:
        # print provided dictionary data structures
        print("\nPatriaBot: Here are the possible options.")
        print(
            "\n======================================================================================================")
        print("Keyword Dictionary: ", canteen_stall_keywords)
        print("Price Dictionary: ", canteen_stall_prices)
        print("Location Dictionary: ", canteen_locations)
        print(
            "========================================================================================================")
        main()

    elif option == 2:

        # introduction
        print(
            "\nPatriaBot: You have selected 'Keyword-based Search'! Tell me what kind of cuisine or type of food you "
            "are craving for today! I will find just the right stalls. [Not what you are looking for? ENTER 'mm' to "
            "return to the main menu.]")

        loop = True
        while loop:
            # calls search_by_keyword function
            lst_of_sets = search_by_keyword(input("\nPatriaBot: What cuisine/type of food are you looking for today? "
                                                  "E.g. 'Halal, Malay, Chicken'\n\n|ENTER KEYWORDS:"))

            # reverses list so that the stalls matching the most keywords are printed first
            for n in reversed(range(len(lst_of_sets))):
                print('\n%d canteen(s) match %d keyword(s):' % ((len(lst_of_sets[n])), n + 1))
                for canteen_and_stall in lst_of_sets[n]:
                    print('=> ', canteen_and_stall)

            # search again
            if not search_again():
                loop = False

    elif option == 3:

        # introduction
        print(
            "\nPatriaBot: You have selected 'Price-based Search'! On a budget? No problem! Tell me what kind of "
            "cuisine or type of food you are craving for today! I will find the most affordable options. "
            "[Not what you are looking for? ENTER 'mm' to return to the main menu.]")

        # calls search_by_price procedure
        search_by_price(input("\nPatriaBot: What cuisine/type of food are you looking for today? I will find the "
                              "stalls and rank them by affordability. E.g. 'Halal, Malay, Chicken'"
                              "\n\n|ENTER KEYWORDS:"))

        # search again
        while search_again():
            search_by_price(input("\nPatriaBot: What cuisine/type of food are you looking for today? I will find the "
                                  "stalls and rank them by affordability. E.g. 'Halal, Malay, Chicken'"
                                  "\n\n|ENTER KEYWORDS:"))

    elif option == 4:

        # introduction
        print(
            "\nPatriaBot: You have selected 'Location-based Search'! Tell me your friend's location and your location! "
            "I will find the nearest canteens to both of you. [Not what you are looking for? ENTER 'mm' to return to "
            "the main menu.]")

        # temp_var introduced to give opportunity to user to go back to main menu
        temp_var = input("\nPatriaBot: Press 'Enter' key to open the map or enter 'mm' to return to main menu."
                         "\n\n|ENTER:")

        loop = True

        while temp_var != 'mm' and loop:

            # initialising user locations
            userA_location = (None, None)
            userB_location = (None, None)

            # error-handling: if user accidentally pressed the close screen button ('X')
            while userA_location == (None, None) or userB_location == (None, None):
                # obtain first user location

                print("\nPatriaBot: Here is a map. Please click on the location where you are at now.")
                userA_location = get_user_location_interface()
                print("Your location (x, y): ", userA_location)
                # obtain second user location
                print("\nPatriaBot: Now, click on the location where your friend is at.")
                userB_location = get_user_location_interface()
                print("Your friend's location (x, y): ", userB_location)

            user_locations = [userA_location, userB_location]

            # obtain k
            k = input(
                '\nPatriaBot: Please enter the number of canteens you want to find. (Range 1-%d)\n\n|ENTER A NUMBER:'
                % len(canteen_locations))

            # error-handling: catches cases where user enters letters or numbers out of range
            if not k.isdigit() or int(k) > len(canteen_locations):
                k = 1 # as required by assignment, default all wrong inputs to 1

            k = int(k)
            print("\nPatriaBot: Here are %s nearest canteens!" % k)

            search_nearest_canteens(user_locations, k)

            # search again
            if not search_again():
                loop = False

        else:
            main()
            exit()

    elif option == 5:

        print('\nPatriaBot: Click on the pop-up screen.')
        print(wheelOfFortune_v1.start()) # view this module i created in another python file
        main()
        exit()

    elif option == 6:

        # exit the program
        print("\nPatriaBot: I hope I've found you just the right food stall! Goodbye, and have a great meal! :) ")
        exit()


print("PatriaBot has entered the chat.")
user_name = input("\nPatriaBot: Hello! I'm Patria, your canteen search assistant. What is your name? \n\n|ENTER NAME:")
print("\nPatriaBot: Welcome, %s!" % user_name)
main()
