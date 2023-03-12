import sys
from time import sleep
import random

import pygame

from settings import Settings
from game_stats import GameStats
from scoreboard import Scoreboard
from ship import Ship
from bullet import Bullet
from alien import Alien
from button import Button

class AlienInvasion:
    '''Класс для управления ресурсами и поведением игры.'''

    def __init__(self):
        '''Инициализирует игру и создает игровые ресурсы.'''
        pygame.init()
        self.settings = Settings()

        # Fullscreen mode
        #self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        #self.settings.screen_width = self.screen.get_rect().width
        #self.settings.screen_height = self.screen.get_rect().height

        # Window screen mode
        self.screen = pygame.display.set_mode((self.settings.screen_width, self.settings.screen_height))
        self.background_surface = pygame.Surface((self.settings.screen_width, self.settings.screen_height))
        pygame.display.set_caption('Alien Invasion')

        # Создание экземпляра для хравнения игровой статистики и панели результатов
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)

        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()

        self._create_fleet()

        # Создание кнопки Play.
        self.play_button = Button(self, 'Play')

        # Создание звездного неба.
        #self.stars()

    def run_game(self):
        '''Запуск основного цикла игры.'''
        while True:
            self._check_events()

            if self.stats.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()

            self._update_screen()

    def stars(self):
        '''Заполнение поверхности звездами'''
        # Рисование звезд на поверхности
        for _ in range(300):
            self.star_x = random.randint(0, self.settings.screen_width)
            self.star_y = random.randint(0, self.settings.screen_height)
            self.star_size = random.randint(1, 3)
            self.star_brightness = random.randint(100, 255)
            pygame.draw.circle(self.background_surface, (self.star_brightness, self.star_brightness, self.star_brightness), (self.star_x, self.star_y), self.star_size)

    def _update_screen(self):
        '''Обновляет изображения на экране и отображает новый экран.'''
        #self.screen.fill(self.settings.bg_color)
        self.stars()
        self.background_surface.scroll(-1, 0)
        self.screen.blit(self.background_surface, (0, 0))
        #pygame.display.update()

        self.ship.blitme()
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.aliens.draw(self.screen)

        # Вывод информации о счете
        self.sb.show_score()
        # Кнопка Play отображается в том случае, если игра неактивна.
        if not self.stats.game_active:
            self.play_button.draw_button()

        
        # Отображение последнего прорисованного экрана.
        pygame.display.flip()
        
    
    def _fire_bullet(self):
        ''''''
        if len(self.bullets) < self.settings.bullet_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)
    
    def _update_bullets(self):
        ''''''
        self.bullets.update()
        #
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
        #        
        self._check_bullet_alien_collisions()

    def _check_bullet_alien_collisions(self):
        ''''''
        collisions = pygame.sprite.groupcollide(self.bullets, self.aliens, True, True)
        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)
            self.sb.prep_score()
            self.sb.check_high_score()

        if not self.aliens:
            # Уничтожение снарядов, провышение скорости и создание нового флота
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()

            # Увеличение уровня
            self.stats.level += 1
            self.sb.prep_level()

    def _create_fleet(self):
        '''Создаем флот пришельцев'''
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        available_space_x = self.settings.screen_width - (1.3 * alien_width)
        number_aliens_x = available_space_x // (1.3 * alien_width)

        #
        ship_height = self.ship.rect.height
        available_space_y = self.settings.screen_height - (1.3 * alien_height) - ship_height
        number_rows = available_space_y // (1.3 * alien_height)
        #
        for row_number in range(int(number_rows)):
            for alien_number in range(int(number_aliens_x)):
                self._create_alien(alien_number, row_number)

    def _create_alien(self, alien_number, row_number):
        '''Создаем одного пришельца'''
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        if row_number % 2 == 0:
            alien.x = alien_width + 1.3 * alien_width * alien_number
        else:
            alien.x = 1.5 * alien_width + 1.3 * alien_width * alien_number
        alien.rect.x = alien.x
        alien.rect.y = alien_height + 1.3 * alien_height * row_number
        self.aliens.add(alien)

    def _update_aliens(self):
        '''Update position of all aliens'''
        self._check_fleet_edges()
        self.aliens.update()

        # Проверка коллизий "прищелец - корабль"
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()

        # Проверить добрались ли пришельцы до нижнего края экрана
        self._check_aliens_bottom()

    def _check_fleet_edges(self):
        ''''''
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _change_fleet_direction(self):
        ''''''
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _ship_hit(self):
        '''Обрабатывает столкновение корабля с пришельцем'''
        if self.stats.ships_left > 1:
            # Уменьшение ship_left и обновление панели счета
            self.stats.ships_left -= 1
            self.sb.prep_ships()

            # Очистка списков пришельцев и снарядов
            self.aliens.empty()
            self.bullets.empty()

            # Создание нового флота и размещение корабля в центре
            self._create_fleet()
            self.ship.center_ship()

            # Пауза
            sleep(0.5)
        else:
            self.stats.game_active = False
            pygame.mouse.set_visible(True)

    def _check_aliens_bottom(self):
        '''Проверяет, добрались ли пришельцы до нижнего края экрана'''
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                # Происходит то же, что и с кораблем
                self._ship_hit()
                break

    def _check_play_button(self, mouse_pos):
        '''Запускает новую игру при нажатии кнопки Play'''
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.stats.game_active:
            # Сброс игровых настроек
            self.settings.initialize_dynamic_settings()

            # Сброс игровой статистики
            self.stats.reset_stats()
            self.stats.game_active = True
            self.sb.prep_score()
            self.sb.prep_level()
            self.sb.prep_ships()

            # Очистка списков пришельцев и снарядов
            self.aliens.empty()
            self.bullets.empty()

            # Создание нового флота и размещение корабля в центре
            self._create_fleet()
            self.ship.center_ship()

            # Скрыть указатель мыши
            pygame.mouse.set_visible(False)

    def _check_events(self):
        '''Обрабатывает нажатия клавиш и события мыши'''
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                with open('record.txt', 'w') as f:
                    f.write(str(self.stats.high_score))
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)
    
    def _check_keydown_events(self, event):
        '''Реагирует на нажатие клавиш.'''
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            with open('record.txt', 'w') as f:
                f.write(str(self.stats.high_score))
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()
    
    def _check_keyup_events(self, event):
        '''Реагирует на отпускание клавиш.'''
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False

if __name__ == '__main__':
    # Создание экземляра и запуск игры.
    ai = AlienInvasion()
    ai.run_game()

