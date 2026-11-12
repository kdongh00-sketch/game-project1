from pathlib import Path
from collections import Counter

import pygame


INK = "#302c35"
CREAM = "#fff1cf"
SHOP_ART = Path(__file__).resolve().parent / "assets" / "shop"


def load_shop_art(name, size):
    path = SHOP_ART / f"{name}.png"
    if path.is_file():
        source = pygame.image.load(str(path)).convert_alpha()
        return pygame.transform.scale(source, source.get_rect().fit(pygame.Rect((0, 0), size)).size)
    return None


def label(surface, font, text, center, color):
    image = font.render(text, True, color)
    surface.blit(image, image.get_rect(center=center))


class Village:
    def __init__(self, game_map, ui):
        self.places = {
            obj.name: pygame.Rect(obj.x, obj.y, obj.width, obj.height)
            for obj in game_map.map_data.get_layer_by_name("Interactions")
        }
        for key, name, roof in (("hospital", "병원", "#659798"), ("shop", "상점", "#ab5d52")):
            r = self.places[key]
            game_map.walls.append(r)
            canvas = game_map.background
            if key == "shop":
                exterior = load_shop_art("exterior", r.size)
                if exterior is not None:
                    canvas.blit(exterior, exterior.get_rect(midbottom=r.midbottom))
                    label(canvas, ui.hint_font, name, (r.centerx,r.top-14), CREAM)
                    continue
            pygame.draw.rect(canvas, INK, r, border_radius=5)
            pygame.draw.rect(canvas, "#e7ce9d", r.inflate(-8, -8))
            pygame.draw.polygon(canvas, roof, [(r.left-7,r.top+24), (r.left+9,r.top-8),
                                              (r.right-9,r.top-8), (r.right+7,r.top+24)])
            pygame.draw.rect(canvas, "#704b42", (r.centerx-16,r.bottom-30,32,30))
            label(canvas, ui.hint_font, name, (r.centerx,r.centery), INK)
        self.draw_gate(game_map.background, self.places["tower"])
        r = self.places["tower"]
        label(game_map.background, ui.hint_font, "타워", (r.centerx,r.bottom+15), CREAM)

    @staticmethod
    def draw_gate(canvas, rect):
        pygame.draw.ellipse(canvas, "#383148", rect)
        pygame.draw.ellipse(canvas, "#bd93ee", rect.inflate(-8,-8), 5)
        pygame.draw.ellipse(canvas, "#7354a0", rect.inflate(-22,-14), 2)

    def nearby(self, player):
        return next((key for key, rect in self.places.items()
                     if rect.inflate(48, 48).colliderect(player.rect)), None)


class TowerEntrance:
    def __init__(self, ui):
        self.width, self.height = 576, 384
        self.background = pygame.Surface((self.width,self.height))
        self.background.fill("#363346")
        for row in range(0,self.height,32):
            for col in range(-32 if row % 64 else 0,self.width,64):
                pygame.draw.rect(self.background,"#50495f",(col+1,row+1,62,30))
        self.walls = []
        self.exit = pygame.Rect(self.width//2-35,self.height-95,70,76)
        Village.draw_gate(self.background,self.exit)
        label(self.background,ui.hint_font,"마을로",(self.exit.centerx,self.exit.top-18),CREAM)

    def draw(self, screen, offset):
        screen.blit(self.background, offset)


ITEMS = (
    ("체력 물약", "붉은색 회복 물약", "#c85753"),
    ("마나 물약", "푸른색 마나 물약", "#557dc4"),
    ("검", "전사가 사용하는 검", "#bfcbd3"),
    ("지팡이", "마법사가 사용하는 지팡이", "#ab80c8"),
    ("활", "궁수가 사용하는 활", "#ad7543"),
    ("화살", "활에 사용하는 화살", "#b29156"),
)
PRICES = (10, 10, 50, 50, 50, 5)
JOB_STOCK = {"전사": (2,), "마법사": (3,), "궁수": (4, 5)}


def item_icon(surface, index, x, y, color):
    if index < 2:
        pygame.draw.circle(surface, INK, (x,y+3), 12)
        pygame.draw.circle(surface, color, (x,y+3), 10)
        pygame.draw.rect(surface, "#d4ab74", (x-4,y-13,8,8))
        pygame.draw.circle(surface, CREAM, (x-3,y), 2)
    elif index == 2:
        pygame.draw.polygon(surface,color,[(x-7,y+8),(x+8,y-14),(x+12,y-15),(x+11,y-9),(x-4,y+10)])
        pygame.draw.line(surface,INK,(x-10,y+6),(x-1,y+12),3)
    elif index == 3:
        pygame.draw.line(surface,"#835839",(x-7,y+14),(x+6,y-9),4)
        pygame.draw.circle(surface,color,(x+7,y-10),6)
    elif index == 4:
        pygame.draw.lines(surface,color,False,[(x-6,y-15),(x+6,y-6),(x+9,y+2),(x-6,y+15)],4)
        pygame.draw.line(surface,INK,(x-6,y-15),(x-6,y+15))
    else:
        pygame.draw.line(surface,color,(x-12,y+12),(x+9,y-9),3)
        pygame.draw.polygon(surface,INK,[(x+13,y-14),(x+9,y-3),(x+3,y-9)])


class Shop:
    def __init__(self, ui, player):
        self.ui = ui
        self.player = player
        self.page = 1
        self.cart = Counter()
        self.in_cart = False
        self.cart_index = 0
        self.notice = ""
        self.selected = 0
        self.image = None
        self.fonts = {}
        self.art = {name: load_shop_art(name, size) for name, size in (
            ("interior", (960,540)), ("owner", (136,220)), ("counter", (370,86)),
            ("panel", (572,301)), ("slot", (84,86)), ("slot_selected", (84,86)))}
        self.icons = [load_shop_art(name, (32,32)) for name in
                      ("health_potion","mana_potion","sword","staff","bow","arrow")]

    def draw_item(self, art, i, x, y):
        icon = self.icons[i]
        if icon is None:
            item_icon(art,i,x,y,ITEMS[i][2])
        else:
            art.blit(icon,icon.get_rect(center=(x,y)))

    def place_art(self, surface, name, rect):
        image = self.art[name]
        if image is None:
            return False
        surface.blit(image, image.get_rect(center=pygame.Rect(rect).center))
        return True

    @property
    def stock(self):
        return (0, 1) if self.page == 1 else JOB_STOCK[self.player.job]

    def handle_key(self, key):
        """Return True when the player leaves the shop."""
        self.image = None
        self.notice = ""
        if self.in_cart:
            rows = list(self.cart)
            if key == pygame.K_ESCAPE:
                self.in_cart = False
            elif key in (pygame.K_UP, pygame.K_DOWN) and rows:
                self.cart_index = (self.cart_index + (1 if key == pygame.K_DOWN else -1)) % len(rows)
            elif key == pygame.K_BACKSPACE and rows:
                item = rows[self.cart_index]
                self.cart[item] -= 1
                if not self.cart[item]:
                    del self.cart[item]
                self.cart_index = min(self.cart_index, max(0, len(self.cart)-1))
            elif key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                cost = self.total()
                if not rows:
                    self.notice = "장바구니가 비어 있습니다"
                elif self.player.gold < cost:
                    self.notice = f"골드가 {cost - self.player.gold}G 부족합니다"
                else:
                    for item, count in self.cart.items():
                        self.player.inventory[ITEMS[item][0]] += count
                    self.player.gold -= cost
                    self.cart.clear()
                    self.cart_index = 0
                    self.notice = "구매 완료 · 인벤토리에 담았습니다"
            return False
        if key == pygame.K_ESCAPE:
            return True
        if key in (pygame.K_1, pygame.K_2):
            self.page = 1 if key == pygame.K_1 else 2
            self.selected = 0
        elif key in (pygame.K_LEFT, pygame.K_RIGHT):
            self.selected = (self.selected + (1 if key == pygame.K_RIGHT else -1)) % len(self.stock)
        elif key == pygame.K_f:
            item = self.stock[self.selected]
            self.cart[item] += 1
            self.notice = f"{ITEMS[item][0]} 1개를 담았습니다"
        elif key == pygame.K_b:
            self.in_cart = True
        return False

    def total(self):
        return sum(PRICES[item] * count for item, count in self.cart.items())

    def draw(self, screen):
        area = pygame.Rect(0,0,960,540).fit(screen.get_rect())
        if self.image is None or self.image.get_size() != area.size:
            art = pygame.Surface((960, 540))
            art.fill("#416a59")
            if not self.place_art(art,"interior",art.get_rect()):
                for y in (118, 180, 242):
                    pygame.draw.rect(art,"#684739",(38,y,324,9))
                    pygame.draw.rect(art,"#c49868",(38,y,324,3))
            for i, item in enumerate(self.stock):
                self.draw_item(art,item,92+(i%2)*84,100+(i//2)*62)
            # 카운터 뒤의 상점 주인
            if not self.place_art(art,"owner",(73,291,136,220)):
                pygame.draw.ellipse(art,"#273e39",(73,352,135,159))
                pygame.draw.rect(art,"#c38e62",(106,379,67,81),border_radius=10)
                pygame.draw.circle(art,"#cf946d",(140,331),38)
                pygame.draw.arc(art,"#503831",(102,291,77,61),0,3.15,13)
                for x in (127,151):
                    pygame.draw.circle(art,INK,(x,331),3)
            if not self.place_art(art,"counter",(0,454,370,86)):
                pygame.draw.rect(art,"#76513e",(0,454,370,86))
                pygame.draw.rect(art,"#bc9567",(0,454,370,9))
            if not self.place_art(art,"panel",(373,18,572,301)):
                pygame.draw.rect(art,"#e8c77c",(373,18,572,301),border_radius=8)
            for i, item in enumerate(() if self.in_cart else self.stock):
                slot = pygame.Rect(389+i*91,77,84,86)
                if not (i == self.selected and self.place_art(art,"slot_selected",slot)):
                    if not self.place_art(art,"slot",slot):
                        pygame.draw.rect(art,"#fff0c8",slot,border_radius=5)
                    pygame.draw.rect(art,"#315b79" if i == self.selected else "#9d7845",
                                     slot,4 if i == self.selected else 2,border_radius=5)
                self.draw_item(art,item,slot.centerx,slot.y+26)
            self.image = pygame.transform.scale(art,area.size)
            self.draw_labels()
        screen.fill(INK)
        screen.blit(self.image,self.image.get_rect(center=screen.get_rect().center))

    def draw_labels(self):
        sx = self.image.get_width() / 960
        sy = self.image.get_height() / 540
        def text(value, x, y, size, color=INK, centered=True):
            px = max(1,round(size * sy))
            if px not in self.fonts:
                self.fonts[px] = pygame.font.Font(str(self.ui.font_path),px)
            rendered = self.fonts[px].render(value,True,color)
            pos = (round(x*sx),round(y*sy))
            self.image.blit(rendered,rendered.get_rect(center=pos) if centered else pos)

        text("상점 주인",141,494,28,CREAM)
        text(f"보유 {self.player.gold}G",795,45,19)
        if self.in_cart:
            text("장바구니",465,45,25)
            if not self.cart:
                text("담긴 물품이 없습니다",402,95,22,centered=False)
            for row,(item,count) in enumerate(self.cart.items()):
                marker = "▶" if row == self.cart_index else "  "
                text(f"{marker}  {ITEMS[item][0]} × {count}",398,78+row*32,20,centered=False)
                text(f"{PRICES[item]*count}G",841,95+row*32,20)
            text(f"합계  {self.total()}G",402,216,23,centered=False)
            help_line = "↑↓ 선택   Backspace 1개 빼기   Enter 구매   Esc 돌아가기"
        else:
            text("1 물약" if self.page == 1 else f"2 무기 · {self.player.job}",396,29,25,centered=False)
            for i,item in enumerate(self.stock):
                text(ITEMS[item][0],431+i*91,139,17)
            item = self.stock[self.selected]
            name,description,_ = ITEMS[item]
            text(f"{name}   {PRICES[item]}G",393,178,24,centered=False)
            text(description,393,219,20,centered=False)
            help_line = f"1 물약  2 무기   ←→ 선택   F 담기   B 바구니({sum(self.cart.values())})   Esc 나가기"
        if self.notice:
            text(self.notice,401,266,18,centered=False)
        text(help_line,666,485,16,CREAM)
