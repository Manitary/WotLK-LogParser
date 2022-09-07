import sys, os, re
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox, QFileDialog, QComboBox, QLabel, QVBoxLayout, QWidget, QTableView, QHBoxLayout, QAbstractItemView, QPushButton, QAbstractItemDelegate, QStyledItemDelegate, QHeaderView, QDialog
from PyQt6.QtGui import QAction, QFont, QPixmap, QBrush, QLinearGradient, QIcon, QStandardItemModel, QStandardItem
from PyQt6.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel
from PyQt6.QtCore import Qt, QRectF, QEvent, QPoint, QSize
import pyqtgraph as pg
from tools import flattenIntervals, plotAuras
import time, datetime
from dateutil.parser import parse as timeparse
import zipfile, rarfile
import parser, pet_recognition, class_recognition

ALL = "AllUnits"
ALL_AURAS = "All auras"
FRIENDLY = "Friendlies"
HOSTILE = "Enemies"
AFFILIATION = [HOSTILE, FRIENDLY]
GAINED = "gained"
APPLIED = "given"
DIRECTION = [GAINED, APPLIED]
DAMAGEDONE = "Damage Done"
DAMAGETAKEN = "Damage Taken"
HEALING = "Healing"
DEATHS = "Deaths"
BUFFS = "Buffs"
DEBUFFS = "Debuffs"
METERS = [DAMAGEDONE, DAMAGETAKEN, HEALING, DEATHS, BUFFS, DEBUFFS]
SPELL_DATA_PATH = os.path.abspath('data/spell_data.db')
EVERYONE = True
ICON = 'icon'
SCHOOL = 'school'
HERO = 'spec'
SPELL = 'spell'
TYPE = 'type'
BAR = 'bar'
HIDE = 'hide'
SPELL_INFO = 'spellInfo'
INFO = 'other'
COLUMNS = {
    DAMAGEDONE: {
        EVERYONE: {
            -1: {TYPE: HERO, BAR: 2, HERO: 5, HIDE: 5},
            0: {TYPE: HERO, BAR: 2, HERO: 4, HIDE: 4},
            2: {TYPE: SPELL, BAR: 2, ICON: 4, SCHOOL: 5, HIDE: 4},
        },
        not EVERYONE: {
            -1: {TYPE: SPELL, BAR: 2, ICON: 11, SCHOOL: 12, HIDE: 11},
            0: {TYPE: HERO, BAR: 2, HERO: 4, HIDE: 4},
            2: {TYPE: SPELL_INFO, BAR: 2, SCHOOL: 7, HIDE: 7},
            6: {TYPE: SPELL_INFO, BAR: 2, SCHOOL: 4, HIDE: 4},
        },
    },
    DAMAGETAKEN: {
        EVERYONE: {
            -1: {TYPE: HERO, BAR: 2, HERO: 6, HIDE: 6},
            0: {TYPE: HERO, BAR: 2, HERO: 4, HIDE: 4},
            2: {TYPE: SPELL, BAR: 2, ICON: 4, SCHOOL: 5, HIDE: 4},
            5: {TYPE: INFO, BAR: 2, HIDE: 4}
        },
        not EVERYONE: {
            -1: {TYPE: SPELL, BAR: 2, ICON: 9, SCHOOL: 10, HIDE: 9},
            0: {TYPE: HERO, BAR: 2, HERO: 4, HIDE: 4},
            2: {TYPE: SPELL_INFO, BAR: 2, SCHOOL: 7, HIDE: 7},
            5: {TYPE: SPELL_INFO, BAR: 2, SCHOOL: 4, HIDE: 4}
        },
    },
    HEALING: {
        EVERYONE: {
            -1: {BAR: 2, ICON: 7, HERO: 7, HIDE: 7},
            2: {},
        },
        not EVERYONE: {
            -1: {BAR: 2, ICON: 8, SCHOOL: 9, HIDE: 8},
            2: {},
        },
    },
}
BAR_OFFSET_X = 5
BAR_OFFSET_Y = 6
PATH_HERO = lambda icon: f"wow_hero_classes/{icon}.png" if icon else ''
PATH_SPELL = lambda icon: f"wow_icon/{icon.lower()}.jpg" if icon else ''
MELEE = 'MeleeSwing'
MELEE_ICON = 'inv_axe_01'

style_sheet = '''
QTableView {
    background-color: black;
    alternate-background-color: #161616;
    gridline-color: #515151;
    color: white;
}
'''

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initializeUI()

    def initializeUI(self):
        self.setMinimumSize(1000, 400)
        self.setWindowTitle("Parser")
        self.createActions()
        self.createMenu()
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.main_vbox = QVBoxLayout(self.centralWidget)
        self.file_name = None
        self.setUpMainWindow()
        self.direction_swap_button.hide()
        self.spell_clear_button.hide()
        self.spell_select.hide()
        self.graph.hide()
        self.show()

    def createActions(self):
        self.quit_act = QAction("Quit")
        self.quit_act.triggered.connect(self.close)
        self.parse_act = QAction("Parse a log")
        self.parse_act.triggered.connect(self.parseFile)
        self.open_act = QAction("Open a parse")
        self.open_act.triggered.connect(self.openParse)
        self.pet_pairing_act = QAction("Edit players' pets")
        self.pet_pairing_act.triggered.connect(self.editPetsOwners)

    def createMenu(self):
        self.menuBar().setNativeMenuBar(False)
        file_menu = self.menuBar().addMenu("File")
        file_menu.addAction(self.open_act)
        file_menu.addAction(self.parse_act)
        #file_menu.addAction(self.quit_act)
        tools_menu = self.menuBar().addMenu("Tools")
        tools_menu.addAction(self.pet_pairing_act)

    def parseFile(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select log file", "logs/", "Text Files (*.txt);; Archive (*.rar; *.zip)")
        if file_name.endswith(".txt"):
            try:
                parser.parse(file_name)
                print('parse done')
            except Exception as e:
                print(e)
        #Decide how to deal with archives later
        '''
        elif file_name.endswith(".zip"):
            try:
                log_file = zipfile.ZipFile(file_name, 'r').read("WoWCombatLog.txt")
                parser.parse(log_file, file_name)
                print('done')
            except:
                print('error')
        elif file_name.endswith(".rar"):
            archive = rarfile.RarFile(file_name, "r")
            for log_file in [f for f in archive.namelist() if f.endswith(".txt")]:
                try:
                    parser.parse(log_file)
                    print('done')
                except:
                    print('error')
        '''

    def openParse(self):
        self.file_name, _ = QFileDialog.getOpenFileName(self, "Select parse", "parses/", "Databases (*.db)")
        if self.file_name:
            DB.setDatabaseName(self.file_name)
            if not DB.open():
                print("Unable to open data source file.")
                sys.exit(1)
            tables_needed = {"events", "encounters", "actors"}
            tables_not_found = tables_needed - set(DB.tables())
            if tables_not_found:
                QMessageBox.critical(None, "Error", f"<p>The following tables are missing from the database: {tables_not_found}</p>")
                sys.exit(1)
            self.setUpParse()

    def setUpMainWindow(self):
        self.create_pet_editing_window = None
        self.encounter_select = QComboBox()
        self.meter_select = QComboBox()
        self.meter_select.addItems(METERS)

        self.source_select = QComboBox()
        self.target_select = QComboBox()
        self.source_clear_button = QPushButton("X", self)
        self.source_clear_button.setMaximumSize(24, 24)
        self.source_clear_button.clicked.connect(self.resetSourceSelection)
        self.target_clear_button = QPushButton("X", self)
        self.target_clear_button.setMaximumSize(24, 24)
        self.target_clear_button.clicked.connect(self.resetTargetSelection)
        self.actors_swap_button = QPushButton(self)
        self.actors_swap_button.setMaximumSize(75, 24)
        self.actors_swap_button.clicked.connect(self.swapAffiliation)

        self.direction_swap_button = QPushButton(self)
        self.direction_swap_button.setMaximumSize(75, 24)
        self.direction_swap_button.clicked.connect(self.swapDirection)
        self.spell_clear_button = QPushButton("X", self)
        self.spell_clear_button.setMaximumSize(24, 24)
        self.spell_clear_button.clicked.connect(self.resetSpellSelection)
        self.spell_select = QComboBox()
        self.spell_select.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)

        self.meter = ''
        self.everyone = True
        self.everyoneTarget = True
        self.affiliation = 1

        self.graph = pg.PlotWidget()
        self.table = tooltipTable()
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.clicked.connect(self.tableClicked)

        self.encounter_select.currentTextChanged.connect(self.updateUnitList)
        self.meter_select.currentTextChanged.connect(self.updateUnitList)
        self.source_select.currentTextChanged.connect(self.updateMainQuery)
        self.target_select.currentTextChanged.connect(self.updateMainQuery)
        self.spell_select.currentIndexChanged.connect(self.updateMainQuery)

        self.model = QSqlTableModel() #to be removed

        self.main_vbox.addWidget(self.encounter_select)
        self.main_vbox.addWidget(self.meter_select)
        self.actors_hbox = QHBoxLayout()
        self.actors_hbox.addWidget(self.source_clear_button)
        self.actors_hbox.addWidget(self.source_select)
        self.actors_hbox.addWidget(self.actors_swap_button)
        self.actors_hbox.addWidget(self.target_select)
        self.actors_hbox.addWidget(self.target_clear_button)
        self.main_vbox.addLayout(self.actors_hbox)
        self.extra_hbox = QHBoxLayout()
        self.extra_hbox.addWidget(self.direction_swap_button)
        self.extra_hbox.addWidget(self.spell_clear_button)
        self.extra_hbox.addWidget(self.spell_select)
        self.main_vbox.addLayout(self.extra_hbox)
        self.main_vbox.addWidget(self.graph)
        self.main_vbox.addWidget(self.table)

    def setUpParse(self):
        QSqlQuery(f"ATTACH DATABASE '{SPELL_DATA_PATH}' AS spell_db").exec()

        self.encounter_select.blockSignals(True)
        self.meter_select.blockSignals(True)
        self.source_select.blockSignals(True)
        self.target_select.blockSignals(True)
        self.spell_select.blockSignals(True)
        self.encounter_select.clear()
        self.source_select.clear()
        self.target_select.clear()
        self.spell_select.clear()

        encounter_query = QSqlQuery("SELECT enemy, timeStart, timeEnd, isKill FROM encounters ORDER BY timeStart")
        encounter_query.exec()
        while encounter_query.next():
            self.encounter_select.addItem(f"{encounter_query.value(0)} ({'kill' if encounter_query.value(3) else 'wipe'}) - {encounter_query.value(1)} | {encounter_query.value(2)}", (encounter_query.value(1), encounter_query.value(2)))
        self.source_current = FRIENDLY
        self.target_current = HOSTILE
        self.source_affiliation = 1
        self.target_affiliation = 0
        self.actors_swap_button.setText(AFFILIATION[self.source_affiliation])
        self.direction = 0
        self.direction_swap_button.setText(DIRECTION[self.direction])
        self.spell_current = ALL_AURAS
        self.spell_select.addItem(self.spell_current)
        self.spell_select.setCurrentIndex(0)

        self.encounter_select.blockSignals(False)
        self.meter_select.blockSignals(False)
        self.source_select.blockSignals(False)
        self.target_select.blockSignals(False)
        self.spell_select.blockSignals(False)

        self.updateUnitList()
        print('setup done')

    def updateMainQuery(self):
        self.updateStatus()
        self.direction_swap_button.hide()
        self.spell_clear_button.hide()
        self.spell_select.hide()
        self.graph.hide()
        self.table.setModel(self.model)
        if self.meter == DAMAGEDONE:
            self.queryDamage()
        elif self.meter == DAMAGETAKEN:
            self.queryDamage()
        elif self.meter == HEALING:
            self.queryHealing()
        elif self.meter == DEATHS:
            self.queryDeaths()
        elif self.meter in (BUFFS, DEBUFFS):
            self.spell_select.blockSignals(True)
            self.populateAuraSelector()
            self.spell_select.blockSignals(False)
            if self.spell_select.currentIndex() <= 0:
                self.spell_select.blockSignals(True)
                self.queryBuffs()
                self.spell_select.blockSignals(False)
            elif self.spell_select.currentIndex() > 0:
                self.querySingleBuff()
        else:
            self.display_query = QSqlQuery()
            self.model.setQuery(self.display_query)
        print('query done')

    def queryDamage(self):
        display_query = QSqlQuery()
        with open(getPath(self.meter, self.everyone, self.everyoneTarget), 'r') as f:
            display_query.prepare(f.read())
        display_query.bindValue(":affiliation", self.source_affiliation)
        if self.meter == DAMAGEDONE:
            display_query.bindValue(":sourceName", self.source_select.currentText())
            display_query.bindValue(":targetName", self.target_select.currentText())
        elif self.meter == DAMAGETAKEN:
            display_query.bindValue(":sourceName", self.target_select.currentText())
            display_query.bindValue(":targetName", self.source_select.currentText())
        display_query.bindValue(":startTime", self.startTime)
        display_query.bindValue(":endTime", self.endTime)
        print(display_query.exec())
        self.table.setItemDelegateForColumn(COLUMNS[self.meter][self.everyone][-1][BAR], DELEGATES[self.meter][self.everyone])
        self.table.setModel(meterSqlTableModel(display_query, self.meter, self.everyone))
        for i in range(COLUMNS[self.meter][self.everyone][-1][HIDE], self.table.horizontalHeader().count()):
            self.table.hideColumn(i)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(COLUMNS[self.meter][self.everyone][-1][BAR], QHeaderView.ResizeMode.Stretch)

    def queryDamageDone(self):
        display_query = QSqlQuery()
        with open(getPath(self.meter, self.everyone, self.everyoneTarget), 'r') as f:
            display_query.prepare(f.read())
        display_query.bindValue(":affiliation", self.source_affiliation)
        display_query.bindValue(":sourceName", self.source_select.currentText())
        display_query.bindValue(":targetName", self.target_select.currentText())
        display_query.bindValue(":startTime", self.startTime)
        display_query.bindValue(":endTime", self.endTime)
        display_query.exec()
        self.table.setItemDelegateForColumn(COLUMNS[self.meter][self.everyone][-1][BAR], DELEGATES[self.meter][self.everyone])
        self.table.setModel(meterSqlTableModel(display_query, self.meter, self.everyone))
        for i in range(COLUMNS[self.meter][self.everyone][-1][HIDE], self.table.horizontalHeader().count()):
            self.table.hideColumn(i)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(COLUMNS[self.meter][self.everyone][-1][BAR], QHeaderView.ResizeMode.Stretch)

    def queryDamageTaken(self):
        display_query = QSqlQuery()
        with open(getPath(self.meter, self.everyone, self.everyoneTarget), 'r') as f:
            display_query.prepare(f.read())
        display_query.bindValue(":affiliation", self.source_affiliation)
        display_query.bindValue(":sourceName", self.target_select.currentText())
        display_query.bindValue(":targetName", self.source_select.currentText())
        display_query.bindValue(":startTime", self.startTime)
        display_query.bindValue(":endTime", self.endTime)
        display_query.exec()
        self.table.setItemDelegateForColumn(COLUMNS[self.meter][self.everyone][-1][BAR], DELEGATES[self.meter][self.everyone])
        self.table.setModel(meterSqlTableModel(display_query, self.meter, self.everyone))
        for i in range(COLUMNS[self.meter][self.everyone][-1][HIDE], self.table.horizontalHeader().count()):
            self.table.hideColumn(i)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(COLUMNS[self.meter][self.everyone][-1][BAR], QHeaderView.ResizeMode.Stretch)

    def queryHealing(self):
        display_query = QSqlQuery()
        if self.everyone:
            if self.target_select.currentData() == AFFILIATION[self.source_affiliation]:
                with open('queries/healing_done_all-all.sql', 'r') as f:
                    display_query.prepare(f.read())
            else:
                with open('queries/healing_done_all-1.sql', 'r') as f:
                    display_query.prepare(f.read())
                display_query.bindValue(":targetName", self.target_select.currentText())
            display_query.bindValue(":affiliation", self.source_affiliation)
        else:
            if self.target_select.currentData() == AFFILIATION[self.source_affiliation]:
                with open('queries/healing_done_1-all.sql', 'r') as f:
                    display_query.prepare(f.read())
            else:
                with open('queries/healing_done_1-1.sql', 'r') as f:
                    display_query.prepare(f.read())
                display_query.bindValue(":targetName", self.target_select.currentText())
            display_query.bindValue(":sourceName", self.source_select.currentText())
        display_query.bindValue(":startTime", self.startTime)
        display_query.bindValue(":endTime", self.endTime)
        display_query.exec()
        self.table.setItemDelegateForColumn(2, DELEGATES[self.meter][self.everyone])
        self.table.setModel(meterSqlTableModel(display_query, self.meter, self.everyone))
        for i in range(COLUMNS[self.meter][self.everyone][-1][HIDE], self.table.horizontalHeader().count()):
            self.table.hideColumn(i)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)

    def queryDeaths(self, timestamp = None, unitName = None):
        self.table.setItemDelegateForColumn(2, QStyledItemDelegate())
        display_query = QSqlQuery()
        if timestamp and unitName:
            with open('queries/deaths_recap.sql', 'r') as f:
                display_query.prepare(f.read())
            display_query.bindValue(":targetName", unitName)
            display_query.bindValue(":endTime", timestamp)
            display_query.bindValue(":startTime", self.startTime)
            display_query.exec()
            self.table.setModel(deathRecapSqlTableModel(display_query))
            for i in range(4, self.table.horizontalHeader().count()):
                self.table.hideColumn(i)
            self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        elif self.everyone:
            with open('queries/deaths_all.sql', 'r') as f:
                display_query.prepare(f.read())
            display_query.bindValue(":affiliation", self.source_affiliation)
            display_query.bindValue(":endTime", self.endTime)
            display_query.bindValue(":startTime", self.startTime)
            display_query.exec()
            self.table.setModel(deathSqlTableModel(display_query))
            for i in range(5, self.table.horizontalHeader().count()):
                self.table.hideColumn(i)
            self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        else:
            with open('queries/deaths_1.sql', 'r') as f:
                display_query.prepare(f.read())
            display_query.bindValue(":affiliation", self.source_affiliation)
            display_query.bindValue(":endTime", self.endTime)
            display_query.bindValue(":startTime", self.startTime)
            display_query.bindValue(":targetGUID", self.source_select.currentData()[1])
            display_query.exec()
            self.table.setModel(deathSqlTableModel(display_query))
            for i in range(5, self.table.horizontalHeader().count()):
                self.table.hideColumn(i)
            self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

    def queryBuffs(self):
        self.direction_swap_button.show()
        self.spell_clear_button.show()
        self.spell_select.show()
        self.table.setItemDelegateForColumn(2, auraDelegate())
        auraType = 'BUFF' if self.meter == BUFFS else 'DEBUFF'
        direction = APPLIED if self.direction else GAINED
        q = QSqlQuery()
        if self.everyone:
            if self.target_select.currentData() == AFFILIATION[self.source_affiliation if self.meter == BUFFS else 1 - self.source_affiliation]:
                with open(f"queries/buffs_{direction}_all-all.sql", 'r') as f:
                    q.prepare(f.read())
            else:
                with open(f"queries/buffs_{direction}_all-1.sql", 'r') as f:
                    q.prepare(f.read())
                q.bindValue(':sourceGUID', self.target_select.currentData()[1])
            q.bindValue(":affiliation", self.source_affiliation)
        else:
            if self.target_select.currentData() == AFFILIATION[self.source_affiliation if self.meter == BUFFS else 1 - self.source_affiliation]:
                with open(f"queries/buffs_{direction}_1-all.sql", 'r') as f:
                    q.prepare(f.read())
            else:
                with open(f"queries/buffs_{direction}_1-1.sql", 'r') as f:
                    q.prepare(f.read())
                q.bindValue(':sourceGUID', self.target_select.currentData()[1])
            q.bindValue(":targetGUID", self.source_select.currentData()[1])
        q.bindValue(":startTime", self.startTime)
        q.bindValue(":endTime", self.endTime)
        q.bindValue(":auraType", auraType)
        q.exec()
        for k in self.auras_current:
            self.auras_current[k]['intervals'] = []
        while q.next():
            self.auras_current[q.value(1)]['intervals'].append((q.value(2), q.value(3)))
        t0 = timeparse(self.startTime)
        encounter_length = timeparse(self.endTime) - t0
        q.exec("DROP TABLE IF EXISTS temp_buff")
        q.exec("CREATE TEMP TABLE temp_buff (spellID MEDIUMINT UNSIGNED UNIQUE NOT NULL, spellName VARCHAR(50), count SMALLINT UNSIGNED, uptime TIMESTAMP, uptimepct FLOAT, intervals VARCHAR, maxlen FLOAT, spellSchool TINYINT UNSIGNED, icon VARCHAR(50))")
        q.prepare("INSERT INTO temp_buff (spellID, spellName, count, uptime, uptimepct, intervals, maxlen, spellSchool, icon) VALUES (:spellID, :spellName, :count, :uptime, :uptimepct, :intervals, :maxlen, :spellSchool, :icon)")
        q.bindValue(':maxlen', encounter_length.total_seconds())
        for k in self.auras_current:
            self.auras_current[k]['count'] = len(self.auras_current[k]['intervals'])
            self.auras_current[k]['intervals'] = flattenIntervals(self.auras_current[k]['intervals'])
            self.auras_current[k]['intervals'] = [(timeparse(x[0]), timeparse(x[1])) for x in self.auras_current[k]['intervals']]
            uptime = datetime.timedelta()
            for x in self.auras_current[k]['intervals']:
                uptime += x[1] - x[0]
            self.auras_current[k]['uptime'] = uptime
            self.auras_current[k]['uptimepct'] = uptime / encounter_length * 100
            self.auras_current[k]['intervals'] = [((x[0] - t0).total_seconds(), (x[1] - t0).total_seconds()) for x in self.auras_current[k]['intervals']]
            q.bindValue(':spellID', k)
            q.bindValue(':spellName', self.auras_current[k]['spellName'])
            q.bindValue(':count', self.auras_current[k]['count'])
            q.bindValue(':uptime', str(self.auras_current[k]['uptime']))
            q.bindValue(':uptimepct', self.auras_current[k]['uptimepct'])
            q.bindValue(':intervals', f"{self.auras_current[k]['intervals']}")
            q.bindValue(':spellSchool', self.auras_current[k]['school'])
            q.bindValue(':icon', self.auras_current[k]['icon'])
            q.exec()
        display_query = QSqlQuery()
        display_query.exec("SELECT spellName, PRINTF('%.2f%%', uptimepct) AS pct, intervals, count, uptime, spellID, maxlen, spellSchool, icon FROM temp_buff ORDER BY uptime DESC, spellName")
        self.table.setModel(auraSqlTableModel(display_query))
        for i in range(4, self.table.horizontalHeader().count()):
            self.table.hideColumn(i)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)

    def querySingleBuff(self):
        self.direction_swap_button.show()
        self.spell_clear_button.show()
        self.spell_select.show()
        self.table.setItemDelegateForColumn(2, auraDelegate(False))
        auraType = 'BUFF' if self.meter == BUFFS else 'DEBUFF'
        spellID = int(self.spell_select.model().data(self.spell_select.model().index(self.spell_select.currentIndex(), 1)))
        direction = APPLIED if self.direction else GAINED
        q = QSqlQuery()
        if self.everyone:
            if self.target_select.currentData() == AFFILIATION[self.source_affiliation if self.meter == BUFFS else 1 - self.source_affiliation]:
                with open(f"queries/buff_{direction}_all-all.sql", 'r') as f:
                    q.prepare(f.read())
            else:
                with open(f"queries/buff_{direction}_all-1.sql", 'r') as f:
                    q.prepare(f.read())
                q.bindValue(':sourceGUID', self.target_select.currentData()[1])
            q.bindValue(":affiliation", self.source_affiliation)
        else:
            if self.target_select.currentData() == AFFILIATION[self.source_affiliation if self.meter == BUFFS else 1 - self.source_affiliation]:
                with open(f"queries/buff_{direction}_1-all.sql", 'r') as f:
                    q.prepare(f.read())
            else:
                with open(f"queries/buff_{direction}_1-1.sql", 'r') as f:
                    q.prepare(f.read())
                q.bindValue(':sourceGUID', self.target_select.currentData()[1])
            q.bindValue(":targetGUID", self.source_select.currentData()[1])
        q.bindValue(":startTime", self.startTime)
        q.bindValue(":endTime", self.endTime)
        q.bindValue(":auraType", auraType)
        q.bindValue(":spellID", spellID)
        q.exec()
        self.aura_current = {}
        while q.next():
            sourceGUID, targetGUID, t0, t1 = q.value(0), q.value(1), q.value(2), q.value(3)
            if (self.everyone and not self.direction) or (not self.everyone and self.direction):
                if targetGUID not in self.aura_current:
                    self.aura_current[targetGUID] = {'sourceGUID': sourceGUID, 'intervals': []}
                self.aura_current[targetGUID]['intervals'].append((t0, t1))
            else:
                if sourceGUID not in self.aura_current:
                    self.aura_current[sourceGUID] = {'targetGUID': targetGUID, 'intervals': []}
                self.aura_current[sourceGUID]['intervals'].append((t0, t1))
        t0 = timeparse(self.startTime)
        encounter_length = timeparse(self.endTime) - t0
        q.exec("DROP TABLE IF EXISTS temp_buff")
        q.exec("CREATE TEMP TABLE temp_buff (unitGUID VARBINARY UNIQUE NOT NULL, unitName VARCHAR(50), spec VARCHAR(10), count SMALLINT UNSIGNED, uptime TIMESTAMP, uptimepct FLOAT, intervals VARCHAR, maxlen FLOAT)")
        q.prepare("INSERT INTO temp_buff (unitGUID, unitName, spec, count, uptime, uptimepct, intervals, maxlen) VALUES (:unitGUID, :unitName, :spec, :count, :uptime, :uptimepct, :intervals, :maxlen)")
        q.bindValue(':maxlen', encounter_length.total_seconds())
        unitInfo = QSqlQuery()
        unitInfo.prepare("SELECT a.unitName AS unitName, spec FROM actors a LEFT JOIN specs ON a.unitGUID = specs.unitGUID WHERE a.unitGUID = :unitGUID")
        for k in self.aura_current:
            self.aura_current[k]['count'] = len(self.aura_current[k]['intervals'])
            self.aura_current[k]['intervals'] = flattenIntervals(self.aura_current[k]['intervals'])
            self.aura_current[k]['intervals'] = [(timeparse(x[0]), timeparse(x[1])) for x in self.aura_current[k]['intervals']]
            uptime = datetime.timedelta()
            for x in self.aura_current[k]['intervals']:
                uptime += x[1] - x[0]
            self.aura_current[k]['uptime'] = uptime
            self.aura_current[k]['uptimepct'] = uptime / encounter_length * 100
            self.aura_current[k]['intervals'] = [((x[0] - t0).total_seconds(), (x[1] - t0).total_seconds()) for x in self.aura_current[k]['intervals']]
            q.bindValue(':unitGUID', k)
            q.bindValue(':count', self.aura_current[k]['count'])
            q.bindValue(':uptime', str(self.aura_current[k]['uptime']))
            q.bindValue(':uptimepct', self.aura_current[k]['uptimepct'])
            q.bindValue(':intervals', f"{self.aura_current[k]['intervals']}")
            unitInfo.bindValue(':unitGUID', k)
            unitInfo.exec()
            unitInfo.next()
            q.bindValue(':unitName', unitInfo.value(0))
            q.bindValue(':spec', unitInfo.value(1))
            q.exec()
        display_query = QSqlQuery()
        display_query.exec("SELECT unitName, PRINTF('%.2f%%', uptimepct) AS pct, intervals, count, uptime, unitGUID, maxlen, spec FROM temp_buff ORDER BY uptime DESC, unitName")
        self.table.setModel(auraSqlTableModel(display_query, False))
        for i in range(4, self.table.horizontalHeader().count()):
            self.table.hideColumn(i)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)

    def updateStatus(self):
        self.startTime = self.encounter_select.currentData()[0]
        self.endTime = self.encounter_select.currentData()[1]
        self.everyone = self.source_select.currentData() == AFFILIATION[self.source_affiliation]
        self.meter = self.meter_select.currentText()
        self.everyoneTarget = isTargetEveryone(self.meter, self.source_affiliation, self.target_select.currentData())
        self.updateTableFilters()

    def updateUnitList(self):
        self.source_select.blockSignals(True)
        self.target_select.blockSignals(True)
        if self.source_select.currentData():
            self.source_current = self.source_select.currentData()
        if self.target_select.currentData():
            self.target_current = self.target_select.currentData()
        self.source_select.clear()
        self.target_select.clear()
        self.meter = self.meter_select.currentText()
        self.updateTargetAffiliation()
        self.source_select.addItem(f"All {AFFILIATION[self.source_affiliation]}", AFFILIATION[self.source_affiliation])
        self.target_select.addItem(f"All {AFFILIATION[self.target_affiliation]}", AFFILIATION[self.target_affiliation])
        unit_query = QSqlQuery()
        with open('queries/find_actors.sql', 'r') as f:
            unit_query.prepare(f.read())
        unit_query.bindValue(":startTime", self.encounter_select.currentData()[0])
        unit_query.bindValue(":endTime", self.encounter_select.currentData()[1])
        unit_query.exec()
        while unit_query.next():
            #Take into account mind controlled NPC as friendly (isPet = 1, isNPC = 1)
            if unit_query.value(1) == self.source_affiliation or unit_query.value(3) == 1 - self.source_affiliation or (unit_query.value(2) and self.source_affiliation):
                self.source_select.addItem(QIcon(QPixmap(PATH_HERO(unit_query.value(5)))), f"{'(pet) ' if unit_query.value(2) and not unit_query.value(3) else ''}{unit_query.value(0)}", (unit_query.value(0), unit_query.value(4)))
            if unit_query.value(1) == self.target_affiliation or unit_query.value(3) == 1 - self.target_affiliation or (unit_query.value(2) and self.target_affiliation):
                self.target_select.addItem(QIcon(QPixmap(PATH_HERO(unit_query.value(5)))), f"{'(pet) ' if unit_query.value(2) and not unit_query.value(3) else ''}{unit_query.value(0)}", (unit_query.value(0), unit_query.value(4)))
        if self.source_current:
            #This does not work for some reason?
            '''
            index = self.source_select.findData(self.source_current)
            self.source_select.setCurrentIndex(0 if index == -1 else index)
            '''
            for i in range(self.source_select.count()):
                if self.source_select.itemData(i) == self.source_current:
                    self.source_select.setCurrentIndex(i)
                    break
        else:
            self.source_select.setCurrentIndex(0)
        if self.target_current:
            #Likewise
            '''
            index = self.target_select.findData(self.target_current)
            self.target_select.setCurrentIndex(0 if index == -1 else index)
            '''
            for i in range(self.target_select.count()):
                if self.target_select.itemData(i) == self.target_current:
                    self.target_select.setCurrentIndex(i)
                    break
        else:
            self.target_select.setCurrentIndex(0)
        self.updateMainQuery()
        self.source_select.blockSignals(False)
        self.target_select.blockSignals(False)

    def resetSourceSelection(self):
        self.source_select.setCurrentIndex(0)

    def resetTargetSelection(self):
        self.target_select.setCurrentIndex(0)

    def swapAffiliation(self):
        self.source_affiliation = 1 - self.source_affiliation
        self.actors_swap_button.setText(AFFILIATION[self.source_affiliation])
        self.updateUnitList()

    def swapDirection(self):
        self.direction = 1 - self.direction
        self.direction_swap_button.setText(DIRECTION[self.direction])
        self.updateUnitList() #mainquery?

    def updateTargetAffiliation(self):
        if self.meter in (DAMAGEDONE, DAMAGETAKEN, DEBUFFS, DEATHS):
            self.target_affiliation = 1 - self.source_affiliation
        elif self.meter in (HEALING, BUFFS):
            self.target_affiliation = self.source_affiliation
        else:
            self.target_affiliation = 0

    def tableClicked(self, item):
        if self.meter in (DAMAGEDONE, DAMAGETAKEN, HEALING):
            if (new_source := self.source_select.findText(item.siblingAtColumn(0).data())) != -1:
                self.source_select.setCurrentIndex(new_source)
        elif self.meter == DEATHS:
            timestamp = item.siblingAtColumn(5).data()
            unitName = item.siblingAtColumn(1).data()
            if (idx := self.source_select.findText(unitName)) != -1:
                self.source_select.blockSignals(True)
                self.source_select.setCurrentIndex(idx)
                self.source_select.blockSignals(False)
                self.queryDeaths(timestamp, unitName)
        elif self.meter in (BUFFS, DEBUFFS):
            name = item.siblingAtColumn(0).data()
            everyone = self.source_select.currentData() == AFFILIATION[self.source_affiliation]
            if self.direction:
                if everyone and (new_source := self.source_select.findText(name)) != -1:
                        self.source_select.setCurrentIndex(new_source)
                elif (new_target := self.target_select.findText(name)) != -1:
                        self.target_select.setCurrentIndex(new_target)
                else:
                    for i in range(self.spell_select.count()):
                        if self.spell_select.model().index(i,1).data() == str(item.siblingAtColumn(5).data()):
                            self.spell_select.setCurrentIndex(i)
                            break
            else:
                if everyone and (new_source := self.source_select.findText(name)) != -1:
                        self.source_select.setCurrentIndex(new_source)
                elif (new_target := self.target_select.findText(name)) != -1:
                        self.target_select.setCurrentIndex(new_target)
                else:
                    for i in range(self.spell_select.count()):
                        if self.spell_select.model().index(i,1).data() == str(item.siblingAtColumn(5).data()):
                            self.spell_select.setCurrentIndex(i)
                            break

    def plotAuraGraph(self, spellID):
        x0, x1, x_Left, x_Width = plotAuras(self.encounter_select.currentData()[0], self.encounter_select.currentData()[1], self.auras_current[spellID]['intervals'])
        self.graph.clear()
        self.graph.setMaximumHeight(100)
        self.graph.setXRange(x0, x1)
        self.graph.setYRange(0, 1)
        
        self.graph.addItem(pg.BarGraphItem(x = x_Left, width = x_Width, height = 1))
        self.graph.show()

    def editPetsOwners(self, database = None):
        if self.file_name:
            if self.create_pet_editing_window:
                self.create_pet_editing_window.show()
            else:
                self.create_pet_editing_window = pet_recognition.PetEditing(self)
                self.create_pet_editing_window.show()

    def populateAuraSelector(self):
        spell_current = self.spell_select.model().index(self.spell_select.currentIndex(),1).data()
        self.direction_swap_button.show()
        self.spell_clear_button.show()
        self.spell_select.show()
        if self.meter in (BUFFS, DEBUFFS):
            everyone = self.source_select.currentData() == AFFILIATION[self.source_affiliation]
            startTime = self.encounter_select.currentData()[0]
            endTime = self.encounter_select.currentData()[1]
            auraType = 'BUFF' if self.meter == BUFFS else 'DEBUFF'
            direction = APPLIED if self.direction else GAINED
            q = QSqlQuery()
            if everyone:
                if self.target_select.currentData() == AFFILIATION[self.source_affiliation if self.meter == BUFFS else 1 - self.source_affiliation]:
                    with open(f"queries/buffs_{direction}_all-all.sql", 'r') as f:
                        q.prepare(f.read())
                else:
                    with open(f"queries/buffs_{direction}_all-1.sql", 'r') as f:
                        q.prepare(f.read())
                    q.bindValue(':sourceGUID', self.target_select.currentData()[1])
                q.bindValue(":affiliation", self.source_affiliation)
            else:
                if self.target_select.currentData() == AFFILIATION[self.source_affiliation if self.meter == BUFFS else 1 - self.source_affiliation]: 
                    with open(f"queries/buffs_{direction}_1-all.sql", 'r') as f:
                        q.prepare(f.read())
                else:
                    with open(f"queries/buffs_{direction}_1-1.sql", 'r') as f:
                        q.prepare(f.read())
                    q.bindValue(':sourceGUID', self.target_select.currentData()[1])
                q.bindValue(":targetGUID", self.source_select.currentData()[1])
            q.bindValue(":startTime", startTime)
            q.bindValue(":endTime", endTime)
            q.bindValue(":auraType", auraType)
            q.exec()
            self.auras_current = {}
            while q.next():
                if q.value(1) not in self.auras_current:
                    self.auras_current[q.value(1)] = {'spellName': q.value(0), 'school': q.value(4), 'icon': q.value(5)}
            model = QStandardItemModel()
            model.appendRow(QStandardItem(ALL_AURAS))
            for i in sorted(self.auras_current.keys(), key = lambda x : self.auras_current[x]['spellName']):
                name = QStandardItem(QIcon(QPixmap(PATH_SPELL(self.auras_current[i]['icon']))), self.auras_current[i]['spellName'])
                name.setForeground(QBrush(class_recognition.getSchoolColours(self.auras_current[i]['school'])[-1]))
                spellID = QStandardItem(str(i))
                model.appendRow([name, spellID])
            table = QTableView()
            table.setModel(model)
            table.verticalHeader().setVisible(False)
            table.horizontalHeader().setVisible(False)
            table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
            table.horizontalHeader().setStretchLastSection(True)

            self.spell_select.setModel(model)
            self.spell_select.setView(table)

            found = False
            for i in range(self.spell_select.count()):
                if self.spell_select.model().index(i,1).data() == spell_current:
                    self.spell_select.setCurrentIndex(i)
                    found = True
                    break
            if not found:
                self.spell_select.setCurrentIndex(0)

    def resetSpellSelection(self):
        self.spell_select.setCurrentIndex(0)

    def updateTableFilters(self):
        self.table.updateFilters()

class meterSqlTableModel(QSqlTableModel):
    def __init__(self, query = QSqlQuery(), meter = DAMAGEDONE, everyone = True, tooltipColumn = -1, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.meter = meter
        self.everyone = everyone
        self.tooltipColumn = tooltipColumn
        self.setQuery(query)

    def data(self, index, role):
        if index.column() == 0:
            if role == Qt.ItemDataRole.DecorationRole:
                try:
                    if COLUMNS[self.meter][self.everyone][self.tooltipColumn][TYPE] == HERO:
                        if (icon := index.siblingAtColumn(COLUMNS[self.meter][self.everyone][self.tooltipColumn][HERO]).data()):
                            return QPixmap(PATH_HERO(icon)).scaledToHeight(25)
                    elif COLUMNS[self.meter][self.everyone][self.tooltipColumn][TYPE] == SPELL:
                        if (icon := index.siblingAtColumn(COLUMNS[self.meter][self.everyone][self.tooltipColumn][ICON]).data()):
                            return QPixmap(PATH_SPELL(icon)).scaledToHeight(25)
                        elif QSqlTableModel.data(self, index, Qt.ItemDataRole.DisplayRole).endswith(MELEE):
                            return QPixmap(PATH_SPELL(MELEE_ICON)).scaledToHeight(25)
                except:
                    pass
            elif role == Qt.ItemDataRole.ForegroundRole and self.meter != DEATHS:
                if COLUMNS[self.meter][self.everyone][self.tooltipColumn][TYPE] == HERO:
                    try:
                        return QBrush(class_recognition.CLASS_COLOUR[index.siblingAtColumn(COLUMNS[self.meter][self.everyone][self.tooltipColumn][HERO]).data()[:-2]][0])
                    except:
                        pass
                elif COLUMNS[self.meter][self.everyone][self.tooltipColumn][TYPE] == SPELL:
                    try:
                        return QBrush(class_recognition.getSchoolColours(int(index.siblingAtColumn(COLUMNS[self.meter][self.everyone][self.tooltipColumn][SCHOOL]).data()))[0])
                    except:
                        pass
        elif index.column() == 1 and role == Qt.ItemDataRole.TextAlignmentRole:
            #return Qt.AlignmentFlag.AlignRight
            return 130
        return QSqlTableModel.data(self, index, role)

class deathSqlTableModel(QSqlTableModel):
    def __init__(self, query, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setQuery(query)

    def data(self, index, role):
        if index.column() == 1:
            if role == Qt.ItemDataRole.DecorationRole:
                if (icon := QSqlTableModel.data(self, index.siblingAtColumn(6), Qt.ItemDataRole.DisplayRole)):
                    return QPixmap(PATH_HERO(icon)).scaledToHeight(25)
            elif role == Qt.ItemDataRole.ForegroundRole:
                try:
                    return QBrush(class_recognition.CLASS_COLOUR[index.siblingAtColumn(6).data()[:-2]])
                except:
                    pass
        elif index.column() == 3:
            if role == Qt.ItemDataRole.DecorationRole:
                if (icon := QSqlTableModel.data(self, index.siblingAtColumn(7), Qt.ItemDataRole.DisplayRole)):
                    return QPixmap(PATH_SPELL(icon)).scaledToHeight(25)
                elif QSqlTableModel.data(self, index, Qt.ItemDataRole.DisplayRole).endswith(MELEE):
                    return QPixmap(PATH_SPELL(MELEE_ICON)).scaledToHeight(25)
            elif role == Qt.ItemDataRole.ForegroundRole:
                try:
                    return QBrush(class_recognition.getSchoolColours(int(index.siblingAtColumn(8).data()))[-1])
                except:
                    pass
        elif index.column() == 0 and role == Qt.ItemDataRole.TextAlignmentRole:
            #return Qt.AlignmentFlag.AlignRight
            return 130
        return QSqlTableModel.data(self, index, role)

class deathRecapSqlTableModel(QSqlTableModel):
    def __init__(self, query, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setQuery(query)
    
    def data(self, index, role):
        if index.column() == 0 and role == Qt.ItemDataRole.TextAlignmentRole:
            #return Qt.AlignmentFlag.AlignRight
            return 130
        elif index.column() == 1:
            if role == Qt.ItemDataRole.ForegroundRole:
                event = index.siblingAtColumn(4).data()
                if event.endswith('DAMAGE'):
                    return QBrush(Qt.GlobalColor.red)
                elif event.endswith('HEAL'):
                    return QBrush(Qt.GlobalColor.green)
                elif event.endswith('MISSED'):
                    return QBrush(Qt.GlobalColor.cyan)
            elif role == Qt.ItemDataRole.DecorationRole:
                if (icon := QSqlTableModel.data(self, index.siblingAtColumn(6), Qt.ItemDataRole.DisplayRole)):
                    return QPixmap(PATH_SPELL(icon)).scaledToHeight(25)
                elif QSqlTableModel.data(self, index.siblingAtColumn(2), Qt.ItemDataRole.DisplayRole).endswith(MELEE):
                    return QPixmap(PATH_SPELL(MELEE_ICON)).scaledToHeight(25)
        elif index.column() == 2:
            if role == Qt.ItemDataRole.ForegroundRole:
                try:
                    colour = class_recognition.getSchoolColours(int(index.siblingAtColumn(7).data()))[-1]
                    return QBrush(colour)
                except:
                    pass
        elif index.column() == 3:
            if role == Qt.ItemDataRole.DecorationRole:
                if (icon := QSqlTableModel.data(self, index.siblingAtColumn(5), Qt.ItemDataRole.DisplayRole)):
                    return QPixmap(PATH_HERO(icon)).scaledToHeight(25)
            elif role == Qt.ItemDataRole.ForegroundRole:
                try:
                    if (colour := class_recognition.CLASS_COLOUR[index.siblingAtColumn(5).data()[:-2]]):
                        return QBrush(colour)
                except:
                    pass
        return QSqlTableModel.data(self, index, role)

class meterDelegate(QAbstractItemDelegate):
    def __init__(self, meter = DAMAGEDONE, everyone = True, tooltipColumn = -1):
        super().__init__()
        self.meter = meter
        self.everyone = everyone
        self.tooltipColumn = tooltipColumn
    
    def paint(self, painter, option, index):
        try:
            scale = float(index.data(Qt.ItemDataRole.DisplayRole))
            if COLUMNS[self.meter][self.everyone][self.tooltipColumn][TYPE] == HERO:
                try:
                    colour = class_recognition.CLASS_COLOUR[index.siblingAtColumn(COLUMNS[self.meter][self.everyone][self.tooltipColumn][HERO]).data()[:-2]]
                except:
                    colour = [Qt.GlobalColor.gray]
            elif COLUMNS[self.meter][self.everyone][self.tooltipColumn][TYPE] in (SPELL, SPELL_INFO):
                try:
                    colour = class_recognition.getSchoolColours(int(index.siblingAtColumn(COLUMNS[self.meter][self.everyone][self.tooltipColumn][SCHOOL]).data()))
                except:
                    colour = [Qt.GlobalColor.gray]
            else:
                colour = [Qt.GlobalColor.gray]
            x = option.rect.topLeft().x()
            y = option.rect.topLeft().y()
            w = option.rect.topRight().x() - x
            h = option.rect.bottomLeft().y() - y
            w = (w - 2 * BAR_OFFSET_X) * scale
            h = (h - 2 * BAR_OFFSET_Y)
            x = x + BAR_OFFSET_X
            y = y + BAR_OFFSET_Y
            painter.setPen(Qt.PenStyle.NoPen)
            if (l := len(colour)) == 1:
                painter.setBrush(QBrush(colour[0]))
                painter.drawRect(QRectF(x, y, w, h))
            else:
                gradient = QLinearGradient(x, y, x + w, y + h)
                for i in range(l):
                    gradient.setColorAt(i * 1.0 / (l - 1), colour[i])
                painter.fillRect(QRectF(x, y, w, h), gradient)
        except:
            pass

class auraDelegate(QAbstractItemDelegate):
    def __init__(self, isSpell = True):
        super().__init__()
        self.isSpell = isSpell

    def paint(self, painter, option, index):
        intervals = re.findall(r"\((\d+\.\d+), (\d+\.\d+)\)", index.data(Qt.ItemDataRole.DisplayRole))
        x = option.rect.topLeft().x() + BAR_OFFSET_X
        y = option.rect.topLeft().y() + BAR_OFFSET_Y
        h = option.rect.bottomLeft().y() - y - BAR_OFFSET_Y
        w = option.rect.topRight().x() - x - BAR_OFFSET_X
        l = float(index.siblingAtColumn(6).data())
        painter.setPen(Qt.PenStyle.NoPen)
        if self.isSpell:
            try:
                painter.setBrush(QBrush(class_recognition.getSchoolColours(int(index.siblingAtColumn(7).data()))[-1]))
            except:
                painter.setBrush(QBrush(Qt.GlobalColor.gray))
        else:
            try:
                painter.setBrush(QBrush(class_recognition.CLASS_COLOUR[index.siblingAtColumn(7).data()[:-2]]))
            except:
                painter.setBrush(QBrush(Qt.GlobalColor.gray))
        for i in intervals:
            x0, x1 = float(i[0]), float(i[1])
            painter.drawRect(QRectF(x + (x0 / l * w), y, (x1 - x0) / l * w, h))

class auraSqlTableModel(QSqlTableModel):
    def __init__(self, query, isSpell = True, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setQuery(query)
        self.isSpell = isSpell

    def data(self, index, role):
        if index.column() == 0:
            if role == Qt.ItemDataRole.DecorationRole:
                if self.isSpell and (icon := index.siblingAtColumn(8).data()):
                    return QPixmap(PATH_SPELL(icon)).scaledToHeight(25)
                elif (icon := index.siblingAtColumn(7).data()):
                    return QPixmap(PATH_HERO(icon)).scaledToHeight(25)
            elif role == Qt.ItemDataRole.ForegroundRole:
                if self.isSpell:
                    try:
                        return QBrush(class_recognition.getSchoolColours(int(index.siblingAtColumn(7).data()))[-1])
                    except:
                        pass
                else:
                    try:
                        return QBrush(class_recognition.CLASS_COLOUR[index.siblingAtColumn(7).data()[:-2]])
                    except:
                        pass
        elif index.column() == 1 and role == Qt.ItemDataRole.TextAlignmentRole:
            #return Qt.AlignmentFlag.AlignRight
            return 130
        return QSqlTableModel.data(self, index, role)

class tooltipTable(QTableView):
    def __init__(self):
        super().__init__()
        self.viewport().installEventFilter(self)
        self.setMouseTracking(True)
        self.tooltip = QDialog(self, Qt.WindowType.Popup | Qt.WindowType.ToolTip)
        self.container = QWidget(self.tooltip)
        self.container_layout = QHBoxLayout()
        self.tooltip_table = QTableView()
        self.tooltip_table.verticalHeader().setVisible(False)
        self.tooltip_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.tooltip_table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tooltip_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.container_layout.addWidget(self.tooltip_table)
        self.container.setLayout(self.container_layout)
        self.current_cell = None
        self.tooltip.installEventFilter(self)

    def updateFilters(self):
        self.meter = self.parent().parent().meter
        self.everyone = self.parent().parent().everyone
        self.target = self.parent().parent().target_select.currentData()
        self.source_affiliation = self.parent().parent().source_affiliation
        self.everyoneTarget = isTargetEveryone(self.meter, self.source_affiliation, self.target)
        self.startTime = self.parent().parent().startTime
        self.endTime = self.parent().parent().endTime

    def eventFilter(self, object, event):
        if self.viewport().isVisible():
            if event.type() == QEvent.Type.MouseMove:
                coords = event.pos()
                index = self.indexAt(coords)
                if index.isValid():
                    path = getPath(self.meter, self.everyone, self.everyoneTarget, index.column())
                    cell = (index.row(), index.column())
                    if cell != self.current_cell:
                        self.current_cell = cell
                        self.hideTooltip()
                        if os.path.exists(path):
                            self.createTooltip(index, self.meter, self.everyone, self.target, self.everyoneTarget, path)
                    if os.path.exists(path):
                        self.showTooltip(index, coords)
                    else:
                        self.hideTooltip()
            elif event.type() == QEvent.Type.Leave:
                self.hideTooltip()
                self.current_cell = None
        return super().eventFilter(object, event)

    def createTooltip(self, index = None, meter = DAMAGEDONE, everyone = True, target = None, everyoneTarget = True, path = ''):
        try:
            targetName = target[0]
        except:
            targetName = ''
        if os.path.exists(path):
            display_query = QSqlQuery()
            with open(path, 'r') as f:
                display_query.prepare(f.read())
            if meter == DAMAGEDONE:
                display_query.bindValue(':targetName', targetName)
                display_query.bindValue(':sourceName', index.siblingAtColumn(6 if everyone else 14).data())
                display_query.bindValue(':spellID', int(index.siblingAtColumn(13).data() or '0'))
                display_query.bindValue(':ownerName', index.siblingAtColumn(15).data())
            elif meter == DAMAGETAKEN:
                display_query.bindValue(':targetName', index.siblingAtColumn(7 if everyone else 12).data())
                display_query.bindValue(':sourceName', targetName if everyoneTarget or everyone else index.siblingAtColumn(13).data())
                display_query.bindValue(':spellID', int(index.siblingAtColumn(11).data() or '0'))
                display_query.bindValue(':ownerName', index.siblingAtColumn(14).data())
            display_query.bindValue(':startTime', self.startTime)
            display_query.bindValue(':endTime', self.endTime)
            print(display_query.exec())
            self.tooltip_table.setItemDelegateForColumn(COLUMNS[meter][everyone][index.column()][BAR], meterDelegate(meter, everyone, index.column()))
            self.tooltip_table.setModel(meterSqlTableModel(display_query, meter, everyone, index.column()))
            self.tooltip_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
            self.tooltip_table.setColumnWidth(2, 200)
            for i in range(COLUMNS[self.meter][self.everyone][index.column()][HIDE], self.tooltip_table.horizontalHeader().count()):
                self.tooltip_table.hideColumn(i)
            self.container.setFixedSize(self.tooltip_table.horizontalHeader().length() + 19, self.tooltip_table.verticalHeader().length() + 43)

    def showTooltip(self, index, coords):
        if self.meter in (DAMAGEDONE, DAMAGETAKEN):
            self.tooltip.move(self.viewport().mapToGlobal(coords + QPoint(10, 20)))
            self.tooltip.show()
        else:
            self.hideTooltip()

    def hideTooltip(self):
        self.tooltip.hide()

def isTargetEveryone(meter, sourceAffiliation, target):
    if meter in (DAMAGEDONE, DAMAGETAKEN, DEBUFFS):
        return target == AFFILIATION[1 - sourceAffiliation]
    else:
        return target == AFFILIATION[sourceAffiliation]

def getPath(meter, everyone, everyoneTarget, column = None):
    return f"queries/{meter.replace(' ', '_').lower()}_{'all' if everyone else 1}-{'all' if everyoneTarget else 1}{'_' + str(column) if column != None else ''}.sql"

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(style_sheet)
    DELEGATES = {meter: {True: meterDelegate(meter, True), False: meterDelegate(meter, False)} for meter in METERS}
    DB = QSqlDatabase.addDatabase("QSQLITE")
    window = MainWindow()
    sys.exit(app.exec())
