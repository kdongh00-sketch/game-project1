from player import Player


class Warrior(Player):
    max_shield = 5
    job = "전사"
    base_stats = (50, 20, 10, 40)

    @property
    def basic_attack_damage(self):
        return self.strength * 0.7
