import random
from assets import player_classes, enemy_types, Tile, cave_description

# global variables
difficulty = 1  # used to adjust dice rolls for traps and enemy generation
player_level = 1  # used to adjust dice rolls for traps and enemy generation
max_tiles = 5  # tiles at which the end tile is generated
enemy = []  # global enemies list. used to call enemies by index
tile = []  # global tiles list. used to call tiles by index
cave_map = []  # global list of pairs (tile, path taken, where it leads) to prevent new tile generation


def d20():
    import random
    return random.randint(1, 20)


def check_condition(target):
    if target.condition == 'poisoned':
        target.hp -= 1
        print(f'You take 1 damage from being poisoned.')
        if d20() >= 10:
            target.condition = 0
            print(f'Your system has ridden itself of the poison.')
    elif target.condition == 'hobbled':
        target.condition = 0
        print(f'You are hobbled and cannot move this turn.')
        return 'hobbled'
    elif target.condition == 'blind':  # to review
        target.ac -= 4
        print(f'You are blind and your attack suffers greatly.')
        if d20() >= 10:
            target.condition = 0
            target.ac += 4
            print(f'Your vision has been restored and you are no longer blind.')


def player_attack(attacker, target, weapon):
    dice = d20()
    if dice + attacker.attack + weapon.attack >= target.ac:
        target.hp -= weapon.damage
        print(f'd{dice} + {attacker.attack} + {weapon.attack} = {dice+attacker.attack+weapon.attack}. '
              f'Target AC: {target.ac}.')
        if target.hp <= 0:
            tile[attacker.location].enemy = 0  # the enemy is removed from the current player tile
            # enemy should also be removed from enemies list? maybe later
            attacker.xp += target.xp_worth
            print(f'You attack the {target.name} with your {weapon.name} for {weapon.damage} damage and kill it.'
                  f' You gain {target.xp_worth} XP.')
        else:
            print(f"You hit the {target.name} for {weapon.damage} damage but somehow it's still kicking.")
            enemy_attack(target, attacker, target.weapon)  # this will be replaced with enemy_ai
    else:
        print(f'd{dice} + {attacker.attack} + {weapon.attack} = {dice + attacker.attack + weapon.attack}. '
              f'Target AC: {target.ac}.')
        print(f'You missed!')
        enemy_attack(target, attacker, target.weapon)  # this will be replaced with enemy_ai


def enemy_attack(attacker, target, weapon):
    dice = d20()
    if dice + attacker.attack + weapon.attack >= target.ac:
        target.hp -= weapon.damage
        print(f'The {attacker.name} attacks you with its {weapon.name} and hits you for {weapon.damage} damage!')
        if weapon.poisoned:
            target.condition = 'poisoned'
            print(f'You have been poisoned.')
    else:
        print(f'The {attacker.name} strikes back with its {weapon.name} but misses!')


def gen_enemy():
    if d20() - player_level - difficulty < 15:
        new_enemy = random.choice(enemy_types)
        enemy.append(new_enemy)  # new enemy gets added to the enemy list
        return new_enemy
        # print(f'generated enemy {len(enemy) - 1}')
        # print(f'Enemy {len(enemy) - 1} is a {enemy[-1].name} with {enemy[-1].attack} attack.')
    else:
        return 0


def gen_tile(location, chosen_path):
    if not cave_map.__contains__((location, chosen_path)):  # checks if the player has taken that path before
        new_tile = Tile(ways_out=random.randint(1, 3), trap_type=0, text_description=cave_description(), enemy=0,
                        link0=location, link1=-1, link2=-1, link3=-1, visited=False)
        # link0(back) always links to current tile

        tile.append(new_tile)                                            # new tile gets added to the tile list
        new_tile_id = len(tile) - 1                                      # newly generated tile id
                                                                         # new_tile is the tile object itself

        if chosen_path == 1:  # links current location tile to the newly generated tile by chosen_path
            tile[location].link1 = new_tile_id  # path 1 of current tile links to the newly generated tile
        elif chosen_path == 2:
            tile[location].link2 = new_tile_id  # path 2 of current tile links to the newly generated tile
        elif chosen_path == 3:
            tile[location].link3 = new_tile_id  # path 3 of current tile links to the newly generated tile

        # print(f'Generated tile{new_tile_id}. tile{location} is linked to tile{new_tile_id} by link{chosen_path}.')
        # print(f'Tile {new_tile_id} is {tile[-1].text_description}')

        tile[new_tile_id].enemy = gen_enemy()  # the newly generated tile gets a newly generated enemy
        cave_map.append((location, chosen_path))  # records that the player has chosen this path from this location
        player.location = new_tile_id  # player location gets updated to the newly generated tile
    else:
        if chosen_path == 1:  # if path was taken before, player location is updated to previously generated tile
            player.location = tile[location].link1
        elif chosen_path == 2:
            player.location = tile[location].link2
        elif chosen_path == 3:
            player.location = tile[location].link3


def gen_tile0():
    new_tile = Tile(ways_out=1, trap_type=0, text_description="a recently collapsed cave", enemy=0, link0=-1, link1=-1,
                    link2=-1, link3=-1, visited=True)     # new_tile object of class Tile gets created
    tile.append(new_tile)                   # and it gets added to the list of tiles
    print(f"""Your eyes barely open after the fall and you realize you're now underground.
Determined to get out of here, you evaluate your options.""")


def present_tile(player, tile):
    if not tile[player.location].visited:  # checks if the current tile was not visited before by the player
        print(f"""Exploring further, you find {tile[player.location].text_description}.""")
        tile[player.location].visited = True  # marks current tile as visited by the player
    elif tile[player.location].enemy == 0 and player.location == 0 and len(tile) > 1:
        print(f"You're back in that damned collapsed cave where you started.")
    elif tile[player.location].enemy == 0 and len(tile) > 1:
        print(f"You find yourself in {tile[player.location].text_description}. You recognize the place "
              f"but it gives you no comfort.")
    else:
        pass


def get_player_input(player, tile):
    if tile[player.location].enemy != 0:
        print(f'A {tile[player.location].enemy.name} faces you. You can either [A]ttack it or go [B]ack.')
    else:
        print(f'You may Res[T] here and risk being ambushed in the hope of regaining some HP.')
        if tile[player.location].ways_out == 1 and player.location != 0:
            print(f'There is a way [F]orward. You could also go [B]ack.')
        elif tile[player.location].ways_out == 1 and player.location == 0:
            print(f'You cannot go back up. The only way is [F]orward.')
        elif tile[player.location].ways_out == 2:
            print(f'You can either go [L]eft or [R]ight or [B]ack.')
        elif tile[player.location].ways_out == 3:
            print(f'You can choose to go [L]eft, [F]orward or [R]ight. Or you can turn [B]ack the way you came.')

    command = input(f'You choose to: ')

    if command.upper() == "B" and player.location != 0:
        player.location = tile[player.location].link0  # player location is updated to previous tile
    elif command.upper() == "B" and player.location == 0:
        print(f'You cannot go back up. The only way is [F]orward.')
    elif command.upper() == "L" and tile[player.location].ways_out >= 2:
        gen_tile(player.location, 1)
    elif command.upper() == "F":
        gen_tile(player.location, 2)
    elif command.upper() == "R" and tile[player.location].ways_out >= 2:
        gen_tile(player.location, 3)
    elif command.upper() == "A" and tile[player.location].enemy != 0:
        player_attack(player, tile[player.location].enemy, player.weapon)
    elif command.upper() == "T" and tile[player.location].enemy == 0:
        rest(player, tile)
    elif command.upper() == "T" and tile[player.location].enemy != 0:
        print(f'You cannot rest under the gaze of the {tile[player.location].enemy.name}!')
    else:
        print(f'Wrong command.')


def rest(player, tile):
    if random.randint(1, 10) + difficulty + player_level > 5:
        tile[player.location].enemy = gen_enemy()
        print(f'Your rest is interrupted!')
        get_player_input(player, tile)
    else:
        player.hp += 2
        if player.hp > player.max_hp:
            player.hp = player.max_hp
        print(f'You got a well-deserved rest and are now at {player.hp}/{player.max_hp} HP.')


def start_turn(player, tile):
    print("")
    check_condition(player)
    # checks if the player has moved to another tile before describing the tile
    present_tile(player, tile)
    get_player_input(player, tile)


player = player_classes[1]  # 0 ranger, 1 fighter
gen_tile0()

while True:
    if player.hp > 0:
        if len(tile) < max_tiles + player_level + difficulty or tile[player.location].enemy != 0:  # checks if reached
            # maximum no of tiles for the game and that there's no enemy on the last tile
            start_turn(player, tile)
        else:
            print(f'You have reached the end of the dungeon and can return safely to the surface!')
            break
    else:
        print(f'You are dead. Game over!')
        break
