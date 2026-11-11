from pathlib import Path

import pygame


class Player:
    def __init__(self, x, y):
        image_path = (
            Path(__file__).resolve().parent
            / "assets"
            / "player"
            / "player.png"
        )

        original_image = pygame.image.load(str(image_path)).convert_alpha()

        height = 64
        width = max(
            1,
            round(original_image.get_width() * height / original_image.get_height()),
        )

        self.image = pygame.transform.scale(
            original_image,
            (width, height),
        )

        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 4

    def update(self, keys, screen_rect, walls):
        dx = 0
        dy = 0

        if keys[pygame.K_LEFT]:
            dx -= self.speed
        if keys[pygame.K_RIGHT]:
            dx += self.speed
        if keys[pygame.K_UP]:
            dy -= self.speed
        if keys[pygame.K_DOWN]:
            dy += self.speed

        # 가로 이동 후 벽 충돌 처리
        self.rect.x += dx

        for wall in walls:
            if self.rect.colliderect(wall):
                if dx > 0:
                    self.rect.right = wall.left
                elif dx < 0:
                    self.rect.left = wall.right

        # 세로 이동 후 벽 충돌 처리
        self.rect.y += dy

        for wall in walls:
            if self.rect.colliderect(wall):
                if dy > 0:
                    self.rect.bottom = wall.top
                elif dy < 0:
                    self.rect.top = wall.bottom

        self.rect.clamp_ip(screen_rect)

    def draw(self, screen, offset=(0, 0)):
        screen.blit(self.image, self.rect.move(offset))