from pathlib import Path

import pygame

from jobs.warrior import Warrior
from player import Player


class Mage(Player):
    job = "마법사"
    base_stats = (20, 20, 60, 20)
    max_shield = 4


class Archer(Player):
    job = "궁수"
    base_stats = (30, 40, 20, 30)
    max_shield = 4


ART_DIR = Path(__file__).resolve().parent / "assets" / "weapons"
SWORD_GRIP = (9, 6)  # 가로로 누운 56×12 검의 손잡이


def weapon_pose(icon, grip, hand, side, rotation, *, smooth=False):
    grip_x, grip_y = grip
    if side < 0:
        grip_x = icon.get_width() - 1 - grip_x
    grip_offset = pygame.Vector2(grip_x + 0.5, grip_y + 0.5) - icon.get_rect().center
    if smooth:
        # 확대할 때 원본 픽셀의 네모 모양을 보존하고, 회전 후 화면 픽셀의 면적만 평균낸다.
        large = pygame.transform.scale_by(icon.premul_alpha(), 4)
        turned = pygame.transform.rotate(large, rotation)
        size = tuple(round(n / 4) for n in turned.get_size())
        rotated = pygame.transform.smoothscale(turned, size)
    else:
        rotated = pygame.transform.rotate(icon, rotation)
    center = pygame.Vector2(hand) - grip_offset.rotate(-rotation)
    return rotated, rotated.get_rect(center=(round(center.x), round(center.y)))


def load_pixel_art(filename, size):
    path = ART_DIR / filename
    if path.is_file():
        source = pygame.image.load(str(path)).convert_alpha()
        frame = source.get_rect().fit(pygame.Rect((0, 0), size))
        return pygame.transform.scale(source, frame.size)
    return None

class WeaponStand:
    def __init__(self, x, y, weapon, job, player_class):
        self.rect = pygame.Rect(0, 0, 76, 32)
        self.rect.center = (x, y)
        self.pedestal = load_pixel_art("pedestal.png", self.rect.size)
        self.weapon = weapon
        self.job = job
        self.player_class = player_class
        icon_size = {"검": (56, 12), "지팡이": (44, 48), "활": (36, 39)}[weapon]
        self.icon = pygame.Surface(icon_size, pygame.SRCALPHA)
        filename = {"검": "sword.png", "지팡이": "staff.png", "활": "bow.png"}[weapon]
        self.projectile_icon = None
        if weapon == "활":
            self.projectile_icon = load_pixel_art("arrow.png", (32, 16))
        elif weapon == "지팡이":
            self.projectile_icon = load_pixel_art("magic_orb.png", (20, 20))
        sprite = load_pixel_art(filename, self.icon.get_size())
        if sprite is not None:
            self.icon.blit(sprite, sprite.get_rect(center=self.icon.get_rect().center))
        elif weapon == "검":
            pygame.draw.polygon(self.icon, "#b4e2ed", [(18, 2), (50, 2), (55, 6), (50, 9), (18, 9)])
            pygame.draw.line(self.icon, "#efbe59", (17, 0), (17, 11), 3)
            pygame.draw.line(self.icon, "#804b30", (2, 6), (17, 6), 3)
        elif weapon == "지팡이":
            pygame.draw.line(self.icon, "#86572f", (13, 44), (26, 12), 5)
            pygame.draw.circle(self.icon, "#664295", (27, 10), 9)
            pygame.draw.circle(self.icon, "#dcbaff", (26, 8), 5)
        else:
            pygame.draw.lines(self.icon, "#ad7840", False, [(11, 2), (21, 9), (26, 19), (23, 29), (11, 37)], 3)
            pygame.draw.line(self.icon, "#f3e7bc", (11, 2), (11, 37), 2)
        if weapon == "검":
            # 칼날 부분의 불투명 픽셀만 판정에 사용한다.
            self.blade = pygame.Surface(self.icon.get_size(), pygame.SRCALPHA)
            blade_area = pygame.Rect(20, 0, 36, 12)
            self.blade.blit(self.icon, blade_area.topleft, blade_area)
            self.left_blade = pygame.transform.flip(self.blade, True, False)
            self.grip, self.held_angle = SWORD_GRIP, 12
        elif weapon == "활":
            self.grip = (24, 28) if sprite is not None else (23, 22)
            self.held_angle = 0
        else:
            self.grip, self.held_angle = ((16, 24), 67) if sprite is not None else ((19, 29), 0)
        self.left_icon = pygame.transform.flip(self.icon, True, False)
        self.resting_icon = self.icon.subsurface(self.icon.get_bounding_rect())
        right, rect = weapon_pose(self.icon, self.grip, (0, 0), 1, self.held_angle)
        left_rect = rect.copy()
        left_rect.right = -rect.left
        self.held_poses = {
            1: (right, rect),
            -1: (pygame.transform.flip(right, True, False), left_rect),
        }

    def held_icon(self, hand_side):
        return self.left_icon if hand_side < 0 else self.icon

    def draw_held(self, screen, offset, player):
        image, rect = self.held_poses[player.hand_side]
        screen.blit(image, rect.move(player.hand_position + offset))

    def is_near(self, player):
        return self.rect.inflate(56, 60).colliderect(player.rect)

    def draw(self, screen, offset, taken):
        base = self.rect.move(offset)
        if self.pedestal is not None:
            screen.blit(self.pedestal, self.pedestal.get_rect(center=base.center))
        else:
            pygame.draw.rect(screen, "#484656", base, border_radius=5)
            pygame.draw.rect(screen, "#aaa4aa", base.inflate(6, -14).move(0, -8), border_radius=5)
        if not taken:
            screen.blit(self.resting_icon, self.resting_icon.get_rect(midbottom=(base.centerx, base.top + 7)))


def training_stands(game_map):
    x, y = game_map.width // 2, game_map.height // 2 - 110
    return [
        WeaponStand(x - 160, y, "검", "전사", Warrior),
        WeaponStand(x, y, "지팡이", "마법사", Mage),
        WeaponStand(x + 160, y, "활", "궁수", Archer),
    ]


class WeaponAttack:
    def __init__(self, player, projectile_icon=None):
        self.weapon = player.weapon
        self.direction = player.facing.copy()
        self.hand_side = player.hand_side
        self.position = player.hand_position
        self.sprite = projectile_icon
        if self.sprite is not None and self.weapon == "활":
            self.sprite = pygame.transform.rotate(self.sprite, -self.direction.as_polar()[1])
        self.age = 0

    def advance(self, dt, bounds, walls):
        self.age += dt
        if self.weapon == "검":
            return self.age < 0.25
        speed = 540 if self.weapon == "활" else 310
        previous = self.position.copy()
        self.position += self.direction * speed * dt
        return (self.age < 1.1 and bounds.collidepoint(self.position)
                and not any(wall.clipline(previous, self.position) for wall in walls))

    def sword_frame(self, player, icon):
        swing = -65 + 130 * self.age / 0.25
        base_angle = 0 if self.hand_side > 0 else 180
        rotation = base_angle - self.direction.as_polar()[1] - self.hand_side * swing
        return weapon_pose(icon, SWORD_GRIP, player.hand_position_on(self.hand_side),
                           self.hand_side, rotation, smooth=True)

    def sword_hits(self, player, stand, target_rect):
        if self.weapon != "검" or self.age >= 0.25:
            return False
        blade = stand.left_blade if self.hand_side < 0 else stand.blade
        image, rect = self.sword_frame(player, blade)
        overlap = rect.clip(target_rect)
        if not overlap:
            return False
        pixels = image.subsurface(overlap.move(-rect.x, -rect.y))
        return pygame.mask.from_surface(pixels).count() > 0

    def draw(self, screen, offset, player, icon):
        if self.weapon == "검":
            blade, rect = self.sword_frame(player, icon)
            screen.blit(blade, rect.move(offset), special_flags=pygame.BLEND_PREMULTIPLIED)
        elif self.sprite is not None:
            screen.blit(self.sprite, self.sprite.get_rect(center=self.position + offset))
        elif self.weapon == "지팡이":
            center = self.position + offset
            pygame.draw.circle(screen, "#a478ed", center, 9)
            pygame.draw.circle(screen, "#eee3ff", center, 5)
        else:
            tip = self.position + offset
            base = tip - self.direction * 8
            side = self.direction.rotate(90) * 4
            pygame.draw.line(screen, "#bb894d", tip - self.direction * 22, tip, 3)
            pygame.draw.polygon(screen, "#e2ebed", [tip, base + side, base - side])
