import pygame
from pygame.sprite import Sprite

class Alien(Sprite):
    '''Class for a single alien'''

    def __init__(self, ai_game):
        '''initializes alien and sets its initial position'''
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings

        # Load image of alien and assignment of the rect attribute
        self.image = pygame.transform.scale(pygame.image.load('images/alien.png'), (50, 50))
        self.rect = self.image.get_rect()

        # Every new alien appears in the upper left corner of the screen
        self.rect.x = self.rect.width
        self.rect.y = self.rect.height

        # Saving alien position as float
        self.x = float(self.rect.x)

    def check_edges(self):
        ''''''
        screen_rect = self.screen.get_rect()
        if self.rect.right >= screen_rect.right or self.rect.left <= 0:
            return True
        
    def update(self):
        ''''''
        self.x += self.settings.alien_speed * self.settings.fleet_direction
        self.rect.x = self.x
    
    