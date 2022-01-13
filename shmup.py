import pygame
import random
from os import path


img_dir = path.join(path.dirname(__file__), 'img')
snd_dir = path.join(path.dirname(__file__), 'snd')

WIDTH = 480
HEIGHT = 600
FPS = 60
POWERUP_TIME = 5000


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)


pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Shmup")
clock = pygame.time.Clock()

font_name = pygame.font.match_font('calibri')


def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)


def newmob():
    m = Mob()
    all_sprites.add(m)
    mobs.add(m)


def newenemy():
    e = Enemy()
    all_sprites.add(e)
    enemy.add(e)


def clear_field():
    all_sprites.empty()
    mobs.empty()
    enemy.empty()
    bullets.empty()
    enemy_bullets.empty()
    powerups.empty()


def waiting():
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_p:
                    waiting = False


def draw_shield_bar(surf, x, y, pct):
    if pct < 0:
        pct = 0
    BAR_LENGHT = 100
    BAR_HEIGHT = 10
    fill = (pct / 100) * BAR_LENGHT
    outline_rect = pygame.Rect(x, y, BAR_LENGHT, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, RED, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)


def draw_boss_shield_bar(surf, x, y, pct):
    if level_cnt == 3:
        if pct < 0:
            pct = 0
        BAR_LENGHT = 100
        BAR_HEIGHT = 10
        fill = (pct / 100) * BAR_LENGHT
        outline_rect = pygame.Rect(x, y, BAR_LENGHT, BAR_HEIGHT)
        fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
        pygame.draw.rect(surf, BLUE, fill_rect)
        pygame.draw.rect(surf, WHITE, outline_rect, 2)


def draw_lives(surf, x, y, lives, img):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 30 * i
        img_rect.y = y
        surf.blit(img, img_rect)


def draw_powerup(surf, x, y, power, img):
    for i in range(power):
        img_rect = img.get_rect()
        img_rect.x = x + 30 * i
        img_rect.y = y
        surf.blit(img, img_rect)


def show_go_screen():
    screen.blit(background, background_rect)
    draw_text(screen, 'Level 1', 64, WIDTH / 2, HEIGHT / 4)
    draw_text(screen, 'WASD to move, Space to fire', 22, WIDTH / 2, HEIGHT / 2)
    draw_text(screen, 'Press "P" to begin', 18, WIDTH / 2, HEIGHT / 1.5)
    pygame.display.flip()
    waiting()


def level_2_screen():
    screen.blit(background, background_rect)
    draw_text(screen, 'Level 2', 64, WIDTH / 2, HEIGHT / 4)
    draw_text(screen, 'Press "P" to begin', 18, WIDTH / 2, HEIGHT / 1.5)
    pygame.display.flip()
    waiting()


def level_3_screen():
    screen.blit(background, background_rect)
    draw_text(screen, 'Level 3', 64, WIDTH / 2, HEIGHT / 4)
    draw_text(screen, 'Press "P" to begin', 18, WIDTH / 2, HEIGHT / 1.5)
    pygame.display.flip()
    waiting()


def end_screen():
    clock.tick(FPS)
    screen.blit(background, background_rect)
    draw_text(screen, 'The End', 64, WIDTH / 2, HEIGHT / 4)
    draw_text(screen, 'You can close the game', 18, WIDTH / 2, HEIGHT / 1.5)
    pygame.display.flip()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()


class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(player_img, (50, 38))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * .85 / 2)
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 0
        self.shield = 100
        self.shoot_delay = 250
        self.last_shoot = pygame.time.get_ticks()
        self.lives = 3

        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()
        self.power = 1
        self.power_time = pygame.time.get_ticks()

    def hide(self):
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (WIDTH / 2, HEIGHT + 200)

    def powerup(self):
        self.power += 1
        self.power_time = pygame.time.get_ticks()
        if self.power >= 3:
            self.power = 3

    def update(self):
        self.speedx = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_a]:
            self.speedx = -8
        if keystate[pygame.K_d]:
            self.speedx = 8
        if keystate[pygame.K_SPACE]:
            self.shoot()
        self.rect.x += self.speedx
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0
        if self.hidden and pygame.time.get_ticks() - self.hide_timer > 1000:
            self.hidden = False
            self.rect.centerx = WIDTH / 2
            self.rect.bottom = HEIGHT - 10
        if self.power >= 2 and pygame.time.get_ticks() - self.power_time > POWERUP_TIME:
            self.power -= 1
            self.power_time = pygame.time.get_ticks()

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shoot > self.shoot_delay:
            self.last_shoot = now
            if self.power == 1:
                bullet = Bullet(self.rect.centerx, self.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)
                shoot_sound.play()
            if self.power == 2:
                bullet1 = Bullet(self.rect.left, self.rect.centery)
                bullet2 = Bullet(self.rect.right, self.rect.centery)
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                bullets.add(bullet1)
                bullets.add(bullet2)
                shoot_sound.play()
            if self.power >= 3:
                bullet1 = Bullet(self.rect.left, self.rect.centery)
                bullet2 = Bullet(self.rect.right, self.rect.centery)
                bullet = Bullet(self.rect.centerx, self.rect.top)
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                all_sprites.add(bullet)
                bullets.add(bullet1)
                bullets.add(bullet2)
                bullets.add(bullet)
                shoot_sound.play()


class Boss(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(boss_img, (170, 170))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * .85 / 2)
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = 190
        self.speedx = 1
        self.speedy = 1
        self.shield = 100
        self.shoot_delay = 2000
        self.last_shoot = pygame.time.get_ticks()
        # self.lives = 1

    def update(self):
        self.rect.x += self.speedx
        if self.rect.left < 0 or self.rect.right > WIDTH:
            self.speedx = -self.speedx
        if running == True:
            self.shoot()

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shoot > self.shoot_delay:
            self.last_shoot = now
            enemy_bullet1 = EnemyBullet(self.rect.left + 20, self.rect.centery + 60)
            enemy_bullet2 = EnemyBullet(self.rect.right - 20, self.rect.centery + 60)
            enemy_bullet = EnemyBullet(self.rect.centerx, self.rect.bottom)
            all_sprites.add(enemy_bullet1)
            all_sprites.add(enemy_bullet2)
            all_sprites.add(enemy_bullet)
            enemy_bullets.add(enemy_bullet1)
            enemy_bullets.add(enemy_bullet2)
            enemy_bullets.add(enemy_bullet)
            enemy_shoot_sound.play()


class Mob(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_orig = random.choice(meteor_images)
        self.image_orig.set_colorkey(BLACK)
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * .85 / 2)
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-150, -100)
        self.speedy = random.randrange(1, 8)
        self.speedx = random.randrange(-3, 3)
        self.rot = 0
        self.rot_speed = random.randrange(-8, 8)
        self.last_update = pygame.time.get_ticks()

    def rotate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 50:
            self.last_update = now
            self.rot = (self.rot + self.rot_speed) % 360
            new_image = pygame.transform.rotate(self.image_orig, self.rot)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center

    def update(self):
        self.rotate()
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        if self.rect.top > HEIGHT + 75 or self.rect.left < -75 or self.rect.right > WIDTH + 75:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(1, 8)


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_orig = random.choice(enemy_images)
        self.image_orig.set_colorkey(BLACK)
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * .85 / 2)
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-150, -100)
        self.speedy = random.randrange(1, 2)
        self.speedx = random.randrange(-3, 3)
        self.shoot_delay = 1500
        self.last_shoot = pygame.time.get_ticks()

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shoot > self.shoot_delay:
            self.last_shoot = now
            enemy_bullet = EnemyBullet(self.rect.centerx, self.rect.bottom)
            all_sprites.add(enemy_bullet)
            enemy_bullets.add(enemy_bullet)
            enemy_shoot_sound.play()

    def update(self):
        self.rect.y += self.speedy
        if self.rect.y == 180:
            self.speedy = 0
        self.rect.x += self.speedx
        if self.rect.left < 0 or self.rect.right > WIDTH :
            self.speedx = -self.speedx
        if running == True:
            self.shoot()


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()


class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = enemy_bullet_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = 4

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT:
            self.kill()


class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosion_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explosion_anim[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = explosion_anim[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center


class Pow(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(['shield', 'gun'])
        self.image = powerup_images[self.type]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 2

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT:
            self.kill()


background = pygame.image.load(path.join(img_dir, 'antonin-landart-space-background.jpg')).convert()
background_rect = background.get_rect()
player_img = pygame.image.load(path.join(img_dir, 'playerShip1_orange.png')).convert()
boss_img = pygame.image.load(path.join(img_dir, 'ufoBlue.png')).convert()
lives_img = pygame.image.load(path.join(img_dir, 'playerLife1_orange.png')).convert()
lives_img = pygame.transform.scale(lives_img, (25, 25))
lives_img.set_colorkey(BLACK)
bullet_img = pygame.image.load(path.join(img_dir, 'laserRed16.png')).convert()
enemy_bullet_img = pygame.image.load(path.join(img_dir, 'laserBlue07.png')).convert()
enemy_images = []
enemy_list = ['enemyBlue1.png', 'enemyBlue4.png', 'enemyBlue5.png']
for img in enemy_list:
    img = pygame.image.load(path.join(img_dir, img)).convert()
    img = pygame.transform.scale(img, (40, 40))
    enemy_images.append(img)
meteor_images = []
meteor_list = ['meteorBrown_big1.png', 'meteorBrown_med1.png', 'meteorBrown_med3.png', 'meteorBrown_small1.png',
               'meteorBrown_small2.png', 'meteorBrown_tiny1.png']
for img in meteor_list:
    meteor_images.append(pygame.image.load(path.join(img_dir, img)).convert())

explosion_anim = {}
explosion_anim['lg'] = []
explosion_anim['sm'] = []
explosion_anim['player'] = []
for i in range(9):
    filename = 'regularExplosion0{}.png'.format(i)
    img = pygame.image.load(path.join(img_dir, filename)).convert()
    img.set_colorkey(BLACK)
    img_lg = pygame.transform.scale(img, (75, 75))
    explosion_anim['lg'].append(img_lg)
    img_sm = pygame.transform.scale(img, (32, 32))
    explosion_anim['sm'].append(img_sm)
    filename = 'sonicExplosion0{}.png'.format(i)
    img = pygame.image.load(path.join(img_dir, filename)).convert()
    img.set_colorkey(BLACK)
    explosion_anim['player'].append(img)

powerup_images = {}
powerup_images['shield'] = pygame.image.load(path.join(img_dir, 'shield_silver.png')).convert()
powerup_images['gun'] = pygame.image.load(path.join(img_dir, 'bold_silver.png')).convert()
powerup_gun_mini = pygame.transform.scale(powerup_images['gun'], (15, 25))
powerup_gun_mini.set_colorkey(BLACK)

shoot_sound = pygame.mixer.Sound(path.join(snd_dir, 'pew.wav'))
enemy_shoot_sound = pygame.mixer.Sound(path.join(snd_dir, 'Laser_Shoot15.wav'))
enemy_shoot_sound.set_volume(0.3)
expl_sounds = []
for snd in ['expl3.wav', 'expl6.wav']:
    expl_sounds.append(pygame.mixer.Sound(path.join(snd_dir, snd)))
pygame.mixer.music.load(path.join(snd_dir, 'level3.ogg'))
pygame.mixer.music.set_volume(0.7)

shield_sound = pygame.mixer.Sound(path.join(snd_dir, 'shield.wav'))
power_sound = pygame.mixer.Sound(path.join(snd_dir, 'power.wav'))


pygame.mixer.music.play(loops=-1)

game_over = True
running = True
level_cnt = 1
score = 0

while running:
    if game_over and level_cnt == 1:
        show_go_screen()
        game_over = False
        all_sprites = pygame.sprite.Group()
        mobs = pygame.sprite.Group()
        enemy = pygame.sprite.Group()
        enemy_bullets = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        powerups = pygame.sprite.Group()
        boss = Boss()
        player = Player()
        all_sprites.add(player)
        score = 0
        for i in range(8):
            newmob()

    if score >= 2000 and level_cnt == 1:
        clear_field()
        level_cnt += 1
        game_over = True
    elif score >= 3000 and level_cnt == 2:
        clear_field()
        level_cnt += 1
        game_over = True

    if game_over and level_cnt == 2:
        level_2_screen()
        game_over = False
        all_sprites = pygame.sprite.Group()
        player = Player()
        all_sprites.add(player)
        for i in range(4):
            newmob()
        for i in range(3):
            newenemy()
        score = 0

    if game_over and level_cnt == 3:
        level_3_screen()
        game_over = False
        all_sprites = pygame.sprite.Group()
        player = Player()
        all_sprites.add(player)
        boss = Boss()
        all_sprites.add(boss)
        for i in range(3):
            newmob()
        for i in range(3):
            newenemy()
        score = 0


    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.shoot()

    all_sprites.update()

    hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
    for hit in hits:
        score += 50 - hit.radius
        random.choice(expl_sounds).play()
        expl = Explosion(hit.rect.center, 'lg')
        all_sprites.add(expl)
        if random.random() > 0.6:
            pow = Pow(hit.rect.center)
            all_sprites.add(pow)
            powerups.add(pow)
        newmob()

    hits = pygame.sprite.groupcollide(enemy, bullets, True, True)
    for hit in hits:
        score += 100
        random.choice(expl_sounds).play()
        expl = Explosion(hit.rect.center, 'lg')
        all_sprites.add(expl)
        if random.random() > 0.7:
            pow = Pow(hit.rect.center)
            all_sprites.add(pow)
            powerups.add(pow)
        newenemy()

    hits = pygame.sprite.spritecollide(player, enemy_bullets, True, pygame.sprite.collide_rect)
    for hit in hits:
        player.shield -= 70
        expl = Explosion(hit.rect.center, 'sm')
        all_sprites.add(expl)
        if player.shield <= 0:
            death_explosion = Explosion(player.rect.center, 'player')
            all_sprites.add(death_explosion)
            player.hide()
            player.lives -= 1
            player.shield = 100

    hits = pygame.sprite.spritecollide(player, mobs, True, pygame.sprite.collide_circle)
    for hit in hits:
        player.shield -= hit.radius * 2
        expl = Explosion(hit.rect.center, 'sm')
        all_sprites.add(expl)
        newmob()
        if player.shield <= 0:
            death_explosion = Explosion(player.rect.center, 'player')
            all_sprites.add(death_explosion)
            player.hide()
            player.lives -= 1
            player.shield = 100

    if level_cnt == 3:
        hits = pygame.sprite.spritecollide(boss, bullets, True, pygame.sprite.collide_circle)
        for hit in hits:
            boss.shield -= 1
            expl = Explosion(hit.rect.center, 'sm')
            all_sprites.add(expl)
            if boss.shield <= 0:
                death_explosion = Explosion(player.rect.center, 'player')
                all_sprites.add(death_explosion)
                end_screen()

    if player.lives == 0 and not death_explosion.alive():
        game_over = True
        level_cnt = 1

    hits = pygame.sprite.spritecollide(player, powerups, True)
    for hit in hits:
        if hit.type == 'shield':
            player.shield += random.randrange(10, 30)
            if player.shield >= 100:
                player.shield = 100
            shield_sound.play()
        if hit.type == 'gun':
            player.powerup()
            power_sound.play()

    screen.fill(BLACK)
    screen.blit(background, background_rect)
    all_sprites.draw(screen)
    draw_text(screen, str(score), 18, WIDTH / 2, 10)
    draw_shield_bar(screen, 5, 5, player.shield)
    draw_lives(screen, WIDTH - 100, 5, player.lives, lives_img)
    draw_powerup(screen, WIDTH - 95, 35, player.power, powerup_gun_mini)
    draw_boss_shield_bar(screen, 5, 20, boss.shield)

    pygame.display.flip()


pygame.quit()
