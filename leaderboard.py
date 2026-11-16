import pygame


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 215, 0)
GRAY = (150, 150, 150)


def draw_leaderboard(
    screen,
    leaderboard,
    player_name,
    player_score,
    title_font,
    font,
):
    screen.fill(BLACK)

    title = title_font.render("GAME OVER", True, (255, 0, 0))
    screen.blit(title, (screen.get_width() // 2 - title.get_width() // 2, 20))

    result = font.render(
        f"{player_name} - Score: {player_score}",
        True,
        WHITE,
    )
    screen.blit(result, (screen.get_width() // 2 - result.get_width() // 2, 85))

    heading = font.render("LEADERBOARD - TOP 10", True, GREEN)
    screen.blit(heading, (screen.get_width() // 2 - heading.get_width() // 2, 145))

    if not leaderboard:
        empty_text = font.render("Chua co ket qua nao.", True, WHITE)
        screen.blit(
            empty_text,
            (screen.get_width() // 2 - empty_text.get_width() // 2, 220),
        )
    else:
        row_font = pygame.font.SysFont("comicsansms", 24)
        for rank, (name, score) in enumerate(leaderboard, start=1):
            color = (
                YELLOW
                if name == player_name and score == player_score
                else WHITE
            )
            row = row_font.render(f"{rank:>2}. {name}  -  {score}", True, color)
            screen.blit(
                row,
                (
                    screen.get_width() // 2 - row.get_width() // 2,
                    195 + (rank - 1) * 30,
                ),
            )

    hint = font.render("Nhan phim bat ky de thoat", True, GRAY)
    screen.blit(
        hint,
        (screen.get_width() // 2 - hint.get_width() // 2, screen.get_height() - 55),
    )
    pygame.display.update()
