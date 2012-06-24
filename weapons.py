import re, random

class Weapon(object) :
    hitMod = 0

    def __init__(self, roll) :
        foo = re.search('(\d+)d(\d+)\+?(\d*)', roll).groups()
        self.diceNum = int(foo[0])
        self.diceVal = int(foo[1])
        if foo[2] != '' : self.damMod = int(foo[2])
        else : self.damMod = 0

    def roll(self) :
        dam = 0
        for roll in range(self.diceNum) :
            dam += random.randint(1, self.diceVal)

        return dam + self.damMod

class MeleeWeapon(Weapon) :
    def __init__(self, roll) :
         Weapon.__init__(self, roll)

class RustyButterKnife(MeleeWeapon) :
    def __init__(self) :
        MeleeWeapon.__init__(self, '1d4')

class HoundClaws(MeleeWeapon) :
  def __init__(self) :
    MeleeWeapon.__init__(self, '1d6')
