import pygame
import random


class Snake_Game:

    def __init__(self, screen, player_name):
        self.screen = screen
        self.player_name = player_name

        self.WIDTH = 800
        self.HEIGHT = 600
        self.CELL_SIZE = 20

        self.black = (0, 0, 0)
        self.white = (255, 255, 255)
        self.green = (0, 255, 0)
        self.red = (255, 0, 0)

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("comicsansms", 35)

        self.snake = [
            [200, 200],
            [180, 200],
            [160, 200]
        ]

        self.direction = "RIGHT"

        self.x_food = random.randrange(
            0,
            self.WIDTH,
            self.CELL_SIZE
        )

        self.y_food = random.randrange(
            0,
            self.HEIGHT,
            self.CELL_SIZE
        )

        self.score = 0
        self.running = True

    def handle_event(self, event):

        if event.type == pygame.QUIT:
            self.running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_UP:
                if self.direction != "DOWN":
                    self.direction = "UP"

            elif event.key == pygame.K_DOWN:
                if self.direction != "UP":
                    self.direction = "DOWN"

            elif event.key == pygame.K_LEFT:
                if self.direction != "RIGHT":
                    self.direction = "LEFT"

            elif event.key == pygame.K_RIGHT:
                if self.direction != "LEFT":
                    self.direction = "RIGHT"

    def move(self):

        head_x = self.snake[0][0]
        head_y = self.snake[0][1]

        if self.direction == "UP":
            head_y -= self.CELL_SIZE

        elif self.direction == "DOWN":
            head_y += self.CELL_SIZE

        elif self.direction == "LEFT":
            head_x -= self.CELL_SIZE

        elif self.direction == "RIGHT":
            head_x += self.CELL_SIZE

        new_head = [head_x, head_y]

        self.snake.insert(0, new_head)

        if head_x == self.x_food and head_y == self.y_food:

            self.score += 10

            self.x_food = random.randrange(
                0,
                self.WIDTH,
                self.CELL_SIZE
            )

            self.y_food = random.randrange(
                0,
                self.HEIGHT,
                self.CELL_SIZE
            )

        else:
            self.snake.pop()

    def check_collision(self):

        head_x = self.snake[0][0]
        head_y = self.snake[0][1]

        if head_x < 0:
            return True

        if head_x >= self.WIDTH:
            return True

        if head_y < 0:
            return True

        if head_y >= self.HEIGHT:
            return True

        if self.snake[0] in self.snake[1:]:
            return True

        return False

    def draw(self):

        self.screen.fill(self.black)

        pygame.draw.rect(
            self.screen,
            self.red,
            (
                self.x_food,
                self.y_food,
                self.CELL_SIZE,
                self.CELL_SIZE
            )
        )

        for part in self.snake:

            pygame.draw.rect(
                self.screen,
                self.green,
                (
                    part[0],
                    part[1],
                    self.CELL_SIZE,
                    self.CELL_SIZE
                )
            )

        player_text = self.font.render(
            f"Player: {self.player_name}",
            True,
            self.white
        )

        self.screen.blit(
            player_text,
            (10, 10)
        )

        score_text = self.font.render(
            f"Score: {self.score}",
            True,
            self.white
        )

        self.screen.blit(
            score_text,
            (10, 45)
        )

        pygame.display.update()

    def run(self):

        while self.running:

            for event in pygame.event.get():
                self.handle_event(event)

            self.move()

            if self.check_collision():
                self.running = False
                break

            self.draw()

            self.clock.tick(10)

        return self.score