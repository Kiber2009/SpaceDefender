import pygame
import os
import sys
import json
import random

# Music: https://musiclab.chromeexperiments.com/Song-Maker/song/5364768818987008

FPS = 60
BULLET_SPEED = 10

pygame.init()

pygame.mixer.music.load("data/sound/music.wav")
pygame.mixer.music.play(-1)


def check_save(_save):
    if _save['settings']['stars'] > 3:
        _save['settings']['stars'] = 3
    elif _save['settings']['stars'] < 0:
        _save['settings']['stars'] = 0

    if _save['settings']['music']:
        pygame.mixer.music.unpause()
    else:
        pygame.mixer.music.pause()

    if _save['money'] < 0:
        _save['money'] = 0

    if _save['damage'] < 1:
        _save['damage'] = 1
    elif _save['damage'] > 5:
        _save['damage'] = 5

    if _save['speed'] < 1:
        _save['speed'] = 1
    elif _save['speed'] > 5:
        _save['speed'] = 5

    return _save


with open('save.json', 'r') as _f:
    save = check_save(json.load(_f))

screen_info = pygame.display.Info()
size = width, height = screen_info.current_w, screen_info.current_h
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()
all_sprites = pygame.sprite.AbstractGroup()

enemys = pygame.sprite.Group()
bullets = pygame.sprite.Group()

cost = [100, 500, 1000, 1500]

wave = 0
defeat = False


def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"[ERROR] Image '{name}' not found")
        sys.exit()
    image = pygame.image.load(fullname)
    if color_key is not None:
        image = image.convert()
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y, speed):
        super().__init__(all_sprites)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)
        self.delay = FPS // speed
        self.cur_delay = 0

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))

    def update(self):
        if self.cur_delay == 0:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]
            self.cur_delay = self.delay
        else:
            self.cur_delay -= 1


class Bullet(pygame.sprite.Sprite):
    image = load_image("image/bullet.png")

    def __init__(self, x, y):
        super().__init__(all_sprites)
        self.image = pygame.transform.scale(Bullet.image, (10, 25))
        self.rect = self.image.get_rect().move(x, y)
        self.add(bullets)

    def del_(self):
        self.remove(all_sprites, bullets)
        del self

    def update(self):
        for _ in range(BULLET_SPEED):
            self.rect.y -= 1
        if self.rect.y < 0:
            self.del_()


class Player(AnimatedSprite):
    image = pygame.transform.scale(load_image('image/player.png', -1), (640, 160))

    def __init__(self, x, y):
        super().__init__(Player.image, 4, 1, x, y, 16)


class Enemy(AnimatedSprite):
    def __init__(self, x, y, hp, speed):
        super().__init__(load_image('image/enemy1.png', -1), 2, 1, x, y, 2)
        self.hp = hp
        self.speed = speed
        self.add(enemys)
        self.v = random.choice([True, False])

    def del_(self):
        self.remove(all_sprites, enemys)
        del self

    def update(self):
        global defeat
        super().update()
        temp = pygame.sprite.spritecollideany(self, bullets)  # type: Bullet
        if temp:
            self.hp -= save['damage']
            temp.del_()
        if self.v:
            for _ in range(self.speed):
                self.rect.x += 1
            if self.rect.x >= width - 140:
                self.rect.x = width - 141
                self.v = False
                self.rect.y += 130
        else:
            for _ in range(self.speed):
                self.rect.x -= 1
            if self.rect.x <= 0:
                self.rect.x = 1
                self.v = True
                self.rect.y += 130
        if self.rect.y > height or pygame.sprite.collide_mask(self, player) or defeat:
            self.hp = 0
            defeat = True
        if self.hp <= 0:
            self.del_()


class Stars:
    def __init__(self, count):
        s = []
        for i in range(count):
            s.append((random.random() * width, random.random() * height, 1, 1))
        self.stars = tuple(s)

    def draw(self, surface):
        for i in self.stars:
            surface.fill(pygame.Color('white'), i)


class Menu:
    def __init__(self, surface):
        self.cur_scene = 0
        self.surface = surface

    def run(self):
        if self.cur_scene == 0:
            self.scene_main()
        elif self.cur_scene == 1:
            self.scene_help()
        elif self.cur_scene == 2:
            self.scene_settings()
        elif self.cur_scene == 3:
            self.scene_play()
        elif self.cur_scene == 4:
            self.scene_score()
        elif self.cur_scene == 5:
            self.scene_shop()

    def draw_button(self, text, y, text_color=(0, 0, 0), rect_color=(100, 255, 100), x=50):
        text = pygame.font.Font(None, 100).render(text, True, text_color)
        pygame.draw.rect(self.surface, rect_color, (x - 10, y - 10, text.get_width() + 20, text.get_height() + 20))
        self.surface.blit(text, (x, y))

    def click(self, pos):
        global running, save, stars, defeat, wave, player
        if self.cur_scene == 0:
            if pos[0] in range(50, 334) and pos[1] in range(500, 569):
                self.cur_scene = 1
            elif pos[0] in range(50, 268) and pos[1] in range(600, 669):
                _quit()
            elif pos[0] in range(50, 412) and pos[1] in range(400, 471):
                self.cur_scene = 2
            elif pos[0] in range(50, 280) and pos[1] in range(200, 271):
                defeat = False
                wave = 0
                self.cur_scene = 3
                player.rect.x = (width / 2) - 80
            elif pos[0] in range(50, 441) and pos[1] in range(300, 371):
                self.cur_scene = 5
        elif self.cur_scene == 1:
            if pos[0] in range(50, 96) and pos[1] in range(60, 129):
                self.cur_scene = 0
        elif self.cur_scene == 2:
            if pos[0] in range(50, 96) and pos[1] in range(60, 129):
                self.cur_scene = 0
            elif pos[0] in range(346, 387) and pos[1] in range(200, 269):
                save['settings']['stars'] -= 1
                save = check_save(save)
                stars = Stars(500 * save['settings']['stars'])
            elif (pos[0] in range(543, 583) if save['settings']['stars'] == 0 else pos[0] in range(603, 643) if
                  save['settings']['stars'] == 1 else pos[0] in range(803, 843)) and pos[1] in range(200, 269):
                save['settings']['stars'] += 1
                save = check_save(save)
                stars = Stars(500 * save['settings']['stars'])
            elif pos[0] in range(340, 390) and pos[1] in range(310, 360):
                save['settings']['music'] = not save['settings']['music']
                check_save(save)
        elif self.cur_scene == 4:
            if pos[0] in range(round(width / 2 - 124.5), round(width / 2 + 124.5)) and pos[1] in range(400, 468):
                self.cur_scene = 3
                player.rect.x = (width / 2) - 80
                defeat = False
                wave = 0
            elif pos[0] in range(round(width / 2 - 243.5), round(width / 2 + 243.5)) and pos[1] in range(500, 568):
                self.cur_scene = 0
                defeat = False
                wave = 0
        elif self.cur_scene == 5:
            if pos[0] in range(50, 96) and pos[1] in range(60, 129):
                self.cur_scene = 0
            elif pos[0] in range(388, 581) and pos[1] in range(300, 368) and save['damage'] < 5:
                if save['money'] >= cost[save['damage'] - 1]:
                    save['damage'] += 1
                    save['money'] -= cost[save['damage'] - 2]
                save = check_save(save)
            elif pos[0] in range(535, 728) and pos[1] in range(400, 468) and save['speed'] < 5:
                if save['money'] >= cost[save['speed'] - 1]:
                    save['speed'] += 1
                    save['money'] -= cost[save['speed'] - 2]
                save = check_save(save)

    @staticmethod
    def gen_wave():
        for _ in range((wave + 4) - (15 * ((wave - 1) // 15))):
            Enemy(random.randint(10, width - 10), random.randint(10, height - 700), wave // 15 + 1, wave // 10 + 1)

    def esc(self):
        global defeat
        if self.cur_scene == 3:
            defeat = True

    def scene_main(self):
        self.surface.blit(pygame.font.Font(None, 150).render('Space Defender', True, (100, 255, 100)), (50, 50))
        self.draw_button('Играть', 200)
        self.draw_button('Улучшения', 300)
        self.draw_button('Настройки', 400)
        self.draw_button('Помощь', 500)
        self.draw_button('Выйти', 600)

    def scene_help(self):
        self.draw_button('X', 60, text_color=(255, 0, 0), rect_color=(0, 0, 0))
        self.surface.blit(pygame.font.Font(None, 150).render('Помощь', True, (100, 255, 100)), (150, 50))
        font = pygame.font.Font(None, 100)
        self.surface.blit(font.render('A - Движение влево', True, (100, 255, 100)), (50, 200))
        self.surface.blit(font.render('D - Движение вправо', True, (100, 255, 100)), (50, 300))
        self.surface.blit(font.render('Space - Выстрел', True, (100, 255, 100)), (50, 400))

    def scene_settings(self):
        self.draw_button('X', 60, text_color=(255, 0, 0), rect_color=(0, 0, 0))
        self.surface.blit(pygame.font.Font(None, 150).render('Настройки', True, (100, 255, 100)), (150, 50))
        font = pygame.font.Font(None, 100)
        self.surface.blit(font.render('Звёзды', True, (100, 255, 100)), (50, 200))
        t = 'Нет' if save['settings']['stars'] == 0 else 'Мало' if save['settings']['stars'] == 1 else 'Нормально' if \
            save['settings']['stars'] == 2 else 'Много'
        self.draw_button(f'< {t} >', 200, x=346)
        self.surface.blit(font.render('Музыка', True, (100, 255, 100)), (50, 300))
        pygame.draw.rect(self.surface, (100, 255, 100), (340, 310, 50, 50), 0 if save['settings']['music'] else 5)

    def scene_play(self):
        global wave, defeat, save
        if len(enemys) == 0:
            wave += 1
            self.gen_wave()
        if defeat:
            enemys.empty()
            save['money'] += ((wave - 1) * 10) + (100 * ((wave - 1) // 15))
            self.cur_scene = 4
        self.surface.blit(pygame.font.Font(None, 50).render(f'Волна: {wave}', True, (100, 255, 100)), (50, 50))

    def scene_score(self):
        font = pygame.font.Font(None, 150)
        self.surface.blit(font.render('Игра окончена', True, (100, 255, 100)), (width / 2 - 378, 50))
        font = pygame.font.Font(None, 100)
        t = font.render(f'Волны: {wave - 1}', True, (100, 255, 100))
        self.surface.blit(t, (width / 2 - t.get_width() / 2, 200))
        t = font.render(f'+{((wave - 1) * 10) + (100 * ((wave - 1) // 15))}$', True, (100, 255, 100))
        self.surface.blit(t, (width / 2 - t.get_width() / 2, 300))
        self.draw_button('Заново', 400, x=width / 2 - 124.5)
        self.draw_button('Главное меню', 500, x=width / 2 - 243.5)

    def scene_shop(self):
        self.draw_button('X', 60, text_color=(255, 0, 0), rect_color=(0, 0, 0))
        self.surface.blit(pygame.font.Font(None, 150).render('Улучшения', True, (100, 255, 100)), (150, 50))
        font = pygame.font.Font(None, 100)
        self.surface.blit(font.render(f'Баланс: {save["money"]}$', True, (100, 255, 100)), (50, 200))
        self.surface.blit(font.render(f"Урон: {save['damage']}/5", True, (100, 255, 100)),
                          (50, 300))
        if save['damage'] != 5:
            self.draw_button(f'{cost[save["damage"] - 1]}$', 300, x=388)
        self.surface.blit(font.render(f"Скорость: {save['speed']}/5", True, (100, 255, 100)),
                          (50, 400))
        if save['speed'] != 5:
            self.draw_button(f'{cost[save["speed"] - 1]}$', 400, x=535)


def _quit():
    global running
    with open('save.json', 'w') as f:
        json.dump(save, f)
    running = False


pygame.display.set_icon(load_image('icon.ico', -1))
pygame.display.set_caption('Space Defender')
player = Player((width / 2) - 80, height - 170)
running = True
stars = Stars(500 * save['settings']['stars'])
menu = Menu(screen)
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            _quit()
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                Bullet(player.rect.x + 75, player.rect.y - 5)
            if event.key == pygame.K_ESCAPE:
                menu.esc()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                menu.click(event.pos)
    if pygame.key.get_pressed()[pygame.K_a] or pygame.key.get_pressed()[pygame.K_LEFT]:
        player.rect.x -= save['speed'] * 4
        if player.rect.x < 0:
            player.rect.x = 0
    if pygame.key.get_pressed()[pygame.K_d] or pygame.key.get_pressed()[pygame.K_RIGHT]:
        player.rect.x += save['speed'] * 4
        if player.rect.x > (width - 160):
            player.rect.x = width - 160
    screen.fill('black')
    stars.draw(screen)
    menu.run()
    all_sprites.draw(screen)
    clock.tick(FPS)
    pygame.display.flip()
    all_sprites.update()
pygame.quit()
