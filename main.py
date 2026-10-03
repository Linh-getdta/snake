import pygame
from game import Snake_Game
from database import creat_player_table, creat_result_table, save_game

pygame.init()
creat_player_table()
creat_result_table()


WIDTH = 800
HEIGHT = 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")

clock = pygame.time.Clock()

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
GRAY = (150, 150, 150)

title_font = pygame.font.SysFont("comicsansms", 50)
font = pygame.font.SysFont("comicsansms", 30)

player_name = ""
entering_name = True

input_box = pygame.Rect(
    250,
    300,
    300,
    50
)

while entering_name:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_RETURN:

                if player_name.strip():
                    entering_name = False

            elif event.key == pygame.K_BACKSPACE:

                player_name = player_name[:-1]

            else:

                if len(player_name) < 20:
                    if event.unicode.isprintable():
                        player_name += event.unicode

    screen.fill(BLACK)

    title = title_font.render(
        "SNAKE_GAME",
        True,
        GREEN
    )

    screen.blit(
        title,
        (
            WIDTH // 2 - title.get_width() // 2,
            150
        )
    )

    label = font.render(
        "Nhap ten nguoi choi:",
        True,
        WHITE
    )

    screen.blit(
        label,
        (
            WIDTH // 2 - label.get_width() // 2,
            240
        )
    )

    # Khung nhập tên
    pygame.draw.rect(
        screen,
        WHITE,
        input_box,
        2
    )

    # Tên người chơi
    text_surface = font.render(
        player_name,
        True,
        WHITE
    )

    screen.blit(
        text_surface,
        (
            input_box.x + 10,
            input_box.y + 8
        )
    )

    # Con trỏ
    cursor_x = input_box.x + 10 + text_surface.get_width()

    pygame.draw.line(
        screen,
        GREEN,
        (cursor_x, input_box.y + 8),
        (cursor_x, input_box.y + 42),
        2
    )

    hint = font.render(
        "Nhan ENTER de bat dau",
        True,
        GRAY
    )

    screen.blit(
        hint,
        (
            WIDTH // 2 - hint.get_width() // 2,
            400
        )
    )

    pygame.display.update()

    clock.tick(30)


# =========================
# BẮT ĐẦU GAME
# =========================

game = Snake_Game(
    screen,
    player_name
)

score = game.run()
save_game(player_name, score)


# =========================
# GAME OVER
# =========================

screen.fill(BLACK)

game_over = title_font.render(
    "GAME OVER",
    True,
    (255, 0, 0)
)

screen.blit(
    game_over,
    (
        WIDTH // 2 - game_over.get_width() // 2,
        200
    )
)

result = font.render(
    f"{player_name} - Score: {score}",
    True,
    WHITE
)

screen.blit(
    result,
    (
        WIDTH // 2 - result.get_width() // 2,
        300
    )
)

pygame.display.update()

pygame.time.wait(3000)

pygame.quit()