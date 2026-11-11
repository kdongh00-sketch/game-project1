import pygame

from jobs.warrior import Warrior
from town_map import TownMap
from ui import GameUI
from portal import Portal, place_player


def main():
    pygame.init()

    try:
        screen = pygame.display.set_mode(
            (0, 0),
            pygame.FULLSCREEN,
        )
        pygame.display.set_caption("game-project1")

        clock = pygame.time.Clock()
        ui = GameUI(screen.get_rect())

        scene = "start"
        exit_requested = False
        tutorial_completed = False

        player = None
        town_map = None
        portal = None
        running = True

        while running:
            clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit_requested = True
                    continue

                # 종료 확인창 입력
                if exit_requested:
                    if event.type == pygame.KEYDOWN:
                        if event.key in (
                            pygame.K_RETURN,
                            pygame.K_KP_ENTER,
                        ):
                            running = False
                            break

                        elif event.key == pygame.K_ESCAPE:
                            exit_requested = False

                    continue

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        exit_requested = True
                        continue

                    # 훈련장 포탈에서 F를 누르면 마을로 이동
                    if (
                        event.key == pygame.K_f
                        and scene == "tutorial"
                        and not tutorial_completed
                        and portal.is_near(player.rect)
                    ):
                        new_map = TownMap("village.tmx")

                        # 기존 캐릭터를 새 맵에 배치
                        place_player(player, new_map)

                        town_map = new_map
                        portal = None
                        tutorial_completed = True
                        scene = "village"

                        print("마을로 이동했습니다.")
                        continue

                # 게임 시작
                if scene == "start" and ui.start_clicked(event):
                    town_map = TownMap("tutorial.tmx")
                    portal = Portal(town_map)

                    player = Warrior(
                        town_map.width // 2,
                        town_map.height // 2,
                    )
                    place_player(player, town_map)

                    scene = "tutorial"

            if not running:
                break

            # 훈련장과 마을에서 이동
            if (
                scene in ("tutorial", "village")
                and not exit_requested
            ):
                keys = pygame.key.get_pressed()

                bounds = pygame.Rect(
                    0,
                    0,
                    town_map.width,
                    town_map.height,
                )

                player.update(
                    keys,
                    bounds,
                    town_map.walls,
                )

            # 화면 그리기
            if scene == "start":
                ui.draw_start(screen)

            else:
                screen.fill((30, 30, 30))

                offset = (
                    (screen.get_width() - town_map.width) // 2,
                    (screen.get_height() - town_map.height) // 2,
                )

                town_map.draw(screen, offset)

                if portal is not None:
                    portal.draw(screen, offset)

                player.draw(screen, offset)

                # 현재 맵 이름 표시
                map_title = (
                    "훈련장" if scene == "tutorial" else "마을"
                )

                ui.draw_text(
                    screen,
                    map_title,
                    ui.map_title_font,
                    (255, 255, 255),
                    (screen.get_width() // 2, 25),
                )

                # 포탈 근처에서 안내 표시
                if (
                    portal is not None
                    and portal.is_near(player.rect)
                ):
                    ui.draw_text(
                        screen,
                        "F: 마을로 이동",
                        ui.hint_font,
                        (255, 255, 255),
                        (
                            screen.get_width() // 2,
                            screen.get_height() - 40,
                        ),
                    )

            if exit_requested:
                ui.draw_exit_dialog(screen)

            pygame.display.flip()

    finally:
        pygame.quit()


if __name__ == "__main__":
    main()