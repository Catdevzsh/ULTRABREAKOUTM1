import pygame
import sys
from array import array
import random

# Initialize Pygame and its mixer
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

# Screen setup
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("ULTRABREAKOUT 20XX")

# Colors
BLACK, WHITE, RED, GREEN, BLUE = (0, 0, 0), (255, 255, 255), (255, 0, 0), (0, 255, 0), (0, 0, 255)

# Game variables
paddle_width, paddle_height = 100, 20
ball_diameter = 20
ball_radius = ball_diameter // 2
brick_width, brick_height = 75, 30
num_bricks_per_row = SCREEN_WIDTH // (brick_width + 10)
num_rows_of_bricks = 5
score = 0

# Sound generation function
def generate_square_wave(frequency=440, volume=0.1, duration=0.1):
    sample_rate = pygame.mixer.get_init()[0]
    period = int(sample_rate / frequency)
    amplitude = 2 ** (abs(pygame.mixer.get_init()[1]) - 1) - 1
    waveform = array('h', [int(amplitude if time < period / 2 else -amplitude) for time in range(period)] * int(duration * frequency))
    sound = pygame.mixer.Sound(waveform)
    sound.set_volume(volume)
    return sound

# Predefined sounds
hit_paddle_sound = generate_square_wave(660, 0.1, 0.1)
break_brick_sound = generate_square_wave(440, 0.1, 0.1)
game_over_sound = generate_square_wave(220, 0.1, 0.5)

def show_game_over_screen():
    screen.fill(BLACK)
    font_large = pygame.font.SysFont("Arial", 72)
    font_small = pygame.font.SysFont("Arial", 36)
    wasted_text = font_large.render("WASTED", True, RED)
    try_again_text = font_small.render("Try again? (Y/N)", True, WHITE)
    screen.blit(wasted_text, (SCREEN_WIDTH // 2 - wasted_text.get_width() // 2, SCREEN_HEIGHT // 2 - wasted_text.get_height() // 2))
    screen.blit(try_again_text, (SCREEN_WIDTH // 2 - try_again_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
    pygame.display.flip()
    waiting_for_input = True
    while waiting_for_input:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    return True  # Restart game
                elif event.key == pygame.K_n:
                    return False  # Quit game

def start_screen():
    font_large = pygame.font.SysFont("Arial", 48)
    text_surf = font_large.render("ULTRABREAKOUT 20XX", True, WHITE)
    subtext_surf = font_large.render("Press Z or SPACE to start", True, WHITE)
    while True:
        screen.fill(BLACK)
        screen.blit(text_surf, (SCREEN_WIDTH / 2 - text_surf.get_width() / 2, SCREEN_HEIGHT / 3))
        screen.blit(subtext_surf, (SCREEN_WIDTH / 2 - subtext_surf.get_width() / 2, SCREEN_HEIGHT / 2))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_z, pygame.K_SPACE):
                    return  # Proceed to the main game

def main_game():
    global score
    score = 0
    paddle = pygame.Rect(SCREEN_WIDTH // 2 - paddle_width // 2, SCREEN_HEIGHT - paddle_height - 10, paddle_width, paddle_height)
    ball = pygame.Rect(SCREEN_WIDTH // 2 - ball_radius, SCREEN_HEIGHT // 2 - ball_radius, ball_diameter, ball_diameter)
    ball_speed = [5, -5]
    bricks = [{'rect': pygame.Rect(x * (brick_width + 10), y * (brick_height + 5) + 50, brick_width, brick_height), 'score': random.randint(10, 30)} for y in range(num_rows_of_bricks) for x in range(num_bricks_per_row)]
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and paddle.left > 0:
            paddle.move_ip(-10, 0)
        if keys[pygame.K_RIGHT] and paddle.right < SCREEN_WIDTH:
            paddle.move_ip(10, 0)
        ball.move_ip(ball_speed)
        if ball.left <= 0 or ball.right >= SCREEN_WIDTH:
            ball_speed[0] = -ball_speed[0]
        if ball.top <= 0:
            ball_speed[1] = -ball_speed[1]
        if ball.colliderect(paddle) or ball.collidelist([b['rect'] for b in bricks]) != -1:
            ball_speed[1] = -ball_speed[1]
            hit_paddle_sound.play()
        if ball.bottom > SCREEN_HEIGHT:
            game_over_sound.play()
            if not show_game_over_screen():
                return  # Quit game if N is pressed
            else:
                main_game()  # Restart game if Y is pressed
        brick_collision_index = ball.collidelist([b['rect'] for b in bricks])
        if brick_collision_index != -1:
            hit_brick = bricks.pop(brick_collision_index)
            score += hit_brick['score']
            break_brick_sound.play()
        screen.fill(BLACK)
        pygame.draw.rect(screen, WHITE, paddle)
        pygame.draw.circle(screen, RED, ball.center, ball_radius)
        for brick in bricks:
            pygame.draw.rect(screen, GREEN, brick['rect'])
        score_text = pygame.font.SysFont("Arial", 24).render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        pygame.display.flip()
        pygame.time.delay(30)

start_screen()
main_game()
