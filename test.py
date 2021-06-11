player_sheet = """#######################
# Fighter  HP 10/10  AC 14  ATT 6  XP 0
# Steel sword equipped  DMG 4  ATT 2
# Enemies killed
# poisoned  
#######################
"""

print(f'#######################')
print(f'# {self.class_}  HP {self.hp}/{self.max_hp}  AC {self.ac}  ATT {self.attack}  XP {self.xp}')
print(f'# {self.weapon.name.capitalize()} equipped  DMG {self.weapon.damage}  ATT {self.weapon.attack_bonus}')
print(f'# Enemies killed {self.killed}')
print(f'# {self.condition.name}')
print(f'#######################')

print(player_sheet)

spider = """
      !             !
       !           !
        !  @0@0@  !     
         @u@@@@@u@
   ~~~~~@@@u@@@u@@@~~~~~~
        @@@@u@u@@@@
         @@@@@@@@@
           @@@@@


"""