from pathlib import Path

import pygame
import pytmx


class Portal:
    def __init__(self, game_map):
        self.rect = None

        for layer in game_map.map_data.layers:
            if (
                isinstance(layer, pytmx.TiledObjectGroup)
                and layer.name == "Interactions"
            ):
                for obj in layer:
                    if (
                        obj.name == "portal_to_town"
                        and obj.width > 0
                        and obj.height > 0
                    ):
                        self.rect = pygame.Rect(
                            round(obj.x + layer.offsetx),
                            round(obj.y + layer.offsety),
                            max(1, round(obj.width)),
                            max(1, round(obj.height)),
                        )
                        break

        if self.rect is None:
            raise ValueError(
                "tutorial.tmx의 Interactions에 "
                "portal_to_town 사각형이 필요합니다."
            )

        # 나중에 사용할 포탈 이미지
        self.image = None

        image_path = (
            Path(__file__).resolve().parent
            / "assets"
            / "portal"
            / "portal.png"
        )

        if image_path.is_file():
            original = pygame.image.load(
                str(image_path)
            ).convert_alpha()

            self.image = pygame.transform.scale(
                original,
                self.rect.size,
            )

    def is_near(self, player_rect):
        # 범위를 늘리지 않고 실제로 겹치는지 확인
        return player_rect.colliderect(self.rect)

    def draw(self, screen, offset):
        draw_rect = self.rect.move(offset)

        if self.image is not None:
            screen.blit(self.image, draw_rect)
        else:
            # 이미지가 준비되기 전까지 사용할 임시 표시
            pygame.draw.ellipse(
                screen,
                (180, 100, 255),
                draw_rect,
                width=4,
            )


def place_player(player, game_map):
    bounds = pygame.Rect(
        0, 0, game_map.width, game_map.height
    )
    candidate = player.rect.copy()
    candidate.center = bounds.center

    if (
        bounds.contains(candidate)
        and candidate.collidelist(game_map.walls) == -1
    ):
        player.rect.center = candidate.center
        return

    # 중앙이 막혀 있으면 빈 위치 찾기
    step_x = game_map.map_data.tilewidth
    step_y = game_map.map_data.tileheight

    for y in range(step_y // 2, game_map.height, step_y):
        for x in range(step_x // 2, game_map.width, step_x):
            candidate.center = (x, y)

            if (
                bounds.contains(candidate)
                and candidate.collidelist(game_map.walls) == -1
            ):
                player.rect.center = candidate.center
                return

    raise ValueError(
        "맵에 캐릭터를 배치할 수 있는 빈 공간이 없습니다."
    )