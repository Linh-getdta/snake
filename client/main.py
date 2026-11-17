import pygame

from client.game import Snake_Game
from client.online import prompt_online_settings, run_online_game
from backend.database import (
    creat_player_table,
    creat_result_table,
    get_leaderboard,
    save_game,
)
from client.leaderboard import draw_leaderboard

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
                    player_name = player_name.strip()
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


playing = True
while playing:
    choosing_mode = True
    while choosing_mode:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                playing = False
                choosing_mode = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    choosing_mode = False
                    selected_mode = "local"
                elif event.key == pygame.K_2:
                    choosing_mode = False
                    selected_mode = "online"
                elif event.key in (pygame.K_ESCAPE, pygame.K_q):
                    playing = False
                    choosing_mode = False

        if not playing:
            break
        screen.fill(BLACK)
        title = title_font.render("SNAKE_GAME", True, GREEN)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 150))
        for label, y in (("1 - Choi mot minh", 270), ("2 - Choi online", 330)):
            option = font.render(label, True, WHITE)
            screen.blit(option, (WIDTH // 2 - option.get_width() // 2, y))
        pygame.display.flip()
        clock.tick(30)

    if not playing:
        break

    if selected_mode == "online":
        settings = prompt_online_settings(screen)
        if settings is not None:
            server_url, room_code = settings
            run_online_game(screen, player_name, server_url, room_code)
        continue

    replay_local = True
    while playing and replay_local:
        game = Snake_Game(screen, player_name)
        score = game.run()
        save_game(player_name, score)

        leaderboard = get_leaderboard()
        draw_leaderboard(
            screen,
            leaderboard,
            player_name,
            score,
            title_font,
            font,
        )

        waiting_for_choice = True
        while waiting_for_choice:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    playing = False
                    waiting_for_choice = False
                    replay_local = False
                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_r, pygame.K_RETURN):
                        waiting_for_choice = False
                    elif event.key == pygame.K_m:
                        waiting_for_choice = False
                        replay_local = False
                    elif event.key in (pygame.K_ESCAPE, pygame.K_q):
                        playing = False
                        waiting_for_choice = False
                        replay_local = False

pygame.quit()
