from pathlib import Path

import pygame
import pytmx
from pytmx.util_pygame import load_pygame


class TownMap:
    def __init__(self, map_name="tutorial.tmx"):
        map_path = (
            Path(__file__).resolve().parent
            / "assets"
            / "maps"
            / map_name
        )

        self.map_data = load_pygame(str(map_path))

        # Collision 오브젝트 레이어 가져오기
        collision_layer = self.map_data.get_layer_by_name("Collision")

        if not isinstance(collision_layer, pytmx.TiledObjectGroup):
            raise ValueError(
                "Collision 레이어는 Object Layer여야 합니다."
            )

        # Tiled의 사각형을 Pygame 충돌 영역으로 변환
        self.walls = []

        for obj in collision_layer:
            if obj.width > 0 and obj.height > 0:
                wall = pygame.Rect(
                    round(obj.x),
                    round(obj.y),
                    max(1, round(obj.width)),
                    max(1, round(obj.height)),
                )
                self.walls.append(wall)

        print("읽은 맵:", map_path)
        print("충돌 사각형 수:", len(self.walls))

        # 맵 배경 생성
        self.width = self.map_data.width * self.map_data.tilewidth
        self.height = self.map_data.height * self.map_data.tileheight

        self.background = pygame.Surface(
            (self.width, self.height)
        ).convert()
        self.background.fill((30, 30, 30))

        for layer in self.map_data.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, image in layer.tiles():
                    self.background.blit(
                        image,
                        (
                            x * self.map_data.tilewidth,
                            y * self.map_data.tileheight,
                        ),
                    )

    def draw(self, screen, offset=(0, 0)):
        screen.blit(self.background, offset)