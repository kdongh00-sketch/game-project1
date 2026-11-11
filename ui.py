import pygame


class GameUI:
    def __init__(self, screen_rect):
        self.screen_rect = screen_rect.copy()

        # 한글을 표시할 폰트
        font_names = "malgungothic,notosanscjkkr,nanumgothic,notosanscjksc"
        self.title_font = pygame.font.SysFont(font_names, 52)
        self.text_font = pygame.font.SysFont(font_names, 28)
        self.hint_font = pygame.font.SysFont(font_names, 22)
        self.map_title_font = pygame.font.SysFont(font_names, 30)

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