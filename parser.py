from asyncio import QueueEmpty
from math import perm
import sys, os, platform
import re
from PyQt6.QtSql import QSqlDatabase, QSqlQuery
import time, datetime
from dateutil.parser import parse as timeparse
from encounters import encounter_creature, creature_encounter
from pet_recognition import permanent_pet_spells, temporary_pet_spells, pet_summon_pet
import class_recognition
import traceback

SPELL_DATA_PATH = os.path.abspath('data/spell_data.db')
APPLIED = 0
REMOVED = 1
REFRESH_START = 2
REFRESH_END = 3

def formatTimestamp(data):
    ans = str(data)
    if len(ans) > 23:
        return ans[:-3]
    elif len(ans) < 23:
        return f"{ans}.000"
    else:
        return ans

class parse:
    def __init__(self, sourceFile):
        super().__init__()
        self.sourceFile = sourceFile
        print(sourceFile)
        self.duplicate = self.generateFileName()
        self.createConnection()
        if not self.duplicate:
            self.populateDB()
            self.populateEncounters()
            self.populateActors()
            self.assignPets()
            self.populateAuras()
            self.assignSpecs()
            self.testQueries()
        self.db.close()
    
    def generateFileName(self):
        try:
            with open(self.sourceFile, "r") as f:
                timestamp = re.search(r"^(\d{1,2})\/(\d{1,2}) (\d{1,2}):(\d{1,2}):(\d{1,2})\.\d{1,3}", f.readline())
            self.year = time.localtime(os.path.getmtime(self.sourceFile)).tm_year
            self.parseFileName = f"{self.year}{''.join(timestamp.groups())}"
        except Exception as e:
            print(e)
        
        if os.path.exists(f"parses/{self.parseFileName}.db"):
        #inform that the file exists and ask the user to re-parse or not
        #if yes, continue (and wipe db), otherwise return without doing anything
            print('already exists')
            return True
        
    def createConnection(self):
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName(f"parses/{self.parseFileName}.db")
        if not self.db.open():
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
                try:
                    query.prepare(events_prepare_insert)
                    args = re.split('  |,', line.rstrip())
                    if line_num % 10000 == 0:
                        print(line_num, time.time() - start)
                        start = time.time()
                    ts = formatTimestamp(timeparse(f"{self.year}-{args[0].replace('/', '-')}"))
                    query.bindValue(":timestamp", ts)
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
                        query.bindValue(":spellSchool", int(args[10], 16))
                        i += 3
                        if suffix[0] == 'P' or suffix[0] == 'B': #PERIODIC_ | BUILDING_
                            suffix = suffix[9:]
                    elif args[1].startswith('SW'): #SWING_
                        suffix = args[1][6:]
                        query.bindValue(":spellName", 'MeleeSwing')
                        query.bindValue(":spellSchool", 1)
                    elif args[1][0] == 'R': #RANGE_
                        suffix = args[1][6:]
                        query.bindValue(":spellID", int(args[8]))
                        query.bindValue(":spellName", args[9][1:-1] if args[9] != 'nil' else None)
                        query.bindValue(":spellSchool", int(args[10], 16))
                        i += 3
                    elif args[1][0] == 'D': #DAMAGE_
                        query.bindValue(":spellID", int(args[8]))
                        query.bindValue(":spellName", args[9][1:-1] if args[9] != 'nil' else None)
                        query.bindValue(":spellSchool", int(args[10], 16))
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
                            if args[i] == 'ABSORB':
                                query.bindValue(":absorbed", args[i+1])
                            elif args[i] == 'RESIST':
                                query.bindValue(":resisted", args[i+1])
                            elif args[i] == 'BLOCK':
                                query.bindValue(":blocked", args[i+1])
                        elif suffix.startswith('DI'): #DISPEL(_)
                            query.bindValue(":extraSpellID", int(args[i]))
                            query.bindValue(":extraSpellName", args[i+1][1:-1] if args[i+1] != 'nil' else None)
                            query.bindValue(":extraSchool", int(args[i+2]))
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
                except:
                    print('Error on:',line_num,line)
                    traceback.print_exc()

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
        
        QSqlQuery("UPDATE events SET spellSchool = 32 WHERE sourceName = 'Shadowfiend' AND eventName LIKE 'SWING%'").exec()
        QSqlQuery("UPDATE events SET spellSchool = 4 WHERE sourceName = 'Greater Fire Elemental' AND eventName LIKE 'SWING%'").exec()
        print('table created')

    def testQueries(self):
        print('running test query')

    def populateActors(self):
        query = QSqlQuery()
        query.exec('DROP TABLE actors')
        with open('queries/actors.sql', 'r') as f:
            query.exec(f.read())
        encounter = QSqlQuery("SELECT timeStart, timeEnd FROM encounters")
        encounter.exec()
        players = QSqlQuery()
        players.prepare("INSERT INTO actors (unitGUID, unitName, isPlayer, encounterTime) SELECT sourceGUID, sourceName, 1, :timeStart FROM events WHERE sourceGUID LIKE '0x__0%' AND (sourceFlags LIKE '%511' OR sourceFlags LIKE '%512' OR sourceFlags LIKE '%514') AND timestamp >= :timeStart AND timestamp <= :timeEnd GROUP BY sourceGUID")
        pets = QSqlQuery()
        pets.prepare("INSERT INTO actors (unitGUID, unitName, isPet, encounterTime) SELECT sourceGUID, sourceName, 1, :timeStart FROM events WHERE (sourceGUID LIKE '0x__4%' OR (sourceGUID LIKE '0x__3%' AND (sourceFlags LIKE '%1111' OR sourceFlags LIKE '%1112' OR sourceFlags LIKE '%1114'))) AND timestamp >= :timeStart AND timestamp <= :timeEnd GROUP BY sourceGUID")
        npcs1, npcs2 = QSqlQuery(), QSqlQuery()
        npcs1.prepare("SELECT sourceGUID, sourceName FROM events WHERE sourceGUID LIKE '0x__3%' AND sourceFlags LIKE '%a48' AND timestamp >= :timeStart AND timestamp <= :timeEnd GROUP BY sourceGUID")
        npcs2.prepare("SELECT targetGUID, targetName FROM events WHERE targetGUID LIKE '0x__3%' AND targetFlags LIKE '%a48' AND timestamp >= :timeStart AND timestamp <= :timeEnd GROUP BY targetGUID")
        while encounter.next():
            t0, t1 = encounter.value(0), encounter.value(1)
            #Insert raid members
            players.bindValue(':timeStart', t0)
            players.bindValue(':timeEnd', t1)
            players.exec()
            query.prepare("SELECT unitGUID, unitName FROM actors WHERE isPlayer = 1 AND encounterTime = :timeStart")
            query.bindValue(':timeStart', t0)
            query.exec()
            player_list = {}
            while query.next():
                player_list[query.value(0)] = query.value(1)
            #Insert permanent pets
            pets.bindValue(':timeStart', t0)
            pets.bindValue(':timeEnd', t1)
            pets.exec()
            query.prepare("SELECT unitGUID, unitName FROM actors WHERE isPet = 1 AND encounterTime = :timeStart")
            query.bindValue(':timeStart', t0)
            query.exec()
            pet_list = {}
            while query.next():
                pet_list[query.value(0)] = query.value(1)
            #Insert NPCs
            NPC_list = {}
            add_npc = QSqlQuery()
            add_npc.prepare("INSERT INTO actors (unitGUID, unitName, isNPC, encounterTime) VALUES (:unitGUID, :unitName, 1, :timeStart) ON CONFLICT DO NOTHING")
            add_npc.bindValue(':timeStart', t0)
            pet_npc = QSqlQuery()
            pet_npc.prepare("UPDATE actors SET isNPC = 1 WHERE unitGUID = :unitGUID AND encounterTime = :timeStart")
            pet_npc.bindValue(':timeStart', t0)
            npcs1.bindValue(':timeStart', t0)
            npcs1.bindValue(':timeEnd', t1)
            npcs1.exec()
            while npcs1.next():
                if npcs1.value(0) not in player_list:
                    NPC_list[npcs1.value(0)] = npcs1.value(1)
                    if npcs1.value(0) in pet_list:
                        pet_npc.bindValue(":unitGUID", npcs1.value(0))
                        pet_npc.exec()
                    else:
                        add_npc.bindValue(':unitGUID', npcs1.value(0))
                        add_npc.bindValue(':unitName', npcs1.value(1))
                        add_npc.exec()
            npcs2.bindValue(':timeStart', t0)
            npcs2.bindValue(':timeEnd', t1)
            npcs2.exec()
            while npcs2.next():
                if npcs2.value(0) not in player_list and npcs2.value(0) not in NPC_list:
                    NPC_list[npcs2.value(0)] = npcs2.value(1)
                    if npcs2.value(0) in pet_list:
                        pet_npc.bindValue(":unitGUID", npcs2.value(0))
                        pet_npc.exec()
                    else:
                        add_npc.bindValue(':unitGUID', npcs2.value(0))
                        add_npc.bindValue(':unitName', npcs2.value(1))
                        add_npc.exec()

    def populateEncounters(self):
        query = QSqlQuery()
        query.exec('DROP TABLE encounters')
        with open('queries/encounters.sql', 'r') as f:
            query.exec(f.read())
        getTime = QSqlQuery()
        getTime.prepare("SELECT DISTINCT timestamp FROM events WHERE (sourceName = :unitName OR targetName = :unitName) AND (eventName LIKE '%DAMAGE' OR eventName = 'UNIT_DIED')")
        insertTime = QSqlQuery()
        insertTime.prepare("INSERT INTO encounters (unitGUID, enemy, timeStart, timeEnd, isKill) VALUES (:unitGUID, :enemy, :timeStart, :timeEnd, :isKill)")
        timediff = datetime.timedelta(seconds = 30)
        for encounter in encounter_creature:
            encounter_times = []
            encounter_GUID = ''
            query.prepare("SELECT DISTINCT CASE WHEN sourceName = :unitName THEN sourceGUID ELSE targetGUID END FROM events WHERE sourceName = :unitName OR targetName = :unitName")
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

    def assignPets(self):
        query = QSqlQuery()
        query.exec('DROP TABLE pets')
        with open('queries/pets.sql', 'r') as f:
            query.exec(f.read())

        #Permanent pets
        getOwner = QSqlQuery()
        getOwner.prepare("INSERT INTO pets (petGUID, petName, ownerGUID, ownerName) SELECT CASE WHEN s.isPlayer = 1 THEN e.targetGUID ELSE e.sourceGUID END , CASE WHEN s.isPlayer = 1 THEN e.targetName ELSE e.sourceName END, CASE WHEN s.isPlayer = 1 THEN e.sourceGUID ELSE e.targetGUID END, CASE WHEN s.isPlayer = 1 THEN e.sourceName ELSE e.targetName END FROM events e JOIN actors s ON e.sourceGUID = s.unitGUID JOIN actors t ON e.targetGUID = t.unitGUID WHERE e.eventName = :eventName AND e.spellID = :spellID AND ((s.isPet = 1 AND s.isNPC IS NULL AND t.isPlayer = 1) OR (s.isPlayer = 1 AND t.isPet = 1 AND t.isNPC IS NULL)) GROUP BY e.sourceGUID, e.targetGUID ON CONFLICT DO NOTHING")
        for spell in permanent_pet_spells:
            #Cannot bind lists -> Only check max rank spells
            getOwner.bindValue(':spellID', permanent_pet_spells[spell]['spellID'][-1])
            #Cannot bind lists -> Check all possible events individually
            for event in permanent_pet_spells[spell]['eventName']:
                getOwner.bindValue(':eventName', event)
                getOwner.exec()

        #Temporary pets
        getOwner.prepare("INSERT INTO pets (petGUID, petName, ownerGUID, ownerName) SELECT e.targetGUID, e.targetName, e.sourceGUID, e.sourceName FROM events e JOIN actors s ON e.sourceGUID = s.unitGUID JOIN actors t ON e.targetGUID = t.unitGUID WHERE e.eventName = 'SPELL_SUMMON' AND e.spellID = :spellID AND s.isPlayer = 1 AND t.isPet = 1 AND t.isNPC IS NULL GROUP BY e.sourceGUID, e.targetGUID ON CONFLICT DO NOTHING")
        for spell in temporary_pet_spells:
            #Only check max rank
            getOwner.bindValue(':spellID', temporary_pet_spells[spell][-1])
            getOwner.exec()

        #Pets summoned by other pets
        getOwner.prepare("INSERT INTO pets (petGUID, petName, ownerGUID, ownerName) SELECT e.targetGUID, e.targetName, p.ownerGUID, p.ownerName FROM events e JOIN pets p ON e.sourceGUID = p.petGUID WHERE e.eventName = 'SPELL_SUMMON' AND e.spellID = :spellID")
        for spell in pet_summon_pet:
            getOwner.bindValue(':spellID', pet_summon_pet[spell][-1])
            getOwner.exec()

        tq = QSqlQuery()
        tq.exec('SELECT ownerName, petName FROM pets GROUP BY ownerName, petName')

        #Snake trap
        t = QSqlQuery('SELECT timeStart, timeEnd from ENCOUNTERS ORDER BY timeStart')
        h = QSqlQuery()
        h.prepare("SELECT e.timestamp, sourceGUID, sourceName, spec FROM events e JOIN specs s ON e.sourceGUID = s.unitGUID WHERE eventName = 'SPELL_CREATE' AND spellID = 34600 AND e.timestamp >= :timeStart AND e.timestamp <= :timeEnd AND s.timestamp = :timeStart ORDER BY id")
        p = QSqlQuery()
        p.prepare("INSERT INTO pets (petGUID, petName, ownerGUID, ownerName) SELECT targetGUID, targetName, :ownerGUID, :ownerName FROM events WHERE eventName = 'SPELL_SUMMON' AND spellID = 57879 AND timestamp >= :timeCast AND timestamp <= :timeExpire ORDER BY id LIMIT :limit ON CONFLICT DO NOTHING")
        t.exec()
        while t.next():
            t0, t1 = t.value(0), t.value(1)
            h.bindValue(':timeStart', t0)
            h.bindValue(':timeEnd', t1)
            h.exec()
            while h.next():
                s0, unit, name, spec = h.value(0), h.value(1), h.value(2), h.value(3)
                p.bindValue(':ownerGUID', unit)
                p.bindValue(':ownerName', name)
                p.bindValue(':timeCast', s0)
                p.bindValue(':timeExpire', formatTimestamp(timeparse(s0) + datetime.timedelta(seconds = 30))[:-3])
                if spec == 'c3-3':
                    p.bindValue(':limit', 14)
                elif spec in ('c3-1', 'c3-2'):
                    p.bindValue(':limit', 8)
                p.exec()

    def assignSpecs(self):
        query = QSqlQuery()
        query.exec('DROP TABLE specs')
        with open('queries/specs.sql', 'r') as f:
            query.exec(f.read())

        getSpec = QSqlQuery()
        getSpec.prepare("INSERT INTO specs (unitGUID, timestamp, unitName, spec) VALUES (:unitGUID, :timestamp, :unitName, :spec)")

        getEncounters = QSqlQuery()
        getEncounters.exec("SELECT timeStart, timeEnd, enemy FROM encounters")

        getPlayerSpells = QSqlQuery()
        getPlayerSpells.prepare("SELECT timestamp, sourceGUID, spellID, sourceName, spellName FROM events JOIN actors ON events.sourceGUID = actors.unitGUID WHERE timestamp >= :timeStart AND timestamp <= :timeEnd AND (isPlayer = 1 or isPet = 1) AND spellID IS NOT NULL GROUP BY sourceGUID, spellID")

        while getEncounters.next():
            print('new boss')
            enemy = getEncounters.value(2)
            timeStart = getEncounters.value(0)
            timeEnd = getEncounters.value(1)
            getPlayerSpells.bindValue(':timeStart', timeStart)
            getPlayerSpells.bindValue(':timeEnd', timeEnd)
            getPlayerSpells.exec()
            while getPlayerSpells.next():
                sourceGUID = getPlayerSpells.value(1)
                spellID = getPlayerSpells.value(2)
                if spellID in class_recognition.spell_spec:
                    print(enemy, getPlayerSpells.value(3), getPlayerSpells.value(4))
                    getSpec.bindValue(':unitGUID', sourceGUID)
                    getSpec.bindValue(':timestamp', timeStart)
                    getSpec.bindValue(':unitName', getPlayerSpells.value(3))
                    getSpec.bindValue(':spec', f"{class_recognition.spell_spec[spellID]['class']}-{class_recognition.spell_spec[spellID]['spec']}")
                    getSpec.exec()

    def populateAuras(self):
        q = QSqlQuery()
        q.exec('DROP TABLE auras')
        with open('queries/auras.sql', 'r') as f:
            q.exec(f.read())
        q.prepare("ATTACH DATABASE :path AS spell_db")
        q.bindValue(':path', SPELL_DATA_PATH)
        q.exec()
        auras = QSqlQuery()
        auras.exec("SELECT DISTINCT sourceGUID, targetGUID, spellID, spellName, auraType, spellSchool FROM events WHERE eventName LIKE 'SPELL_AURA_%'")
        find = QSqlQuery()
        find.prepare("SELECT eventName, timestamp FROM events WHERE sourceGUID = :sourceGUID AND targetGUID = :targetGUID AND spellID = :spellID AND auraType = :auraType AND eventName LIKE 'SPELL_AURA_%' ORDER BY timestamp")
        duration = QSqlQuery()
        duration.prepare("SELECT duration FROM spell_db.spell_data WHERE spellID = :spellID")
        new_aura = QSqlQuery()
        new_aura.prepare("INSERT INTO auras (spellName, spellID, spellSchool, sourceGUID, targetGUID, auraType, timeStart, timeEnd, eventType) VALUES (:spellName, :spellID, :spellSchool, :sourceGUID, :targetGUID, :auraType, :timeStart, :timeEnd, :eventType)")
        try:
            while auras.next():
                sourceGUID, targetGUID, spellID, spellName, auraType, spellSchool = auras.value(0), auras.value(1), auras.value(2), auras.value(3), auras.value(4), auras.value(5)
                print(f"Current batch: {spellName} ({spellID}) - {sourceGUID} -> {targetGUID} - ({spellSchool}, {auraType})")
                duration.bindValue(':spellID', spellID)
                duration.exec()
                duration.next()
                auraDuration = duration.value(0)
                find.bindValue(':sourceGUID', sourceGUID)
                find.bindValue(':targetGUID', targetGUID)
                find.bindValue(':spellID', spellID)
                find.bindValue(':auraType', auraType)
                applied, refresh, removed = [], [], []
                find.exec()
                while find.next():
                    if find.value(0) == 'SPELL_AURA_APPLIED':
                        applied.append(find.value(1))
                    elif find.value(0) == 'SPELL_AURA_REMOVED':
                        removed.append(find.value(1))
                    elif find.value(0).startswith('SPELL_AURA_REFRESH') or find.value(0).endswith('DOSE'):
                        refresh.append(find.value(1))
                data = []
                while applied:
                    start = applied.pop(0)
                    search = True
                    while search:
                        candidates = (min((timeparse(x) for x in removed if x >= start), default = None), min((timeparse(x) for x in refresh if x >= start), default = None), (timeparse(start) + datetime.timedelta(milliseconds = auraDuration)) if auraDuration > 0 else None)
                        end = min((x for x in candidates if x), default = None)
                        if end:
                            idx = candidates.index(end)
                            end = formatTimestamp(end)
                            if idx == 0:
                                removed.remove(end)
                                search = False
                            elif idx == 1:
                                refresh.remove(end)
                            else:
                                search = False
                        else:
                            search = False
                        data.append((start, end, APPLIED))
                        start = end
                while refresh:
                    start = refresh.pop(0)
                    search = True
                    candidates = (max((timeparse(x[1]) for x in data if x[1] and x[1] <= start), default = None), (timeparse(start) - datetime.timedelta(milliseconds = auraDuration)) if auraDuration > 0 else None)
                    candidate = max((x for x in candidates if x), default = None)
                    candidate = formatTimestamp(candidate) if candidate else None
                    data.append((candidate, start, REFRESH_END))
                    while search:
                        candidates = (min((timeparse(x) for x in removed if x >= start), default = None), min((timeparse(x) for x in refresh if x >= start), default = None), (timeparse(start) + datetime.timedelta(milliseconds = auraDuration)) if auraDuration > 0 else None)
                        end = min((x for x in candidates if x), default = None)
                        if end:
                            idx = candidates.index(end)
                            end = formatTimestamp(end)
                            if idx == 0:
                                removed.remove(end)
                                search = False
                            elif idx == 1:
                                refresh.remove(end)
                            else:
                                search = False
                        else:
                            search = False
                        data.append((start, end, REFRESH_START))
                        start = end
                while removed:
                    end = removed.pop(0)
                    candidates = (max((timeparse(x[1]) for x in data if x[1] and x[1] <= end), default = None), (timeparse(end) - datetime.timedelta(milliseconds = auraDuration)) if auraDuration > 0 else None)
                    candidate = max((x for x in candidates if x), default = None)
                    candidate = formatTimestamp(candidate) if candidate else None
                    data.append((candidate, end, REMOVED))
                new_aura.bindValue(':spellName', spellName)
                new_aura.bindValue(':spellID', spellID)
                new_aura.bindValue(':sourceGUID', sourceGUID)
                new_aura.bindValue(':targetGUID', targetGUID)
                new_aura.bindValue(':auraType', auraType)
                new_aura.bindValue(':spellSchool', spellSchool)
                for x in data:
                    new_aura.bindValue(':timeStart', x[0])
                    new_aura.bindValue(':timeEnd', x[1])
                    new_aura.bindValue(':eventType', x[2])
                    new_aura.exec()
        except:
            print(f"Current batch: {spellName} - {sourceGUID} -> {targetGUID}")
            traceback.print_exc()

if __name__ == "__main__":
    parse('C:\\Users\\Manitary\\WotLK-LogParser\\logs\\WoWCombatLog.txt')
    sys.exit(0)
