import random
from assets import player_classes, enemy_types, Tile, cave_description, Game, Condition, conditions


def d20():
    return random.randint(1, 20)


def attack(attacker, target, weapon):
    if attacker == player:
        dice = d20()
        if dice + attacker.attack + weapon.attack_bonus >= target.ac:
            target.hp -= weapon.damage
            print(f'd{dice} + {attacker.attack} + {weapon.attack_bonus} = '
                  f'{dice + attacker.attack + weapon.attack_bonus}. Target AC: {target.ac}.')
            if target.hp <= 0:
                player.location.enemy = 0  # the enemy is removed from the current player tile
                # enemy should also be removed from enemies list? maybe later
                attacker.xp += target.xp_worth
                attacker.killed += 1
                print(f'You attack the {target.name} with your {weapon.name} for {weapon.damage} damage and kill it.'
                      f' You gain {target.xp_worth} XP.')
            else:
                print(f"You hit the {target.name} for {weapon.damage} damage but somehow it's still kicking.")
                attack(target, attacker, target.weapon)  # this will be replaced with enemy_ai
        else:
            print(
                f'd{dice} + {attacker.attack} + {weapon.attack_bonus} = {dice + attacker.attack + weapon.attack_bonus}.'
                f'Target AC: {target.ac}.')
            print(f'You missed!')
            attack(target, attacker, target.weapon)  # this will be replaced with enemy_ai
    else:  # if the attacker is the enemy
        dice = d20()
        if dice + attacker.attack + weapon.attack_bonus >= target.ac:
            target.hp -= weapon.damage
            print(f'The {attacker.name} attacks you with its {weapon.name} and hits you for {weapon.damage} damage!')
            if weapon.apply_condition != 0:  # if weapon applies a condition ie. poison
                target.condition = weapon.apply_condition
                print(f'You have been {target.condition.name}.')
        else:
            print(f'The {attacker.name} strikes back with its {weapon.name} but misses!')


def gen_enemy():
    if d20() - player.level - game.difficulty < 15:
        new_enemy = random.choice(enemy_types)
        return new_enemy
    else:
        return 0


def gen_tile(location, chosen_path):
    if not game.cave_map.__contains__((location, chosen_path)):  # checks if the player has taken that path before
        new_tile = Tile(ways_out=random.randint(1, 3), trap_type=0, text_description=cave_description(), enemy=0,
                        link0=location, link1=-1, link2=-1, link3=-1, visited=False, start_tile=False)
        # link0(back) always links to current tile
        if chosen_path == 1:  # links current location tile to the newly generated tile by chosen_path
            player.location.link1 = new_tile  # path 1 of current tile links to the newly generated tile
        elif chosen_path == 2:
            player.location.link2 = new_tile  # path 2 of current tile links to the newly generated tile
        elif chosen_path == 3:
            player.location.link3 = new_tile  # path 3 of current tile links to the newly generated tile

        # print(f'Generated tile{new_tile_id}. tile{location} is linked to tile{new_tile_id} by link{chosen_path}.')
        # print(f'Tile {new_tile_id} is {tile[-1].text_description}')

        player.location = new_tile  # player location gets updated to the newly generated tile
        player.location.enemy = gen_enemy()  # the newly generated tile gets a newly generated enemy
        game.cave_map.append((location, chosen_path))  # records that the player has chosen this path from this tile

    else:
        if chosen_path == 1:  # if path was taken before, player location is updated to previously generated tile
            player.location = player.location.link1
        elif chosen_path == 2:
            player.location = player.location.link2
        elif chosen_path == 3:
            player.location = player.location.link3


def gen_tile0():
    tile0 = Tile(ways_out=1, trap_type=0, text_description="a recently collapsed cave", enemy=0, link0=-1, link1=-1,
                 link2=-1, link3=-1, visited=True, start_tile=True)  # new_tile object of class Tile gets created
    player.location = tile0
    print(f"""Your eyes barely open after the fall and you realize you're now underground.
Determined to get out of here, you evaluate your options.
You can always check your [C]haracter sheet.""")


def present_tile():
    if player.location.start_tile and len(game.cave_map) > 0:  # checks if player is back in tile0
        print(f"You're back in that damned collapsed cave where you started.")
    elif not player.location.visited:  # checks if the current tile was not visited before by the player
        print(f"""Exploring further, you find {player.location.text_description}.""")
        player.location.visited = True  # marks current tile as visited by the player
    elif len(game.cave_map) > 0:  # checks if it's another visited tile than tile 0
        print(f"You find yourself in {player.location.text_description}. You recognize the place "
              f"but it gives you no comfort.")


def get_player_input():
    if player.location.enemy != 0:
        print(f'A {player.location.enemy.name} faces you. You can either [A]ttack it or go [B]ack.')
    else:
        print(f'You may Res[T] here and risk being ambushed in the hope of regaining some HP.')
        if player.location.ways_out == 1 and not player.location.start_tile:
            print(f'There is a way [F]orward. You could also go [B]ack.')
        elif player.location.ways_out == 1 and player.location.start_tile:
            print(f'You cannot go back up. The only way is [F]orward.')
        elif player.location.ways_out == 2:
            print(f'You can either go [L]eft or [R]ight or [B]ack.')
        elif player.location.ways_out == 3:
            print(f'You can choose to go [L]eft, [F]orward or [R]ight. Or you can turn [B]ack the way you came.')

    command = input(f'You choose to: ')
    if command.upper() == 'C':
        player.sheet()
    elif command.upper() == "B" and not player.location.start_tile:
        player.location = player.location.link0  # player goes to the previous tile
    elif command.upper() == "B" and player.location.start_tile:
        print(f'You cannot go back up. The only way is [F]orward.')
    elif command.upper() == "L" and player.location.enemy == 0 and player.location.ways_out >= 2:
        gen_tile(player.location, 1)
    elif command.upper() == "F" and player.location.enemy == 0 and player.location.ways_out != 2:
        gen_tile(player.location, 2)
    elif command.upper() == "R" and player.location.enemy == 0 and player.location.ways_out >= 2:
        gen_tile(player.location, 3)
    elif command.upper() == "A" and player.location.enemy != 0:
        attack(player, player.location.enemy, player.weapon)
    elif command.upper() == "T" and player.location.enemy == 0:
        rest()
    elif command.upper() == "T" and player.location.enemy != 0:
        print(f'You cannot rest under the gaze of the {player.location.enemy.name}!')
    elif command.upper() == "L" or "F" or "R" and player.location.enemy != 0:  # BUG if F and there's only L and R
        print(f'You cannot advance past the enemy.')
    else:
        print(f'Wrong command.')


def rest():
    if random.randint(1, 10) + game.difficulty > 5:  # chance to get ambushed scales with game difficulty
        player.location.enemy = gen_enemy()
        print(f"Your rest is interrupted and you've been ambushed!")
        attack(player.location.enemy, player, player.location.enemy.weapon)  # enemy attacks first if it ambushes you
        get_player_input()
    else:
        player.hp += 2
        if player.hp > player.max_hp:
            player.hp = player.max_hp
        print(f'You got a well-deserved rest and are now at {player.hp}/{player.max_hp} HP.')


def check_player_condition():
    if player.condition != 0 and player.condition == conditions[0]:  # Code problem?
        player.hp -= 1
        print(f'You take 1 damage from being poisoned.')
        if d20() >= 10:
            player.condition = 0
            print(f'Your system has ridden itself of the poison.')


def start_turn():
    print("")
    check_player_condition()
    present_tile()
    get_player_input()


def choose_class():
    global player
    print(f'Welcome to text_RPG. You can play as one of 3 classes:')
    for i in player_classes:
        player = i
        player.sheet()
    choice = input("""Choose:
[1] Ranger
[2] Fighter
[3] Wizard
""")
    if choice == '1':
        player = player_classes[0]  # Ranger
        print(f'You are a Ranger.')
    elif choice == '2':
        player = player_classes[1]  # Fighter
        print(f'You are a Fighter.')
    elif choice == '3':
        player = player_classes[2]  # Wizard
        print(f'You are a Wizard.')
    else:
        print(f'Invalid input.')
        choose_class()


game = Game(difficulty=1, length=5, cave_map=[])  # initialize the game object
# player = player_classes[0]  # initializes the player object as a Ranger
choose_class()  # player chooses his class
gen_tile0()  # generate the start tile

while True:
    if player.hp > 0:
        if len(game.cave_map) < game.length + player.level + game.difficulty or player.location.enemy != 0:
            # checks if reached maximum no of tiles for the game and that there's no enemy on the last tile
            start_turn()
        else:
            print(f'You have reached the end of the dungeon and can return safely to the surface!')
            break
            # this doesn't stop the game?
    else:
        print(f'You are dead. Vermin will feed on your remains.')
        break