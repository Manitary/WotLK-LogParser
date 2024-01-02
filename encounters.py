encounter_creature = {
    "Thaddius": (
        "Thaddius",
        "Stalagg",
        "Feugen",
    ),
    "Grobbulus": ("Grobbulus",),
    "Gluth": ("Gluth",),
    "Heigan the Unclean": ("Heigan the Unclean",),
    "Maexxna": ("Maexxna",),
    "Grand Widow Faerlina": ("Grand Widow Faerlina",),
    "Noth the Plaguebringer": (
        "Noth the Plaguebringer",
        "Plagued Warrior",
        "Plagued Champion",
        "Plagued Guardian",
    ),
    "Anub'Rekhan": (
        "Anub'Rekhan",
        "Crypt Guard",
    ),
    "Sapphiron": ("Sapphiron",),
    "Loatheb": ("Loatheb",),
    "Patchwerk": ("Patchwerk",),
    "Gothik the Harvester": (
        "Gothik the Harvester",
        "Unrelenting Trainee",
        "Unrelenting Death Knight",
        "Unrelenting Rider",
        "Spectral Trainee",
        "Spectral Death Knight",
        "Spectral Rider",
        "Spectral Horse",
    ),
    "Instructor Razuvious": ("Instructor Razuvious", "Death Knight Understudy"),
    "The Four Horsemen": (
        "Baron Rivendare",
        "Thane Korth'azz",
        "Sir Zeliek",
        "Lady Blaumeux",
    ),
    "Kel'Thuzad": (
        "Kel'Thuzad",
        "Soldier of the Frozen Wastes",
        "Unstoppable Abomination",
        "Soul Weaver",
    ),
}

creature_encounter = {}
for encounter in encounter_creature:
    for creature in encounter_creature[encounter]:
        creature_encounter[creature] = encounter
