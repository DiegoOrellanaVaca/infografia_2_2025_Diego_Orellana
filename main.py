from character import create_rogue, create_tank, create_wizard, create_paladin
import random

CLASSES = {
    '1': ('Rogue', create_rogue),
    '2': ('Tank', create_tank),
    '3': ('Wizard', create_wizard),
    '4': ('Paladin', create_paladin),
}

def choose_class_for(name):
    print(f"Elige clase para {name}:")
    for k,(label,_) in CLASSES.items():
        print(f"  {k}) {label}")
    while True:
        c = input("Selecciona número de clase: ").strip()
        if c in CLASSES:
            return CLASSES[c][1](name)
        print("Opción inválida. Intenta de nuevo.")

def choose_target(players, current_idx):
    alive_indexes = [i for i,p in enumerate(players) if p.is_alive() and i!=current_idx]
    if not alive_indexes:
        return None
    print("Objetivos disponibles:")
    for i in alive_indexes:
        print(f"  {i+1}) {players[i].nombre} (HP {players[i].hp})")
    while True:
        try:
            sel = int(input("Selecciona objetivo (número): "))
            if (sel-1) in alive_indexes:
                return sel-1
        except:
            pass
        print("Selección inválida.")

def print_players(players):
    for i,p in enumerate(players):
        status = p.show_status()
        alive = "VIVO" if p.is_alive() else "MUERTO"
        print(f"{i+1}) {status} - {alive}")

def main():
    print("Bienvenido al juego de luchas más grande del mundo")
    while True:
        try:
            numero_Jugadores = int(input("Selecciona el numero de jugadores [2-4]: "))
            if 2 <= numero_Jugadores <= 4:
                break
        except:
            pass
        print("Número inválido.")
    while True:
        try:
            numero_turnos = int(input("Selecciona el numero de turnos (rondas completas): "))
            if numero_turnos > 0:
                break
        except:
            pass
        print("Ingresa un número válido.")

    players = []
    for i in range(1, numero_Jugadores+1):
        nombre = input(f"Nombre del jugador {i}: ").strip() or f"Jugador{i}"
        p = choose_class_for(nombre)
        players.append(p)

    
    order = list(range(len(players)))
    random.shuffle(order)
    print("Orden de turnos (aleatorio):")
    for pos, idx in enumerate(order, start=1):
        print(f"  Turno {pos}: {players[idx].nombre}")

    
    for ronda in range(1, numero_turnos+1):
        print("\n" + "="*30)
        print(f"Ronda {ronda}/{numero_turnos}")
        print_players(players)

        for turn_pos in order:
            actor = players[turn_pos]
            if not actor.is_alive():
                continue

            print(f"\n-- Turno de {actor.nombre} --")
            
            actor.apply_effects_start_turn()
            if not actor.is_alive():
                print(f"{actor.nombre} murió por efectos al inicio del turno.")
                continue

            
            alive = [p for p in players if p.is_alive()]
            if len(alive) == 1:
                break

            
            while True:
                print("Elige acción:")
                print("  1) Atacar")
                print("  2) Usar habilidad")
                print("  3) Pasar")
                action = input("Acción (1/2/3): ").strip()
                if action == '1':
                    target_idx = choose_target(players, turn_pos)
                    if target_idx is None:
                        print("No hay objetivos válidos.")
                    else:
                        actor.attack(players[target_idx])
                    break
                elif action == '2':
                    
                    for i, ab in enumerate(actor.abilities, start=1):
                        estado = "(AGOTADA)" if ab.uses_left <= 0 else f"usos: {ab.uses_left}"
                        print(f"  {i}) {ab.name} - {estado} - {ab.description}")
                    try:
                        sel = int(input("Selecciona habilidad (número): "))
                        if 1 <= sel <= len(actor.abilities):
                            abil = actor.abilities[sel-1]
                            if not abil.can_use():
                                print("Esa habilidad está agotada. Elige otra acción.")
                                continue  
                           
                            if abil.name in ['Heal', 'Holy Guard', 'Shield Up']:
                                target = actor
                            else:
                                target_idx = choose_target(players, turn_pos)
                                if target_idx is None:
                                    print("No hay target válido.")
                                    continue
                                target = players[target_idx]
                            used = actor.use_ability(sel-1, target)
                            if not used:
                                print("No se pudo ejecutar la habilidad.")
                                continue
                            
                            print(f"  Usos restantes de {abil.name}: {abil.uses_left}")
                            break
                        else:
                            print("Selección inválida.")
                    except Exception as e:
                        print("Entrada inválida.", e)
                elif action == '3':
                    print(f"{actor.nombre} decide pasar.")
                    break
                else:
                    print("Acción inválida. Intenta de nuevo.")

          
            alive = [p for p in players if p.is_alive()]
            if len(alive) == 1:
                break

        
        alive = [p for p in players if p.is_alive()]
        if len(alive) == 1:
            winner = alive[0]
            print("\n¡Juego terminado! Ganador por eliminación:", winner.nombre)
            return

   
    alive = [p for p in players if p.is_alive()]
    if not alive:
        print("Todos murieron. No hay ganador.")
        return
    ganador = max(alive, key=lambda p: p.hp)
    print("\nSe acabaron las rondas. Ganador por mayor HP:", ganador.nombre, f"({ganador.hp} HP)")

if __name__ == '__main__':
    main()
