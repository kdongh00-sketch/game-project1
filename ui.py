from pathlib import Path

import pygame
from player import STAT_NAMES


class GameUI:
    def __init__(self, screen_rect):
        self.screen_rect = screen_rect.copy()

        # 한글을 표시할 폰트
        self.font_path = font_path = Path(__file__).resolve().parent / "assets" / "fonts" / "NotoSansKR-VF.ttf"
        self.title_font = pygame.font.Font(str(font_path), 52)
        self.text_font = pygame.font.Font(str(font_path), 28)
        self.hint_font = pygame.font.Font(str(font_path), 22)
        self.map_title_font = pygame.font.Font(str(font_path), 30)
        hud_dir = Path(__file__).resolve().parent / "assets" / "hud"
        def hud_image(name):
            image = pygame.image.load(str(hud_dir / f"{name}.png")).convert_alpha()
            return pygame.transform.scale(
                image, (2 * image.get_width(), 2 * image.get_height()))

        self.status_panel = hud_image("panel")
        self.stats_panel = hud_image("stats_panel")
        self.status_rows = [(name, hud_image(name), hud_image(f"{name}_bar"))
                            for name in ("health", "shield", "mana")]
        self.status_font = pygame.font.Font(None, 22)
        self.status_font.set_bold(True)
        self.status_rect = self.status_panel.get_rect(topleft=(16, 12))

        # 게임 시작 버튼
        self.start_button = pygame.Rect(0, 0, 280, 72)
        self.start_button.center = (
            screen_rect.centerx,
            screen_rect.centery + 30,
        )

        # 종료 확인창 뒤에 깔리는 반투명 배경
        self.shade = pygame.Surface(
            screen_rect.size,
            pygame.SRCALPHA,
        )
        self.shade.fill((0, 0, 0, 170))

        # 종료 확인창
        self.exit_panel = pygame.Rect(0, 0, 600, 220)
        self.exit_panel.center = screen_rect.center

    def draw_status(self, screen, player):
        screen.blit(self.status_panel, self.status_rect)
        for index, (name, icon, bar) in enumerate(self.status_rows):
            top = self.status_rect.top + 8 + index * 24
            left = self.status_rect.left + 36
            current = getattr(player, name)
            maximum = getattr(player, f"max_{name}")
            screen.blit(icon, (self.status_rect.x + 8, top))
            width = round(bar.get_width() * max(0, min(1, current / maximum))) if maximum else 0
            if width:
                screen.blit(bar, (left, top + 2), (0, 0, width, bar.get_height()))
            value = f"{current:g}/{maximum:g}"
            text = self.status_font.render(value, True, "#fff8dd")
            rect = text.get_rect(center=(left + bar.get_width() // 2, top + 10))
            shadow = self.status_font.render(value, True, "#292331")
            screen.blit(shadow, rect.move(1, 2))
            screen.blit(text, rect)

    def draw_job_prompt(self, screen, job):
        question = self.text_font.render(f"{job}로 전직하시겠습니까?", True, "#ffffff")
        controls = self.hint_font.render("Enter: 전직    Esc: 취소", True, "#efe1b3")
        panel = pygame.Rect(16, self.status_rect.bottom + 8, max(question.get_width(), controls.get_width()) + 32,
                            question.get_height() + controls.get_height() + 32)
        pygame.draw.rect(screen, "#272631", panel, border_radius=8)
        screen.blit(question, (panel.x + 16, panel.y + 10))
        screen.blit(controls, (panel.x + 16, panel.y + 18 + question.get_height()))

    def draw_stats(self, screen, player):
        screen.blit(self.shade, (0, 0))
        panel = self.stats_panel.get_rect(center=screen.get_rect().center)
        screen.blit(self.stats_panel, panel)
        def write(value, x, y, color, right=False):
            text = self.hint_font.render(str(value), True, color)
            rect = text.get_rect()
            if right:
                rect.midright = panel.x + x, panel.y + y
            else:
                rect.midleft = panel.x + x, panel.y + y
            screen.blit(text, rect)
        write(player.job, 24, 30, "#fff2cd")
        write(f"Lv. {player.level}", 374, 30, "#ffe19a", True)
        write("남은 포인트", 24, 74, "#352a28")
        write(player.stat_points, 374, 74, "#352a28", True)
        for index, (stat, name) in enumerate(STAT_NAMES):
            y = 117 + index * 41
            write(index + 1, 35, y, "#ffe19a")
            write(name, 80, y, "#fff2dc")
            write(getattr(player, stat), 368, y, "#fff2dc", True)
        write("1~4: 능력치 +1    Tab / Esc: 닫기", 24, 288, "#352a28")

    def draw_inventory(self, screen, player):
        screen.blit(self.shade, (0, 0))
        panel = self.stats_panel.get_rect(center=screen.get_rect().center)
        screen.blit(self.stats_panel, panel)
        lines = [(f"인벤토리     {player.gold}G", 16, "#fff2cd"),
                 ("보유 물품", 59, "#352a28"), ("I / Esc: 닫기", 274, "#352a28")]
        items = list(player.inventory.items()) or [("비어 있습니다", None)]
        for row, (name, count) in enumerate(items):
            label = name if count is None else f"{name}   × {count}"
            lines.append((label, 101 + row * 41, "#fff2dc"))
        for label, y, color in lines:
            screen.blit(self.hint_font.render(label, True, color), (panel.x+28, panel.y+y))

    def start_clicked(self, event):
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.start_button.collidepoint(event.pos)
        )

    def draw_text(self, screen, text, font, color, center):
        image = font.render(text, True, color)
        screen.blit(image, image.get_rect(center=center))

    def draw_start(self, screen):
        screen.fill((25, 30, 40))

        self.draw_text(
            screen,
            "TOWER RPG",
            self.title_font,
            (240, 240, 245),
            (
                self.screen_rect.centerx,
                self.screen_rect.centery - 100,
            ),
        )

        hovered = self.start_button.collidepoint(
            pygame.mouse.get_pos()
        )

        button_color = (
            (65, 145, 110) if hovered else (45, 105, 80)
        )

        pygame.draw.rect(
            screen,
            button_color,
            self.start_button,
            border_radius=10,
        )

        self.draw_text(
            screen,
            "게임 시작",
            self.text_font,
            (255, 255, 255),
            self.start_button.center,
        )

        self.draw_text(
            screen,
            "ESC: 종료 확인",
            self.hint_font,
            (180, 185, 195),
            (
                self.screen_rect.centerx,
                self.start_button.bottom + 45,
            ),
        )

    def draw_exit_dialog(self, screen):
        screen.blit(self.shade, (0, 0))

        pygame.draw.rect(
            screen,
            (40, 45, 55),
            self.exit_panel,
            border_radius=12,
        )

        pygame.draw.rect(
            screen,
            (125, 135, 155),
            self.exit_panel,
            width=2,
            border_radius=12,
        )

        self.draw_text(
            screen,
            "게임을 나가겠습니까?",
            self.text_font,
            (255, 255, 255),
            (
                self.exit_panel.centerx,
                self.exit_panel.centery - 30,
            ),
        )

        self.draw_text(
            screen,
            "Enter: 종료    ESC: 취소",
            self.hint_font,
            (205, 210, 220),
            (
                self.exit_panel.centerx,
                self.exit_panel.centery + 40,
            ),
        )
