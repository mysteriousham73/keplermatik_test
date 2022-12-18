import numpy as np
from PIL import Image
import copy

from os import environ as env
import platform
import os

ESC = '\u001B['
eraseScreen = ESC + '2J'

if platform.system() == 'Windows':
    clearTerminal = '{}{}0f'.format(eraseScreen, ESC)
    # 1. Erases the screen (Only done in case '2' is not supported)
    # 2. Erases the whole screen including scrollback buffer
    # 3. Moves cursor to the top-left position
    # More info: https://www.real-world-systems.com/docs/ANSIcode.html
else:
    clearTerminal = '{}{}3J{}H'.format(eraseScreen, ESC, ESC)



class TUIMap():
    def __init__(self):
        self.satellite_latitude = 0
        self.satellite_longitude = 0
        self.previous_row = 0
        self.previous_col = 0
        self.character_columns = 160
        self.character_rows = 50
        # Load the input image
        self.image = Image.open("dist/map.png")
        #self.image = self.image.resize((self.character_columns, self.character_rows))

        # Create the text image with 50 character columns and 30 character rows
        self.base_image = self.create_text_image()
        self.map_buffer = copy.deepcopy(self.base_image)

    def create_text_image(self):
        # Convert the input image to a numpy array
        image_array = np.array(self.image)
        #print (image_array)

        # Get the dimensions of the input image
        self.image_height, self.image_width = image_array.shape

        # Calculate the width and height of each character in the output text image
        character_width = self.image_width / self.character_columns
        character_height = self.image_height / self.character_rows

        # Create an empty list to store the text image
        text_image = []

        # Iterate over the rows and columns of the output text image
        for row in range(self.character_rows):
            text_image.append([])
            for col in range(self.character_columns):
                # Calculate the average color of the corresponding area in the input image
                average_color = np.mean(image_array[int(row * character_height):int((row + 1) * character_height), int(col * character_width):int((col + 1) * character_width)], axis=(0, 1))
                #print(average_color)
                # Convert the average color to a character
                if average_color < .7:
                    # Black pixel
                    text_image[row].append("X")
                else:
                    # White pixel
                    text_image[row].append(" ")

        return text_image

    def update_map(self, lat, lon):
        self.satellite_latitude = lat
        self.satellite_longitude = lon
        # Calculate the width and height of each character in the output text image
        character_width = self.image_width / self.character_columns
        character_height = self.image_height / self.character_rows

        # Map the latitude and longitude to the corresponding row and column
        row = int((90 - lat) / 180 * self.character_rows)
        col = int((180 + lon) / 360 * self.character_columns)

        #print(self.previous_row)
        #print(self.previous_col)
        #print(row)
        #print(col)

        if (self.previous_row != row or self.previous_col != col):

            self.map_buffer[self.previous_row][self.previous_col] = self.base_image[self.previous_row][self.previous_col]

            self.map_buffer[row][col] = "\033[37m\033[91mO\033[37m"
            self.previous_row = row
            self.previous_col = col

            print(clearTerminal)
            print("\033[37m")
            for row in self.map_buffer:
                print("".join(row))



        #self.satellite_latitude = lat
        #self.satellite_longitude = lon

        return row, col




