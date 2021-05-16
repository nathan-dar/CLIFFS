import pygame as pg
from settings import *
from random import choice, randrange
vec = pg.math.Vector2

class Spritesheet:
    def __init__(self, filename):
        self.images = pg.image.load(filename).convert()

    def get_image(self, x, y, WIDTH, HEIGHT):
        image = pg.Surface((WIDTH,HEIGHT))
        image.blit(self.images, (0, 0), (x, y, WIDTH, HEIGHT))
        image = pg.transform.scale(image, (WIDTH * 5, HEIGHT * 5))
        return image

class Player(pg.sprite.Sprite):
    def __init__(self, game):
        self._layer = PLAYER_LAYER
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.walking = False
        self.jumping = False
        self.current_frame = 0
        self.last_update = 0
        self.load_images()
        self.image = self.standing_frames[0]
        self.rect = self.image.get_rect()
        self.rect.center = (50, HEIGHT - 100)
        self.pos = vec(50, HEIGHT - 100)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)

    def load_images(self):
        self.standing_frames = [self.game.images.get_image(19, 0, 11, 16),
                                self.game.images.get_image(66, 0, 11, 16)]
        for frame in self.standing_frames:
            frame.set_colorkey(RED)

        self.walk_frames_r = [self.game.images.get_image(50, 0, 12, 16),
                              self.game.images.get_image(2, 0, 12, 16)]
        for frame in self.walk_frames_r:
            frame.set_colorkey(RED)

        self.walk_frames_l = []
        for frame in self.walk_frames_r:
            self.walk_frames_l.append(pg.transform.flip(frame, True, False))

        self.jump_frame_r = [self.game.images.get_image(34, 0, 12, 16)]
        for frame in self.jump_frame_r:
            frame.set_colorkey(RED)

        self.jump_frame_l = []
        for frame in self.jump_frame_r:
            self.jump_frame_l.append(pg.transform.flip(frame, True, False))


    def jump(self):
        self.rect.x += 2
        hits = pg.sprite.spritecollide(self, self.game.platforms, False)
        self.rect.x -= 2
        if hits and not self.jumping:
            self.jumping = True
            self.vel.y = -PLAYER_JUMP

    def jump_cut(self):
        if self.jumping:
            if self.vel.y < -10:
                self.vel.y = 1

    def update(self):
        self.animate()
        self.acc = vec(0, PLAYER_GRAV)
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT]:
            self.acc.x = -PLAYER_ACC
        if keys[pg.K_RIGHT]:
            self.acc.x = PLAYER_ACC

        self.acc.x += self.vel.x * PLAYER_FRICTION
        self.vel += self.acc
        if abs(self.vel.x) < 0.1:
            self.vel.x = 0
        self.pos += self.vel + 0.5 * self.acc
        if self.pos.x > WIDTH:
            self.pos.x = 0
        if self.pos.x < 0:
            self.pos.x = WIDTH

        self.rect.midbottom = self.pos

    def animate(self):
        now = pg.time.get_ticks()
        if self.vel.x != 0:
            self.walking = True
        else:
            self.walking = False

        if self.walking:
            if now - self.last_update > 250:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.walk_frames_l)
                if self.vel.x > 0:
                    self.image = self.walk_frames_r[self.current_frame]
                else:
                    self.image = self.walk_frames_l[self.current_frame]

        if not self.jumping and not self.walking:
            if now - self.last_update > 350:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.standing_frames)
                self.image = self.standing_frames[self.current_frame]

        if self.jumping:
            if now - self.last_update > 200:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.jump_frame_l)
                if self.vel.x > 0:
                    self.image = self.jump_frame_r[self.current_frame]
                else:
                    self.image = self.jump_frame_l[self.current_frame]
        self.mask = pg.mask.from_surface(self.image)

class Background(pg.sprite.Sprite):
    def __init__(self, game):
        self._layer = BACKGROUND_LAYER
        self.groups = game.all_sprites, game.background
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = choice(self.game.background_images)
        self.image.set_colorkey(RED)
        self.rect = self.image.get_rect()
        scale = randrange(400,500) / 100
        self.image = pg.transform.scale(self.image, (int(self.rect.width * scale),
                                                     int(self.rect.height * scale)))
        self.rect.x = randrange(WIDTH - self.rect.width)
        self.rect.y = randrange(-800, -50)

    def update(self):
        if self.rect.top > HEIGHT:
            self.kill()

class Platform(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = PLATFORM_LAYER
        self.groups = game.all_sprites, game.platforms
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        images = [self.game.images.get_image(0, 22, 16, 7),
                  self.game.images.get_image(22, 22, 20, 7),
                  self.game.images.get_image(47, 22, 33, 7)]
        self.image = choice(images)
        self.image.set_colorkey(RED)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        if randrange(100) < POW_SPAWN_PCT:
            PowUp(self.game, self)

class PowUp(pg.sprite.Sprite):
    def __init__(self, game, plat):
        self._layer = POWUP_LAYER
        self.groups = game.all_sprites, game.powerups
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.plat = plat
        self.type = choice(['boost'])
        self.image = self.game.images.get_image(1, 48, 16, 16)
        self.image.set_colorkey(RED)
        self.rect = self.image.get_rect()
        self.rect.centerx = self.plat.rect.centerx
        self.rect.bottom = self.plat.rect.top - 5

    def update(self):
        self.rect.bottom = self.plat.rect.top - 5
        if not self.game.platforms.has(self.plat):
            self.kill()

class Enemy(pg.sprite.Sprite):
    def __init__(self, game):
        self._layer = ENEMY_LAYER
        self.groups = game.all_sprites, game.enemy
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image_up = self.game.images.get_image(4,32,12,16)
        self.image_up.set_colorkey(RED)
        self.image_down = self.game.images.get_image(19,32,12,16)
        self.image_down.set_colorkey(RED)
        self.image = self.image_up
        self.rect = self.image.get_rect()
        self.rect.centerx = choice ([-100, WIDTH + 100])
        self.vx = randrange(1, 4)
        if self.rect.centerx > WIDTH:
            self.vx *= -1
        self.rect.y = randrange(HEIGHT /2)
        self.vy = 0
        self.dy = 0.5

    def update(self):
        self.rect.x += self.vx
        self.vy += self.dy
        if self.vy > 3 or self.vy < -3:
            self.dy *= -1
        center = self.rect.center
        if self.dy < 0:
            self.image = self.image_up
        else:
            self.image = self.image_down
        self.rect = self.image.get_rect()
        self.mask = pg.mask.from_surface(self.image)
        self.rect.center = center
        self.rect.y += self.vy
        if self.rect.left > WIDTH + 100 or self.rect.right < -100:
            self.kill()
