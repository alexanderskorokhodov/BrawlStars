import os
import sys
from math import pi, cos, acos, sqrt

import pygame
from pygame.draw import line
ev: pygame.event

class Field:

    def __init__(self, mapName='DriedUpRiver.txt'):
