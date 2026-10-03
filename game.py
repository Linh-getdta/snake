import pygame
import random

class Snake_Game:
    pygame.init()

WIDTH = 800
HEIGHT = 600
CELL_SIZE = 20

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")
clock = pygame.time.Clock()

black = (0, 0, 0)
white = (255, 255, 255)
green = (0, 255, 0)
red = (255, 0, 0)

snake = [
    [200, 200],
    [180, 200],
    [160, 200]
]


direction = "RIGHT"

x_food = random.randrange(1, (WIDTH // CELL_SIZE)) * CELL_SIZE
y_food = random.randrange(1, (HEIGHT // CELL_SIZE)) * CELL_SIZE

score = 0

font = pygame.font.SysFont("comicsansms", 35)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and direction != "DOWN":
                direction = "UP"
            if event.key == pygame.K_DOWN and direction != "UP":
                direction = "DOWN"
            if event.key == pygame.K_LEFT and direction != "RIGHT":
                direction = "LEFT"
            if event.key == pygame.K_RIGHT and direction != "LEFT":
                direction = "RIGHT"

    head_x = snake[0][0]
    head_y = snake[0][1]

    if direction == "UP":
        head_y -= CELL_SIZE
    elif direction == "DOWN":
        head_y += CELL_SIZE
    elif direction == "LEFT":
        head_x -= CELL_SIZE
    elif direction == "RIGHT":
        head_x += CELL_SIZE

    new_head = [head_x, head_y] 

    snake.insert(0, new_head)


    if head_x == x_food and head_y == y_food:
        score += 10

        x_food = random.randrange(0, WIDTH, CELL_SIZE)
        y_food = random.randrange(0, HEIGHT, CELL_SIZE)

    else:
        snake.pop()

    if new_head in snake[1:]:
        running = False

    screen.fill(black)

    pygame.draw.rect(screen, red,(x_food, y_food, CELL_SIZE, CELL_SIZE))

    for part in snake:
        pygame.draw.rect(screen, green,(part[0], part[1], CELL_SIZE, CELL_SIZE))

    score_text = font.render(
        f"score: {score}", True, white
    )
    screen.blit(score_text,(10, 10))
    pygame.display.update()
    clock.tick(10)




pygame.quit()