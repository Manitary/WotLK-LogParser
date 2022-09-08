DEATHKNIGHT = 'c6'
DRUID = 'c11'
HUNTER = 'c3'
MAGE = 'c8'
PALADIN = 'c2'
PRIEST = 'c5'
ROGUE = 'c4'
SHAMAN = 'c7'
WARLOCK = 'c9'
WARRIOR = 'c1'
AURA = 'SPELL_AURA_APPLIED'
DAMAGE = 'SPELL_DAMAGE'
DAMAGEPERIODIC = 'SPELL_PERIODIC_DAMAGE'
SUMMON = 'SPELL_SUMMON'
HEAL = 'SPELL_HEAL'
HEALPERIODIC = 'SPELL_PERIODIC_HEAL'
CAST = 'SPELL_CAST_SUCCESS'

CLASS_COLOUR = {
  HUNTER: (0xFFABD473,),
  WARLOCK: (0xFF8788EE,),
  PRIEST: (0xFFFFFFFF,),
  PALADIN: (0xFFF58CBA,),
  MAGE: (0xFF3FC7EB,),
  ROGUE: (0xFFFFF569,),
  DRUID: (0xFFFF7D0A,),
  SHAMAN: (0xFF0070DE,),
  WARRIOR: (0xFFC79C6E,),
  DEATHKNIGHT: (0xFFC41F3B,),
  '': (0xFFFFFFFF,),
}

spell_spec = {
    #DK - Blood
    49016: {
        'name': 'Hysteria',
        'class': DEATHKNIGHT,
        'spec': 1,
        'type': AURA,
    },
    55233: {
        'name': 'Vampiric Blood',
        'class': DEATHKNIGHT,
        'spec': 1,
        'type': AURA,
    },
    55262: {
        'name': 'Heart Strike',
        'class': DEATHKNIGHT,
        'spec': 1,
        'type': DAMAGE,
    },
    49504: {
        'name': 'Bloody Vengeance',
        'class': DEATHKNIGHT,
        'spec': 1,
        'type': AURA,
    },
    #DK - Frost
    51271: {
        'name': 'Unbreakable Armor',
        'class': DEATHKNIGHT,
        'spec': 2,
        'type': AURA,
    },
    55268: {
        'name': 'Frost Strike',
        'class': DEATHKNIGHT,
        'spec': 2,
        'type': DAMAGE,
    },
    #DK - Unholy
    55271: {
        'name': 'Scourge Strike',
        'class': DEATHKNIGHT,
        'spec': 3,
        'type': DAMAGE,
    },
    49222: {
        'name': 'Bone Shield',
        'class': DEATHKNIGHT,
        'spec': 3,
        'type': AURA,
    },
    #Druid - Balance
    53201: {
        'name': 'Starfall',
        'class': DRUID,
        'spec': 1,
        'type': AURA,
    },
    33831: {
        'name': 'Force of Nature',
        'class': DRUID,
        'spec': 1,
        'type': SUMMON,
    },
    24907: {
        'name': 'Moonkin Aura',
        'class': DRUID,
        'spec': 1,
        'type': AURA,
    },
    #Druid - Feral (Cat)
    69369: {
        'name': 'Predatory Swiftness',
        'class': DRUID,
        'spec': 2,
        'type': AURA,
    },
    52610: {
        'name': 'Savage Roar',
        'class': DRUID,
        'spec': 2,
        'type': AURA,
    },
    62078: {
        'name': 'Swipe (Cat)',
        'class': DRUID,
        'spec': 2,
        'type': DAMAGE,
    },
    #Druid - Feral (Bear)
    5229: {
        'name': 'Enrage',
        'class': DRUID,
        'spec': 4,
        'type': AURA,
    },
    22842: {
        'name': 'Frenzied Regeneration',
        'class': DRUID,
        'spec': 4,
        'type': AURA,
    },
    48480: {
        'name': 'Maul',
        'class': DRUID,
        'spec': 4,
        'type': DAMAGE,
    },
    48562: {
        'name': 'Swipe (Bear)',
        'class': DRUID,
        'spec': 4,
        'type': DAMAGE,
    },
    #Druid - Restoration
    33891: {
        'name': 'Tree of Life',
        'class': DRUID,
        'spec': 3,
        'type': AURA,
    },
    17116: {
        'name': "Nature's Swiftness",
        'class': DRUID,
        'spec': 3,
        'type': AURA,
    },
    53251: {
        'name': 'Wild Growth',
        'class': DRUID,
        'spec': 3,
        'type': HEALPERIODIC,
    },
    #Hunter - Beast master
    19754: {
        'name': 'Bestial Wrath',
        'class': HUNTER,
        'spec': 1,
        'type': AURA,
    },
    #Hunter - Marksmanship
    53209: {
        'name': 'Chimera Shot',
        'class': HUNTER,
        'spec': 2,
        'type': DAMAGE,
    },
    34490: {
        'name': 'Silencing Shot',
        'class': HUNTER,
        'spec': 2,
        'type': DAMAGE,
    },
    #Hunter - Survival
    63672: {
        'name': 'Black Arrow',
        'class': HUNTER,
        'spec': 3,
        'type': AURA,
    },
    60053: {
        'name': 'Explosive Shot',
        'class': HUNTER,
        'spec': 3,
        'type': DAMAGE,
    },
    #Mage - Arcane
    44781: {
        'name': 'Arcane Barrage',
        'class': MAGE,
        'spec': 1,
        'type': DAMAGE,
    },
    12042: {
        'name': 'Arcane Power',
        'class': MAGE,
        'spec': 1,
        'type': AURA,
    },
    12043: {
        'name': 'Presence of Mind',
        'class': MAGE,
        'spec': 1,
        'type': AURA,
    },
    #Mage - Fire
    11129: {
        'name': 'Combustion',
        'class': MAGE,
        'spec': 2,
        'type': AURA,
    },
    55362: {
        'name': 'Living Bomb',
        'class': MAGE,
        'spec': 2,
        'type': DAMAGE,
    },
    #Mage - Frost
    43039: {
        'name': 'Ice Barrier',
        'class': MAGE,
        'spec': 3,
        'type': AURA,
    },
    44572: {
        'name': 'Deep Freeze',
        'class': MAGE,
        'spec': 3,
        'type': DAMAGE,
    },
    31687: {
        'name': 'Summon Water Elemental',
        'class': MAGE,
        'spec': 3,
        'type': CAST,
    },
    #Paladin - Holy
    53563: {
        'name': 'Beacon of Light',
        'class': PALADIN,
        'spec': 1,
        'type': AURA,
    },
    48825: {
        'name': 'Holy Shock',
        'class': PALADIN,
        'spec': 1,
        'type': HEAL,
    },
    #Paladin - Protection
    48827: {
        'name': "Avenger's Shield",
        'class': PALADIN,
        'spec': 2,
        'type': DAMAGE,
    },
    53595: {
        'name': 'Hammer of the Righteous',
        'class': PALADIN,
        'spec': 2,
        'type': DAMAGE,
    },
    48952: {
        'name': 'Holy Shield',
        'class': PALADIN,
        'spec': 2,
        'type': AURA,
    },
    #Paladin - Retribution
    35395: {
        'name': 'Crusader Strike',
        'class': PALADIN,
        'spec': 3,
        'type': DAMAGE,
    },
    53385: {
        'name': 'Divine Storm',
        'class': PALADIN,
        'spec': 3,
        'type': DAMAGE,
    },
    #Priest - Discipline
    33206: {
        'name': 'Pain Suppression',
        'class': PRIEST,
        'spec': 1,
        'type': AURA,
    },
    53007: {
        'name': 'Penance',
        'class': PRIEST,
        'spec': 1,
        'type': DAMAGE,
    },
    10060: {
        'name': 'Power Infusion',
        'class': PRIEST,
        'spec': 1,
        'type': AURA,
    },
    #Priest - Holy
    48089: {
        'name': 'Circle of Healing',
        'class': PRIEST,
        'spec': 2,
        'type': HEAL,
    },
    47788: {
        'name': 'Guardian Spirit',
        'class': PRIEST,
        'spec': 2,
        'type': HEAL,
    },
    #Priest - Shadow
    48160: {
        'name': 'Vampiric Touch',
        'class': PRIEST,
        'spec': 3,
        'type': DAMAGEPERIODIC,
    },
    47585: {
        'name': 'Dispersion',
        'class': PRIEST,
        'spec': 3,
        'type': AURA,
    },
    #Rogue - Assassination
    57993: {
        'name': 'Envenom',
        'class': ROGUE,
        'spec': 1,
        'type': DAMAGE,
    },
    51662: {
        'name': 'Hunger for Blood',
        'class': ROGUE,
        'spec': 1,
        'type': AURA,
    },
    #Rogue - Combat
    13750: {
        'name': 'Adrenaline Rush',
        'class': ROGUE,
        'spec': 2,
        'type': AURA,
    },
    51690: {
        'name': 'Blade Flurry',
        'class': ROGUE,
        'spec': 2,
        'type': DAMAGE,
    },
    #Rogue - Subtlety
    48660: {
        'name': 'Hemorrhage',
        'class': ROGUE,
        'spec': 3,
        'type': DAMAGE,
    },
    36554: {
        'name': 'Shadowstep',
        'class': ROGUE,
        'spec': 3,
        'type': AURA,
    },
    #Shaman - Elemental
    16166: {
        'name': 'Elemental Mastery',
        'class': SHAMAN,
        'spec': 1,
        'type': AURA,
    },
    59159: {
        'name': 'Thunderstorm',
        'class': SHAMAN,
        'spec': 1,
        'type': DAMAGE,
    },
    #Shaman - Enhancement
    17364: {
        'name': 'Stormstrike',
        'class': SHAMAN,
        'spec': 2,
        'type': DAMAGE,
    },
    60103: {
        'name': 'Lava Lash',
        'class': SHAMAN,
        'spec': 2,
        'type': DAMAGE,
    },
    #Shaman - Restoration
    49284: {
        'name': 'Earth Shield',
        'class': SHAMAN,
        'spec': 3,
        'type': AURA,
    },
    61301: {
        'name': 'Riptide',
        'class': SHAMAN,
        'spec': 3,
        'type': HEAL,
    },
    #Warlock - Affliction
    59164: {
        'name': 'Haunt',
        'class': WARLOCK,
        'spec': 1,
        'type': DAMAGE,
    },
    47843: {
        'name': 'Unstable Affliction',
        'class': WARLOCK,
        'spec': 1,
        'type': DAMAGEPERIODIC,
    },
    #Warlock - Demonology
    47193: {
        'name': 'Demonic Empowerment',
        'class': WARLOCK,
        'spec': 2,
        'type': AURA,
    },
    47241: {
        'name': 'Metamorphosis',
        'class': WARLOCK,
        'spec': 2,
        'type': AURA,
    },
    #Warlock - Destruction
    59172: {
        'name': 'Chaos Bolt',
        'class': WARLOCK,
        'spec': 3,
        'type': DAMAGE,
    },
    17962: {
        'name': 'Conflagrate',
        'class': WARLOCK,
        'spec': 3,
        'type': DAMAGE,
    },
    #Warrior - Arms
    46924: {
        'name': 'Bladestorm',
        'class': WARRIOR,
        'spec': 1,
        'type': AURA,
    },
    47486: {
        'name': 'Mortal Strike',
        'class': WARRIOR,
        'spec': 1,
        'type': DAMAGE,
    },
    #Warrior - Fury
    12292: {
        'name': 'Death Wish',
        'class': WARRIOR,
        'spec': 2,
        'type': DAMAGE,
    },
    12970: {
        'name': 'Flurry',
        'class': WARRIOR,
        'spec': 2,
        'type': AURA,
    },
    #Warrior - Protection
    47498: {
        'name': 'Devastate',
        'class': WARRIOR,
        'spec': 3,
        'type': DAMAGE,
    },
    50720: {
        'name': 'Vigilance',
        'class': WARRIOR,
        'spec': 3,
        'type': AURA,
    },
}

SPELL_SCHOOL = {
    1: 0xFFFFFF00,
    2: 0xFFFFE680,
    4: 0xFFFF8000,
    8: 0xFF4DFF4D,
    16: 0xFF80FFFF,
    32: 0xFF8080FF,
    64: 0xFFFF80FF,
}

def getSchools(school):
    return [school & 2**i for i in range(7)]

def getSchoolColours(school):
    return [SPELL_SCHOOL[x] for x in getSchools(school) if x > 0]
