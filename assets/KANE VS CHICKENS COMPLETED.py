import pygame
import random
import sys
from math import sin, cos, pi

# 1. Setup & Audio Initialization
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("KANE... vs CHICKENS")
clock = pygame.time.Clock()

# --- AUDIO LOAD ---
try:
    pygame.mixer.music.load("music.mp3")
    pygame.mixer.music.set_volume(0.4)
    # This loads the sound into memory for instant firing
    laser_sound = pygame.mixer.Sound("laser.wav")
    laser_sound.set_volume(0.4) 
except:
    laser_sound = None

# 2. Asset Loading
def load_sprite(path, size, use_mask=True):
    try:
        img = pygame.image.load(path).convert_alpha()
        img = pygame.transform.scale(img, size)
        if use_mask:
            mask = pygame.mask.from_surface(img)
            return img, mask
        return img
    except:
        return None

K_W, K_H = 120, 120
C_W, C_H = 150, 150

menu_bg = load_sprite("kane_vs_chickens.png", (800, 600), use_mask=False)
game_bg = load_sprite("orange_desert.png", (800, 600), use_mask=False)

k_stuff = load_sprite("kane.png", (K_W, K_H), use_mask=True)
kane_img, kane_mask = k_stuff if k_stuff else (None, None)

chicken_data = []
for i in range(1, 4):
    c_stuff = load_sprite(f"chicken{i}.png", (C_W, C_H), use_mask=True)
    if c_stuff: chicken_data.append(c_stuff)

# 3. Classes
class Particle:
    def __init__(self, x, y):
        self.x, self.y = float(x), float(y)
        angle, speed = random.uniform(0, 2*pi), random.uniform(2, 6)
        self.vx, self.vy = cos(angle)*speed, sin(angle)*speed
        self.life = 25
    def update(self):
        self.vy += 0.1; self.x += self.vx; self.y += self.vy; self.life -= 1
    def draw(self, surf):
        pygame.draw.rect(surf, (255, 150, 0), (int(self.x), int(self.y), 4, 4))

class Enemy:
    def __init__(self, lvl):
        self.image, self.mask = random.choice(chicken_data)
        spawn_x = random.randint(0, WIDTH - C_W)
        self.rect = self.image.get_rect(midtop=(spawn_x + (C_W//2), -C_H))
        self.speed = 2.5 + (lvl * 0.3)

# 4. Game State
game_state = "MENU"
score, level = 0, 1
player_rect = pygame.Rect(WIDTH//2 - K_W//2, HEIGHT - K_H - 20, K_W, K_H)
bullets, enemies, particles = [], [], []

def start_game():
    global score, level, bullets, enemies, particles, game_state
    score, level = 0, 1
    bullets, enemies, particles = [], [], []
    player_rect.centerx = WIDTH//2
    game_state = "PLAYING"
    try: pygame.mixer.music.play(-1)
    except: pass

# 5. Main Loop
while True:
    clock.tick(60)
    m_pos = pygame.mouse.get_pos()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        
        if game_state == "MENU" and event.type == pygame.MOUSEBUTTONDOWN:
            if pygame.Rect(WIDTH//2-100, 430, 200, 55).collidepoint(event.pos): start_game()
            if pygame.Rect(WIDTH//2-100, 500, 200, 55).collidepoint(event.pos): pygame.quit(); sys.exit()
            
        elif game_state == "PLAYING" and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                bullets.append(pygame.Rect(player_rect.centerx-5, player_rect.top-10, 10, 25))
                # --- TRIGGER LASER SOUND ON FIRE ---
                if laser_sound:
                    laser_sound.stop() # Stops previous sound if spamming
                    laser_sound.play() 

        elif game_state == "GAMEOVER" and event.type == pygame.MOUSEBUTTONDOWN:
            if pygame.Rect(WIDTH//2-100, 450, 200, 55).collidepoint(event.pos): 
                game_state = "MENU"
                pygame.mixer.music.stop()

    if game_state == "PLAYING":
        # --- MOVEMENT (UNTOUCHED) ---
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and player_rect.left > 0:
            player_rect.x -= 8
        if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and player_rect.right < WIDTH:
            player_rect.x += 8

        level = (score // 100) + 1
        if random.randint(1, 40) == 1 and chicken_data: enemies.append(Enemy(level))
        
        for b in bullets[:]:
            b.y -= 12
            if b.bottom < 0: bullets.remove(b)

        for e in enemies[:]:
            e.rect.y += e.speed
            if kane_mask:
                offset_p = (player_rect.x - e.rect.x, player_rect.y - e.rect.y)
                if e.mask.overlap(kane_mask, offset_p):
                    game_state = "GAMEOVER"
                    pygame.mixer.music.fadeout(1000)
            for b in bullets[:]:
                b_mask = pygame.Mask((10, 25)); b_mask.fill()
                if e.mask.overlap(b_mask, (b.x - e.rect.x, b.y - e.rect.y)):
                    score += 10
                    for _ in range(15): particles.append(Particle(e.rect.centerx, e.rect.centery))
                    enemies.remove(e); bullets.remove(b); break
            if e.rect.top > HEIGHT: enemies.remove(e)

        for p in particles[:]:
            p.update()
            if p.life <= 0: particles.remove(p)

    # --- DRAWING ---
    if game_state == "MENU":
        if isinstance(menu_bg, pygame.Surface): screen.blit(menu_bg, (0,0))
        for i, txt in enumerate(["START", "QUIT"]):
            btn = pygame.Rect(WIDTH//2-100, 430 + (i*70), 200, 55)
            c = (255, 120, 0) if btn.collidepoint(m_pos) else (60, 30, 0)
            pygame.draw.rect(screen, c, btn, border_radius=12); pygame.draw.rect(screen, (255,255,255), btn, 2, border_radius=12)
            lbl = pygame.font.SysFont("Arial", 30, bold=True).render(txt, True, (255,255,255))
            screen.blit(lbl, lbl.get_rect(center=btn.center))
    else:
        if isinstance(game_bg, pygame.Surface): screen.blit(game_bg, (0,0))
        if isinstance(kane_img, pygame.Surface): screen.blit(kane_img, player_rect)
        for b in bullets: pygame.draw.rect(screen, (0, 255, 0), b)
        for e in enemies: screen.blit(e.image, e.rect) 
        for p in particles: p.draw(screen)
        
        s_txt = pygame.font.SysFont("Arial", 28, bold=True).render(f"Score: {score}", True, (255,255,255))
        l_txt = pygame.font.SysFont("Arial", 28, bold=True).render(f"Level: {level}", True, (0, 255, 0))
        screen.blit(s_txt, (20, 20)); screen.blit(l_txt, (WIDTH-140, 20))
        if game_state == "GAMEOVER":
            ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA); ov.fill((0,0,0,200)); screen.blit(ov, (0,0))
            t = pygame.font.SysFont("Arial", 80, bold=True).render("GAME OVER", True, (255,0,0))
            screen.blit(t, t.get_rect(center=(WIDTH//2, 280)))
            btn = pygame.Rect(WIDTH//2-100, 450, 200, 55)
            pygame.draw.rect(screen, (255, 120, 0), btn, border_radius=12)
            r_txt = pygame.font.SysFont("Arial", 32, bold=True).render("RETRY", True, (255,255,255))
            screen.blit(r_txt, r_txt.get_rect(center=btn.center))

    pygame.display.flip()
