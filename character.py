import random
from typing import List, Dict, Optional


class Ability:
    """
    Clase base para habilidades.
    kind: 'single' (1 uso) o 'uses' (x usos).
    """
    def __init__(self, name: str, kind: str = 'single', uses_left: int = 1, description: str = ""):
        self.name = name
        self.kind = kind
        self.uses_left = uses_left
        self.description = description

    def can_use(self) -> bool:
        return self.uses_left > 0

    def execute(self, user: 'Character', target: Optional['Character']):
        """Sobrescribir en subclases: efecto real de la habilidad."""
        raise NotImplementedError

    def use(self, user: 'Character', target: Optional['Character']) -> bool:
        """Llamar para intentar usar la habilidad. Devuelve True si se usó."""
        if not self.can_use():
            print(f"  La habilidad {self.name} está agotada.")
            return False

        print(f"{user.nombre} usa {self.name} {'sobre ' + target.nombre if target else 'sobre sí mismo'}")
        self.execute(user, target)

      
        if self.kind == 'single':
            self.uses_left = 0
        elif self.kind == 'uses':
            self.uses_left = max(0, self.uses_left - 1)
        return True


class RogueCritBurst(Ability):
    def __init__(self):
        super().__init__("Crit Burst", kind='single', uses_left=1, description="Gran daño single-use")

    def execute(self, user, target):
        dmg = user.base_damage * 3
        print(f"  {user.nombre} hace Crit Burst a {target.nombre} por {dmg}")
        target.hurt(dmg)

class RoguePoison(Ability):
    def __init__(self):
        super().__init__("Poison Blade", kind='uses', uses_left=2, description="Aplica DoT 3 turnos")

    def execute(self, user, target):
        target.add_effect({'type': 'dot', 'name': 'Poison', 'value': 5, 'turns': 3})
        print(f"  {target.nombre} queda envenenado por 3 turnos (5 dmg/turno).")


class TankShieldUp(Ability):
    def __init__(self):
        super().__init__("Shield Up", kind='uses', uses_left=2, description="Aumenta parry por X turnos")

    def execute(self, user, target):
        user.add_effect({'type': 'buff', 'name': 'Shield Up', 'what': 'parry', 'value': 0.25, 'turns': 2})
        print(f"  {user.nombre} aumenta su parry +0.25 por 2 turnos.")

class TankCrush(Ability):
    def __init__(self):
        super().__init__("Crush", kind='uses', uses_left=2, description="Daño fuerte, varios usos")

    def execute(self, user, target):
        dmg = user.base_damage * 2
        print(f"  {user.nombre} hace Crush a {target.nombre} por {dmg}")
        target.hurt(dmg)


class WizardFireball(Ability):
    def __init__(self):
        super().__init__("Fireball", kind='single', uses_left=1, description="Gran daño single-use")

    def execute(self, user, target):
        dmg = user.base_damage * 3
        print(f"  {user.nombre} lanza Fireball a {target.nombre} por {dmg}")
        target.hurt(dmg)

class WizardBurn(Ability):
    def __init__(self):
        super().__init__("Burn", kind='uses', uses_left=2, description="DoT por 2 turnos")

    def execute(self, user, target):
        target.add_effect({'type': 'dot', 'name': 'Burn', 'value': 7, 'turns': 2})
        print(f"  {target.nombre} sufre Burn: 7 dmg por 2 turnos.")


class PaladinHeal(Ability):
    def __init__(self):
        super().__init__("Heal", kind='uses', uses_left=2, description="Cura al usuario")

    def execute(self, user, target):
        heal = 30
        user.hp = min(user.max_hp, user.hp + heal)
        print(f"  {user.nombre} se cura {heal}. Queda {user.hp} HP.")

class PaladinHolyGuard(Ability):
    def __init__(self):
        super().__init__("Holy Guard", kind='uses', uses_left=2, description="Aumenta parry por X turnos")

    def execute(self, user, target):
        user.add_effect({'type': 'buff', 'name': 'Holy Guard', 'what': 'parry', 'value': 0.2, 'turns': 2})
        print(f"  {user.nombre} activa Holy Guard: +0.2 parry por 2 turnos.")


class Character:
    def __init__(self, nombre: str, hp: int, base_damage: int, parry_prob: float, crit_prob: float):
        self.nombre = nombre
        self.max_hp = hp
        self.hp = hp
        self.base_damage = base_damage
        self.parry_prob = parry_prob
        self.crit_prob = crit_prob

        self.effects: List[Dict] = []
        self.abilities: List[Ability] = []

    def is_alive(self) -> bool:
        return self.hp > 0

    def apply_effects_start_turn(self):
        to_remove = []
        for e in list(self.effects):
            if e['type'] == 'dot':
                dmg = e['value']
                self.hp -= dmg
                if self.hp < 0: self.hp = 0
                print(f"  {self.nombre} recibe {dmg} de {e.get('name','DoT')} (queda {self.hp} HP).")
            elif e['type'] == 'hot':
                heal = e['value']
                self.hp = min(self.max_hp, self.hp + heal)
                print(f"  {self.nombre} se cura {heal} por {e.get('name','HoT')} (queda {self.hp} HP).")
            e['turns'] -= 1
            if e['turns'] <= 0:
                to_remove.append(e)
        for r in to_remove:
            self.effects.remove(r)
            print(f"  Efecto {r.get('name','(efecto)')} en {self.nombre} ha terminado.")

    def current_parry(self) -> float:
        parry = self.parry_prob
        for e in self.effects:
            if e['type'] == 'buff' and e.get('what') == 'parry':
                parry += e['value']
        return min(0.95, parry)

    def current_crit(self) -> float:
        crit = self.crit_prob
        for e in self.effects:
            if e['type'] == 'buff' and e.get('what') == 'crit':
                crit += e['value']
        return min(0.95, crit)

    def attack(self, other: 'Character'):
        crit_chance = self.current_crit()
        damage = self.base_damage * 2 if random.random() <= crit_chance else self.base_damage
        print(f"{self.nombre} ataca a {other.nombre} ({'CRIT' if damage > self.base_damage else 'normal'}) -> daño {damage}")
        other.hurt(damage)

    def hurt(self, damage: int):
        if random.random() <= self.current_parry():
            print(f"  {self.nombre} realiza un PARRY y evita el daño.")
            return
        self.hp -= damage
        if self.hp < 0:
            self.hp = 0
        print(f"  {self.nombre} recibe {damage} de daño, queda {self.hp} HP.")

    def add_effect(self, effect: Dict):
        self.effects.append(effect)

    def add_ability(self, ability: Ability):
        self.abilities.append(ability)

    def use_ability(self, idx: int, target: Optional['Character']) -> bool:
        if idx < 0 or idx >= len(self.abilities):
            print("Índice de habilidad inválido.")
            return False
        ability = self.abilities[idx]
        if not ability.can_use():
            print(f"  {ability.name} no tiene usos restantes.")
            return False
        return ability.use(self, target)

    def show_status(self) -> str:
        return f"{self.nombre} HP:{self.hp}/{self.max_hp} DMG:{self.base_damage} PAR:{self.current_parry():.2f} CRIT:{self.current_crit():.2f}"



def create_rogue(nombre: str) -> Character:
    c = Character(nombre, hp=80, base_damage=25, parry_prob=0.05, crit_prob=0.25)
    c.add_ability(RogueCritBurst())
    c.add_ability(RoguePoison())
    return c

def create_tank(nombre: str) -> Character:
    c = Character(nombre, hp=220, base_damage=12, parry_prob=0.25, crit_prob=0.05)
    c.add_ability(TankShieldUp())
    c.add_ability(TankCrush())
    return c

def create_wizard(nombre: str) -> Character:
    c = Character(nombre, hp=70, base_damage=18, parry_prob=0.05, crit_prob=0.18)
    c.add_ability(WizardFireball())
    c.add_ability(WizardBurn())
    return c

def create_paladin(nombre: str) -> Character:
    c = Character(nombre, hp=150, base_damage=16, parry_prob=0.15, crit_prob=0.08)
    c.add_ability(PaladinHeal())
    c.add_ability(PaladinHolyGuard())
    return c
