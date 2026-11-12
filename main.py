import pygame

from player import Player, STAT_NAMES
from tutorial_weapons import WeaponAttack, training_stands
from town_map import TownMap
from ui import GameUI
from portal import Portal, place_player
from village import Shop, TowerEntrance, Village


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
        stands = []
        held = None
        confirming_job = False
        stats_open = False
        inventory_open = False
        attack = None

        player = None
        town_map = None
        portal = None
        village_map = None
        village = None
        shop = None
        running = True

        while running:
            dt = min(clock.tick(60) / 1000, 0.05)

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
                    if inventory_open:
                        if event.key in (pygame.K_i, pygame.K_ESCAPE):
                            inventory_open = False
                        continue
                    if stats_open:
                        if event.key in (pygame.K_TAB, pygame.K_ESCAPE):
                            stats_open = False
                        elif pygame.K_1 <= event.key <= pygame.K_4:
                            stat, _ = STAT_NAMES[event.key - pygame.K_1]
                            player.spend_point(stat)
                        continue

                    if (event.key == pygame.K_i and scene in ("tutorial", "village", "tower")
                            and not confirming_job):
                        inventory_open = True
                        continue

                    if (event.key == pygame.K_TAB and scene in ("tutorial", "village", "tower")
                            and hasattr(player, "job") and not confirming_job):
                        stats_open = True
                        continue
                    if scene == "shop":
                        if shop.handle_key(event.key):
                            scene = "village"
                        continue

                    if scene == "village" and event.key == pygame.K_f:
                        place = village.nearby(player)
                        if place == "shop":
                            if shop is None:
                                shop = Shop(ui, player)
                            scene = "shop"
                            attack = None
                        elif place == "tower":
                            town_map = TowerEntrance(ui)
                            player.rect.center = town_map.exit.center
                            scene = "tower"
                            attack = None
                        continue

                    if scene == "tower" and event.key == pygame.K_f and town_map.exit.colliderect(player.rect):
                        town_map = village_map
                        player.rect.midtop = village.places["tower"].midbottom
                        scene = "village"
                        attack = None
                        continue
                    if confirming_job:
                        if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                            facing = player.facing.copy()
                            hand_side = player.hand_side
                            player = held.player_class(*player.rect.center)
                            player.weapon = held.weapon
                            player.facing = facing
                            player.hand_side = hand_side
                            portal = Portal(town_map)
                            confirming_job = False
                        elif event.key == pygame.K_ESCAPE:
                            confirming_job = False
                        continue

                    if event.key == pygame.K_ESCAPE:
                        exit_requested = True
                        continue

                    if event.key == pygame.K_f and scene == "tutorial" and portal is None:
                        nearby = next((stand for stand in stands if stand.is_near(player)), None)
                        if nearby is not None and nearby is not held:
                            held = nearby
                            player.weapon = held.weapon
                            attack = None
                        continue

                    if event.key == pygame.K_e and scene == "tutorial" and portal is None and held:
                        confirming_job = True
                        attack = None
                        continue

                    if player and event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                        player.hand_side = 1 if event.key == pygame.K_RIGHT else -1

                    if event.key == pygame.K_SPACE and held and attack is None:
                        attack = WeaponAttack(player, held.projectile_icon)
                        continue

                    # 전직 후 열린 포탈에서 마을로 이동
                    if (
                        event.key == pygame.K_f
                        and scene == "tutorial"
                        and portal is not None
                        and portal.is_near(player.rect)
                    ):
                        new_map = TownMap("village.tmx")
                        village = Village(new_map, ui)
                        village_map = new_map

                        # 기존 캐릭터를 새 맵에 배치
                        place_player(player, new_map)

                        town_map = new_map
                        attack = None
                        portal = None
                        scene = "village"

                        print("마을로 이동했습니다.")
                        continue

                # 게임 시작
                if scene == "start" and ui.start_clicked(event):
                    town_map = TownMap("tutorial.tmx")
                    stands = training_stands(town_map)

                    player = Player(
                        town_map.width // 2,
                        town_map.height // 2,
                    )
                    place_player(player, town_map)

                    scene = "tutorial"

            if not running:
                break

            # 훈련장과 마을에서 이동
            if (
                scene in ("tutorial", "village", "tower")
                and not exit_requested
                and not confirming_job
                and not stats_open
                and not inventory_open
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
                if attack and not attack.advance(dt, bounds, town_map.walls):
                    attack = None

            # 화면 그리기
            if scene == "start":
                ui.draw_start(screen)
            elif scene == "shop":
                shop.draw(screen)

            else:
                screen.fill((30, 30, 30))

                offset = (
                    (screen.get_width() - town_map.width) // 2,
                    (screen.get_height() - town_map.height) // 2,
                )
                if scene == "village":
                    offset = tuple(
                        max(view - extent, min(0, view // 2 - pos)) if extent > view else centered
                        for view, extent, pos, centered in zip(screen.get_size(), (town_map.width, town_map.height),
                                                               player.rect.center, offset)
                    )

                town_map.draw(screen, offset)
                if scene == "tutorial":
                    for stand in stands:
                        stand.draw(screen, offset, stand is held)

                if portal is not None:
                    portal.draw(screen, offset)

                player.draw(screen, offset)
                if held is not None:
                    if not attack or held.weapon != "검":
                        held.draw_held(screen, offset, player)
                    if attack:
                        attack.draw(screen, offset, player, held.held_icon(attack.hand_side))

                # 현재 맵 이름 표시
                map_title = {"tutorial": "훈련장", "village": "마을", "tower": "타워 입구"}[scene]

                ui.draw_text(
                    screen,
                    map_title,
                    ui.map_title_font,
                    (255, 255, 255),
                    (screen.get_width() // 2, 25),
                )

                ui.draw_status(screen, player)
                if hasattr(player, "job"):
                    info = ui.hint_font.render(f"Lv. {player.level}   Tab: 능력치   I: 가방", True, "#fff8dd", "#302c35")
                    screen.blit(info,(ui.status_rect.left, ui.status_rect.bottom + 3))
                if confirming_job:
                    ui.draw_job_prompt(screen, held.job)
                elif scene in ("village", "tower"):
                    hint = None
                    if scene == "tower" and town_map.exit.colliderect(player.rect):
                        hint = "F: 마을로 돌아가기"
                    elif scene == "village":
                        hint = {"shop": "F: 상점 열기", "tower": "F: 타워 입장"}.get(village.nearby(player))
                    if hint:
                        ui.draw_text(screen, hint, ui.hint_font, (255,255,255),
                                     (screen.get_width() // 2, screen.get_height() - 40))
                elif scene == "tutorial" and portal is None:
                    nearby = next((stand for stand in stands if stand.is_near(player)), None)
                    hint = "Space: 무기 사용    E: 전직" if held else "단상에 다가가 무기를 집으세요"
                    if nearby and nearby is not held:
                        hint = f"F: {nearby.weapon} 집기    {hint}" if held else f"F: {nearby.weapon} 집기"
                    ui.draw_text(screen, hint, ui.hint_font, (255, 255, 255),
                                 (screen.get_width() // 2, screen.get_height() - 40))

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

            if stats_open:
                ui.draw_stats(screen, player)
            if inventory_open:
                ui.draw_inventory(screen, player)
            if exit_requested:
                ui.draw_exit_dialog(screen)

            pygame.display.flip()

    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
