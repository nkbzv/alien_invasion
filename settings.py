class Settings():
    '''Class for all settings in the Alien Invasion'''

    def __init__(self):
        '''Initializes the game settings'''
        # Screen settings
        self.screen_width = 1400
        self.screen_height = 700
        self.bg_color = (230, 230, 230)
        
        # Ship settings
        self.ship_speed = 1.5
        self.ship_limit = 2

        # Bullet settings
        self.bullet_speed = 1.5
        self.bullet_width = 3
        self.bullet_height = 15
        self.bullet_color = (60, 60, 60)
        self.bullet_allowed = 5

        # Alien settings
        self.alien_speed = 1.5
        self.fleet_drop_speed = 1

        # Темп ускорения игры
        self.speedup_scale = 1.1

        # Темп роста стоимости пришельцев
        self.score_scale = 1.5

        self.initialize_dynamic_settings()

    def initialize_dynamic_settings(self):
        '''Инициализирует настройки, изменяющиеся в ходе игры'''
        self.ship_speed = 1.5
        self.bullet_speed = 3.0
        self.alien_speed = 1.5
        self.alien_points = 50

        # fleet_direction = 1 - to the left, -1 - to the right
        self.fleet_direction = 1

    def increase_speed(self):
        '''Увеличивает настройки скорости и стоимость пришельцев'''
        self.ship_speed *= self.speedup_scale
        self.bullet_speed *= self.speedup_scale
        self.alien_speed *= self.speedup_scale
        self.alien_points = int(self.alien_points * self.score_scale)