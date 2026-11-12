from pathlib import Path
from collections import Counter

import pygame


STAT_NAMES = (("strength", "힘"), ("agility", "민첩"), ("magic", "마력"), ("vitality", "체력"))


class Player:
    # 힘, 민첩, 마력, 체력 순서. 전직 전에는 기존 체력과 마나로 시작한다.
    base_stats = (0, 0, 10, 7)
    max_shield = 0

    def __init__(self, x, y):
        self.strength, self.agility, self.magic, self.vitality = self.base_stats
        self.level = 1
        self.cleared_floor = 0
        self.stat_points = 0
        self.gold = 100
        self.inventory = Counter()
        self.health = self.max_health
        self.shield = self.max_shield
        self.mana = float(self.max_mana)
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
        self.weapon = None
        self.facing = pygame.Vector2(1, 0)
        self.hand_side = 1

    @property
    def max_health(self):
        return self.vitality

    @property
    def max_mana(self):
        return self.magic

    def clear_floor(self, floor):
        if floor != self.cleared_floor + 1:
            return False
        self.cleared_floor = floor
        self.level += 1
        self.stat_points += 20
        return True

    def spend_point(self, stat):
        if self.stat_points < 1 or stat not in dict(STAT_NAMES):
            return False
        setattr(self, stat, getattr(self, stat) + 1)
        self.stat_points -= 1
        if stat == "magic":
            self.mana += 1
        elif stat == "vitality":
            self.health += 1
        return True

    @property
    def hand_position(self):
        return self.hand_position_on(self.hand_side)

    def hand_position_on(self, side):
        # 현재 64px 캐릭터 그림에서 양손의 중심
        return pygame.Vector2(self.rect.centerx + (19 if side > 0 else -16),
                              self.rect.centery + 15)

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
        if dx or dy:
            self.facing = pygame.Vector2(dx, dy).normalize()
        if dx:
            self.hand_side = 1 if dx > 0 else -1

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
