import sys, os, platform
import re
from PyQt6.QtSql import QSqlDatabase, QSqlQuery
import time, datetime
from dateutil.parser import parse as timeparse
from encounters import encounter_creature, creature_encounter

class parse:
    def __init__(self, sourceFile):
        super().__init__()
        self.sourceFile = sourceFile
        self.duplicate = self.generateFileName()
        self.createConnection()
        if not self.duplicate:
            self.populateDB()
        self.populateDB()
        self.populateActors()
        self.populateEncounters()
        self.testQueries()
    
    def generateFileName(self):
        try:
            with open(self.sourceFile, "r") as f:
                timestamp = re.search(r"^(\d{1,2})\/(\d{1,2}) (\d{1,2}):(\d{1,2}):(\d{1,2})\.\d{1,3}", f.readline())
            self.year = time.localtime(os.path.getctime(self.sourceFile)).tm_year #only works in Windows
            self.parseFileName = f"{self.year}{''.join(timestamp.groups())}"
        except Exception as e:
            print(e)
        
        if os.path.exists(f"parses/{self.parseFileName}.db"):
        #inform that the file exists and ask the user to re-parse or not
        #if yes, continue (and wipe db), otherwise return without doing anything
            print('already exists')
            return True
        
    def createConnection(self):
        db = QSqlDatabase.addDatabase("QSQLITE")
        db.setDatabaseName(f"parses/{self.parseFileName}.db")
        if not db.open():
            print("Unable to open data source file.")
            sys.exit(1) # Error code 1 - signifies error

    def populateDB(self):
        query = QSqlQuery()
        query.exec("DROP TABLE events")
        with open('queries/events.sql', 'r') as f:
            query.exec(f.read().replace(' ', '\n'))
        #Event details at: https://wowpedia.fandom.com/wiki/COMBAT_LOG_EVENT#Events
        
        with open('queries/events_prepare.sql', 'r') as f:
            events_prepare_insert = f.read()
    
        with open(self.sourceFile, "r") as f:
            start = time.time()
            for line_num, line in enumerate(f.readlines()):
                query.prepare(events_prepare_insert)
                args = re.split('  |,', line.rstrip())
                if line_num % 10000 == 0:
                    print(line_num, time.time() - start)
                    start = time.time()
                query.bindValue(":timestamp", f"{self.year}-{args[0].replace('/', '-')}")
                query.bindValue(":eventName", args[1])
                query.bindValue(":sourceGUID", args[2])
                query.bindValue(":sourceName", args[3][1:-1] if args[3] != 'nil' else None)
                query.bindValue(":sourceFlags", args[4])
                query.bindValue(":targetGUID", args[5])
                query.bindValue(":targetName", args[6][1:-1] if args[6] != 'nil' else None)
                query.bindValue(":targetFlags", args[7])
                i = 8
                suffix = ''
                #parse prefix
                if args[1].startswith('SP'): #SPELL_
                    suffix = args[1][6:]
                    query.bindValue(":spellID", int(args[8]))
                    query.bindValue(":spellName", args[9][1:-1] if args[9] != 'nil' else None)
                    query.bindValue(":spellSchool", args[10])
                    i += 3
                    if suffix[0] == 'P' or suffix[0] == 'B': #PERIODIC_ | BUILDING_
                        suffix = suffix[9:]
                elif args[1].startswith('SW'): #SWING_
                    suffix = args[1][6:]
                    query.bindValue(":spellName", 'MeleeSwing')
                    query.bindValue(":spellSchool", '0x1')
                elif args[1][0] == 'R': #RANGE_
                    suffix = args[1][6:]
                    query.bindValue(":spellID", int(args[8]))
                    query.bindValue(":spellName", args[9][1:-1] if args[9] != 'nil' else None)
                    query.bindValue(":spellSchool", args[10])
                    i += 3
                elif args[1][0] == 'D': #DAMAGE_
                    query.bindValue(":spellID", int(args[8]))
                    query.bindValue(":spellName", args[9][1:-1] if args[9] != 'nil' else None)
                    query.bindValue(":spellSchool", args[10])
                    i += 3
                    if args[1].endswith('ED'): #DAMAGE_SHIELD_MISSED
                        suffix = 'MISSED'
                    else: #DAMAGE_SPLIT | DAMAGE_SHIELD
                        suffix = 'DAMAGE'
                elif args[1].startswith('ENV'): #ENVIRONMENTAL_
                    query.bindValue(":environmentalType", args[8])
                    suffix = args[1][14:]
                    i += 1
                elif args[1].startswith('ENC'): #ENCHANT_APPLIED | ENCHANT_REMOVED
                    query.bindValue(":spellName", args[8][1:-1] if args[8] != 'nil' else None)
                    query.bindValue(":itemID", int(args[9]))
                    query.bindValue(":itemName", args[10][1:-1] if args[10] != 'nil' else None)
                #parse suffix
                if suffix:
                    if suffix.startswith('DA'): #DAMAGE
                        query.bindValue(":amount", int(args[i]))
                        query.bindValue(":overkill",int(args[i+1]))
                        query.bindValue(":school", int(args[i+2]))
                        query.bindValue(":resisted", int(args[i+3]))
                        query.bindValue(":blocked", int(args[i+4]))
                        query.bindValue(":absorbed", int(args[i+5]))
                        query.bindValue(":critical", 0 if args[i+6] == 'nil' else int(args[i+6]))
                        query.bindValue(":glancing", 0 if args[i+7] == 'nil' else int(args[i+7]))
                        query.bindValue(":crushing", 0 if args[i+8] == 'nil' else int(args[i+8]))
                    elif suffix == 'HEAL': #HEAL
                        query.bindValue(":amount", int(args[i]))
                        query.bindValue(":overhealing", int(args[i+1]))
                        query.bindValue(":absorbed", int(args[i+2]))
                        query.bindValue(":critical", 0 if args[i+3] == 'nil' else int(args[i+3]))
                    elif suffix[0] == 'A': #AURA_
                        if suffix[-1] == 'E': #APPLIED_DOSE | REMOVED_DOSE
                            query.bindValue(":auraType", args[i])
                            query.bindValue(":amount", int(args[i+1]))
                        elif suffix[-1] == 'L': #BROKEN_SPELL
                            query.bindValue(":extraSpellID", int(args[i]))
                            query.bindValue(":extraSpellName", args[i+1][1:-1] if args[i+1] != 'nil' else None)
                            query.bindValue(":extraSchool", args[i+2])
                            query.bindValue(":auraType", args[i+3])
                        else: #APPLIED | REMOVED | REFRESH | BROKEN
                            query.bindValue(":auraType", args[i])
                    elif suffix.startswith('EN'): #ENERGIZE
                        query.bindValue(":amount", int(args[i]))
                        query.bindValue(":overEnergize", int(args[i+1]))
                        #query.bindValue(":powerType", args[i+2])
                        #looks like it's not needed in WotLK?
                    elif suffix[0] == 'M': #MISSED
                        query.bindValue(":missType", args[i])
                        query.bindValue(":absorbed", args[i+1])
                    elif suffix.startswith('DI'): #DISPEL(_)
                        query.bindValue(":extraSpellID", int(args[i]))
                        query.bindValue(":extraSpellName", args[i+1][1:-1] if args[i+1] != 'nil' else None)
                        query.bindValue(":extraSchool", args[i+2])
                        if suffix[-1] == 'L': #DISPEL vs DISPEL_FAILED
                            query.bindValue(":auraType", args[i+3])
                    elif suffix.startswith('INT'): #INTERRUPT
                        query.bindValue(":extraSpellID", int(args[i]))
                        query.bindValue(":extraSpellName", args[i+1][1:-1] if args[i+1] != 'nil' else None)
                        query.bindValue(":extraSchool", args[i+2])
                    elif suffix.startswith('ST'): #STOLEN
                        query.bindValue(":extraSpellID", int(args[i]))
                        query.bindValue(":extraSpellName", args[i+1][1:-1] if args[i+1] != 'nil' else None)
                        query.bindValue(":extraSchool", args[i+2])
                        query.bindValue(":auraType", args[i+3])
                    elif suffix in ('DRAIN', 'LEECH'):
                        query.bindValue(":amount", int(args[i]))
                        query.bindValue(":powerType", int(args[i+1]))
                        query.bindValue(":extraAmount", int(args[i+2]))
                    elif suffix.startswith('EX'): #EXTRA_ATTACKS
                        query.bindValue(":amount", int(args[i]))
                '''
                if args[1] in ("ENCHANT_APPLIED", "ENCHANT_REMOVED"):
                    query.bindValue(":spellName", args[8][1:-1] if args[8] != 'nil' else None)
                    query.bindValue(":itemID", int(args[9]))
                    query.bindValue(":itemName", args[10][1:-1] if args[10] != 'nil' else None)
                elif args[1] in ("UNIT_DIED", "UNIT_DESTROYED", "UNIT_DISSIPATES", "PARTY_KILL"):
                    pass
                else:
                    if args[1].startswith('ENV'): #ENVIRONMENTAL_
                    #re.search(r"^ENVIRONMENTAL_", args[1]):
                        query.bindValue(":environmentalType", args[8])
                        i += 1
                    elif args[1] in ("DAMAGE_SPLIT", "DAMAGE_SHIELD", "DAMAGE_SHIELD_MISSED") or (not re.search(r"^SWING_", args[1])):
                        query.bindValue(":spellID", int(args[8]))
                        query.bindValue(":spellName", args[9][1:-1] if args[9] != 'nil' else None)
                        query.bindValue(":spellSchool", args[10])
                        i += 3
                    #parse suffiX
                    if re.search(r"_(?:DAMAGE|SHIELD|SPLIT)$", args[1]):
                        query.bindValue(":amount", int(args[i]))
                        query.bindValue(":overkill",int(args[i+1]))
                        query.bindValue(":school", int(args[i+2]))
                        query.bindValue(":resisted", int(args[i+3]))
                        query.bindValue(":blocked", int(args[i+4]))
                        query.bindValue(":absorbed", int(args[i+5]))
                        query.bindValue(":critical", 0 if args[i+6] == 'nil' else int(args[i+6]))
                        query.bindValue(":glancing", 0 if args[i+7] == 'nil' else int(args[i+7]))
                        query.bindValue(":crushing", 0 if args[i+8] == 'nil' else int(args[i+8]))
                    elif re.search(r"_HEAL$", args[1]):
                        query.bindValue(":amount", int(args[i]))
                        query.bindValue(":overhealing", int(args[i+1]))
                        query.bindValue(":absorbed", int(args[i+2]))
                        query.bindValue(":critical", 0 if args[i+3] == 'nil' else int(args[i+3]))
                    elif re.search(r"_AURA_(?:APPLIED|REMOVED|REFRESH|BROKEN)$", args[1]):
                        query.bindValue(":auraType", args[i])
                    elif re.search(r"_AURA_(?:APPLIED_DOSE|REMOVED_DOSE)$", args[1]):
                        query.bindValue(":auraType", args[i])
                        query.bindValue(":amount", int(args[i+1]))
                    elif re.search(r"_MISSED$", args[1]):
                        query.bindValue(":missType", args[i])
                    elif re.search(r"_ENERGIZE$", args[1]):
                        query.bindValue(":amount", int(args[i]))
                        query.bindValue(":overEnergize", int(args[i+1]))
                        #query.bindValue(":powerType", args[i+2])
                        #looks like it's not needed in WotLK
                    elif re.search(r"_(?:INTERRUPT|DISPEL_FAILED)$", args[1]):
                        query.bindValue(":extraSpellID", int(args[i]))
                        query.bindValue(":extraSpellName", args[i+1][1:-1] if args[i+1] != 'nil' else None)
                        query.bindValue(":extraSchool", args[i+2])
                    elif re.search(r"_(?:DISPEL|STOLEN)$", args[1]):
                        query.bindValue(":extraSpellID", int(args[i]))
                        query.bindValue(":extraSpellName", args[i+1][1:-1] if args[i+1] != 'nil' else None)
                        query.bindValue(":extraSchool", args[i+2])
                        query.bindValue(":auraType", args[i+3])
                    elif re.search(r"_(?:DRAIN|LEECH)$", args[1]):
                        #may not be needed in WotLK
                        query.bindValue(":amount", int(args[i]))
                        query.bindValue(":powerType", int(args[i+1]))
                        query.bindValue(":extraAmount", int(args[i+2]))
                    elif re.search(r"_EXTRA_ATTACKS$", args[1]):
                        query.bindValue(":amount", int(args[i]))
                '''
                query.exec()
        print('table created')

    def testQueries(self):
        print('running test query')
        query = QSqlQuery()
        #query.exec("SELECT DISTINCT sourceGUID, sourceName FROM events")
        #query.exec("SELECT sourceName, SUM(amount) AS dmg FROM events WHERE (eventName = 'SWING_DAMAGE' or eventName = 'SPELL_DAMAGE' or eventName = 'SPELL_PERIODIC_DAMAGE') AND (targetName = 'Patchwerk') GROUP BY sourceName ORDER BY dmg DESC")
        #with open('test_query.sql', 'r') as f:
        #    query.exec(f.read())
        #query.exec("SELECT sourceGUID, sourceName, sourceFlags FROM events WHERE sourceFlags = '0x1114' GROUP BY sourceGUID ")
        #query.exec("SELECT COUNT(critical) FROM events WHERE eventName = 'SWING_DAMAGE' AND sourceName = 'Watary' LIMIT 10")
        #query.exec("SELECT id, unitGUID, enemy, timeStart, timeEnd, isKill FROM encounters")
        query.exec("SELECT * FROM events WHERE spellName = 'Hymn of Hope'")
        print('test query done')
        while (query.next()):
            #print(query.value(0), query.value(1), query.value(2), query.value(3), query.value(4), query.value(5))
            print([query.value(i) for i in range(30)])


    def populateActors(self):
        query = QSqlQuery()
        query.exec('DROP TABLE actors')
        with open('queries/actors.sql', 'r') as f:
            query.exec(f.read())
        #Insert raid members
        query.exec("INSERT INTO actors (unitGUID, unitName, isPlayer) SELECT sourceGUID, sourceName, 1 FROM events WHERE sourceGUID LIKE '0x__0%' AND (sourceFlags LIKE '%511' OR sourceFlags LIKE '%512' OR sourceFlags LIKE '%514') GROUP BY sourceGUID")
        query.exec("SELECT unitGUID, unitName FROM actors WHERE isPlayer = 1")
        player_list = {}
        while (query.next()):
            player_list[query.value(0)] = query.value(1)
        #Insert permanent pets
        query.exec("INSERT INTO actors (unitGUID, unitName, isPet) SELECT sourceGUID, sourceName, 1 FROM events WHERE sourceGUID LIKE '0x__4%' GROUP BY sourceGUID")
        #Insert summoned pets
        query.exec("INSERT INTO actors (unitGUID, unitName, isPet) SELECT sourceGUID, sourceName, 1 FROM events WHERE sourceGUID LIKE '0x__3%' AND (sourceFlags LIKE '%1111' OR sourceFlags LIKE '%1112' OR sourceFlags LIKE '%1114') GROUP BY sourceGUID")
        query.exec("SELECT unitGUID, unitName FROM actors WHERE isPet = 1")
        pet_list = {}
        while (query.next()):
            pet_list[query.value(0)] = query.value(1)
        #Insert NPCs
        query.exec("SELECT sourceGUID, sourceName, 1 FROM events WHERE sourceGUID LIKE '0x__3%' AND sourceFlags LIKE '%a48' GROUP BY sourceGUID")
        NPC_list = {}
        add_npc = QSqlQuery()
        add_npc.prepare("INSERT INTO actors (unitGUID, unitName, isNPC) VALUES (:unitGUID, :unitName, 1)")
        pet_npc = QSqlQuery()
        pet_npc.prepare("UPDATE actors SET isNPC = 1 WHERE unitGUID = :unitGUID")
        while (query.next()):
            NPC_list[query.value(0)] = query.value(1)
            if query.value(0) not in player_list:
                if query.value(0) in pet_list:
                    pet_npc.bindValue(":unitGUID", query.value(0))
                    pet_npc.exec()
                else:
                    add_npc.bindValue(':unitGUID', query.value(0))
                    add_npc.bindValue(':unitName', query.value(1))
                    add_npc.exec()
        '''
        query.exec("SELECT unitGUID, unitName, isPet, isNPC FROM actors WHERE isPet = 1 GROUP BY unitName")
        while (query.next()):
            print(query.value(0), query.value(1), query.value(2), query.value(3))
        '''

    def populateEncounters(self):
        query = QSqlQuery()
        query.exec('DROP TABLE encounters')
        with open('queries/encounters.sql', 'r') as f:
            query.exec(f.read())
        getTime = QSqlQuery()
        getTime.prepare("SELECT DISTINCT timestamp FROM events WHERE (sourceName = :unitName OR targetName = :unitName) AND eventName LIKE '%DAMAGE' OR eventName = 'UNIT_DIED'")
        insertTime = QSqlQuery()
        insertTime.prepare("INSERT INTO encounters (unitGUID, enemy, timeStart, timeEnd, isKill) VALUES (:unitGUID, :enemy, :timeStart, :timeEnd, :isKill)")
        timediff = datetime.timedelta(seconds = 30)
        for encounter in encounter_creature:
            encounter_times = []
            encounter_GUID = ''
            query.prepare("SELECT unitGUID FROM actors WHERE unitName = :unitName")
            query.bindValue(":unitName", encounter_creature[encounter][0])
            query.exec()
            while (query.next()):
                encounter_GUID = query.value(0)
            if encounter_GUID:
                for creature in encounter_creature[encounter]:
                    getTime.bindValue(':unitName', creature)
                    getTime.exec()
                    while (getTime.next()):
                        encounter_times.append(getTime.value(0))
                if encounter_times:
                    encounter_times.sort()
                    encounter_start = [encounter_times[0]]
                    encounter_end = []
                    old_time = encounter_start[0]
                    for i in range(1, len(encounter_times)):
                        new_time = encounter_times[i]
                        if timeparse(new_time) - timeparse(old_time) > timediff:
                            encounter_start.append(new_time)
                            encounter_end.append(old_time)
                        old_time = new_time
                    encounter_end.append(encounter_times[-1])
                    for i in range(len(encounter_start)):
                        isKill = 1 if i == len(encounter_start) - 1 else 0
                        insertTime.bindValue(":unitGUID", encounter_GUID)
                        insertTime.bindValue(":enemy", encounter)
                        insertTime.bindValue(":timeStart", encounter_start[i])
                        insertTime.bindValue(":timeEnd", encounter_end[i])
                        insertTime.bindValue(":isKill", isKill)
                        insertTime.exec()

if __name__ == "__main__":
    parse()
    sys.exit(0)
