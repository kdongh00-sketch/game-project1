from player import Player


class Warrior(Player):
    def __init__(self, x, y):
        # Player에 있는 이미지와 이동 설정 가져오기
        super().__init__(x, y)

        self.job = "전사"
        self.strength = 50
        self.agility = 20
        self.magic = 10
        self.vitality = 40

        self.max_mana = self.magic
        self.mana = float(self.max_mana)

        self.basic_attack_damage = self.strength * 0.7