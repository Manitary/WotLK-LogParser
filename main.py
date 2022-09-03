import sys, os, re
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox, QFileDialog, QComboBox, QLabel, QVBoxLayout, QWidget, QTableView, QHBoxLayout, QAbstractItemView, QPushButton, QAbstractItemDelegate, QStyledItemDelegate, QHeaderView
from PyQt6.QtGui import QAction, QFont, QPixmap, QBrush, QLinearGradient, QIcon
from PyQt6.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel
from PyQt6.QtCore import Qt, QRectF
import pyqtgraph as pg
from tools import flattenIntervals, plotAuras
import time, datetime
from dateutil.parser import parse as timeparse
import zipfile, rarfile
import parser, pet_recognition, class_recognition

ALL = "AllUnits"
FRIENDLY = "Friendlies"
HOSTILE = "Enemies"
AFFILIATION = [HOSTILE, FRIENDLY]
DAMAGEDONE = "Damage Done"
DAMAGETAKEN = "Damage Taken"
HEALING = "Healing"
DEATHS = "Deaths"
BUFFS = "Buffs"
DEBUFFS = "Debuffs"
METERS = [DAMAGEDONE, DAMAGETAKEN, HEALING, DEATHS, BUFFS, DEBUFFS]
SPELL_DATA_PATH = os.path.abspath('data/spell_data.db')
ICON_COL = {
    DAMAGEDONE: {True: 5, False: 10},
    DAMAGETAKEN: {True: 6, False: 10},
    HEALING: {True: 7, False: 8},
}
BAR_COL = {
    DAMAGEDONE: {True: 2, False: 2},
}
BAR_OFFSET_X = 5
BAR_OFFSET_Y = 6
PATH_HERO = lambda icon: f"wow_hero_classes/{icon}.png" if icon else ''
PATH_SPELL = lambda icon: f"wow_icon/{icon.lower()}.jpg" if icon else ''
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
        self.setMinimumSize(600, 400)
        self.setWindowTitle("Parser")
        self.createActions()
        self.createMenu()
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.main_vbox = QVBoxLayout(self.centralWidget)
        self.file_name = None
        self.setUpMainWindow()
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
        self.graph = pg.PlotWidget()
        self.table = QTableView()
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.clicked.connect(self.tableClicked)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.encounter_select.currentTextChanged.connect(self.updateUnitList)
        self.meter_select.currentTextChanged.connect(self.updateUnitList)
        self.source_select.currentTextChanged.connect(self.updateMainQuery)
        self.target_select.currentTextChanged.connect(self.updateMainQuery)

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
        self.main_vbox.addWidget(self.graph)
        self.main_vbox.addWidget(self.table)
    
    def setUpParse(self):
        QSqlQuery(f"ATTACH DATABASE '{SPELL_DATA_PATH}' AS spell_db").exec()

        self.encounter_select.blockSignals(True)
        self.meter_select.blockSignals(True)
        self.source_select.blockSignals(True)
        self.target_select.blockSignals(True)
        self.encounter_select.clear()
        self.source_select.clear()
        self.target_select.clear()

        encounter_query = QSqlQuery("SELECT enemy, timeStart, timeEnd, isKill FROM encounters ORDER BY timeStart")
        encounter_query.exec()
        while encounter_query.next():
            self.encounter_select.addItem(f"{encounter_query.value(0)} ({'kill' if encounter_query.value(3) else 'wipe'}) - {encounter_query.value(1)} | {encounter_query.value(2)}", (encounter_query.value(1), encounter_query.value(2)))
        self.source_current = FRIENDLY
        self.target_current = HOSTILE
        self.source_affiliation = 1
        self.target_affiliation = 0
        self.actors_swap_button.setText(AFFILIATION[self.source_affiliation])

        self.encounter_select.blockSignals(False)
        self.meter_select.blockSignals(False)
        self.source_select.blockSignals(False)
        self.target_select.blockSignals(False)

        self.updateUnitList()
        print('setup done')

    def updateMainQuery(self):
        meter = self.meter_select.currentText()
        self.graph.hide()
        self.table.setModel(self.model)
        if meter == DAMAGEDONE:
            self.queryDamageDone(meter)
        elif meter == DAMAGETAKEN:
            self.queryDamageTaken(meter)
        elif meter == HEALING:
            self.queryHealing(meter)
        elif meter == DEATHS:
            self.queryDeaths(meter)
        elif meter in (BUFFS, DEBUFFS):
            self.queryBuffs(meter)
        else:
            self.display_query = QSqlQuery()
            self.model.setQuery(self.display_query)
        print('query done')

    def queryDamageDone(self, meter):
        display_query = QSqlQuery()
        everyone = self.source_select.currentData() == AFFILIATION[self.source_affiliation]
        if everyone:
            if self.target_select.currentData() == AFFILIATION[1 - self.source_affiliation]:
                with open('queries/damage_done_all-all.sql', 'r') as f:
                    display_query.prepare(f.read())
            else:
                with open('queries/damage_done_all-1.sql', 'r') as f:
                    display_query.prepare(f.read())
                display_query.bindValue(":targetName", self.target_select.currentText())
            display_query.bindValue(":affiliation", self.source_affiliation)
        else:
            if self.target_select.currentData() == AFFILIATION[1 - self.source_affiliation]:
                with open('queries/damage_done_1-all.sql', 'r') as f:
                    display_query.prepare(f.read())
            else:
                with open('queries/damage_done_1-1.sql', 'r') as f:
                    display_query.prepare(f.read())
                display_query.bindValue(":targetName", self.target_select.currentText())
            display_query.bindValue(":sourceName", self.source_select.currentText())
        display_query.bindValue(":startTime", self.encounter_select.currentData()[0])
        display_query.bindValue(":endTime", self.encounter_select.currentData()[1])
        display_query.exec()
        self.table.setItemDelegateForColumn(2, DELEGATES[meter][everyone])
        self.table.setModel(meterSqlTableModel(display_query, meter, everyone))
        self.table.hideColumn(ICON_COL[meter][everyone])
        self.table.hideColumn(ICON_COL[meter][everyone] + 1)

    def queryDamageTaken(self, meter):
        display_query = QSqlQuery()
        everyone = self.source_select.currentData() == AFFILIATION[self.source_affiliation]
        if everyone:
            if self.target_select.currentData() == AFFILIATION[1 - self.source_affiliation]:
                with open('queries/damage_taken_all-all.sql', 'r') as f:
                    display_query.prepare(f.read())
            else:
                with open('queries/damage_taken_all-1.sql', 'r') as f:
                    display_query.prepare(f.read())
                    display_query.bindValue(":sourceName", self.target_select.currentText())
            display_query.bindValue(":affiliation", self.source_affiliation)
        else:
            if self.target_select.currentData() == AFFILIATION[1 - self.source_affiliation]:
                with open('queries/damage_taken_1-all.sql', 'r') as f:
                    display_query.prepare(f.read())
            else:
                with open('queries/damage_taken_1-1.sql', 'r') as f:
                    display_query.prepare(f.read())
                    display_query.bindValue(":sourceName", self.target_select.currentText())
            display_query.bindValue(":targetName", self.source_select.currentText())
        display_query.bindValue(":startTime", self.encounter_select.currentData()[0])
        display_query.bindValue(":endTime", self.encounter_select.currentData()[1])
        display_query.exec()
        self.table.setItemDelegateForColumn(2, DELEGATES[meter][everyone])
        self.table.setModel(meterSqlTableModel(display_query, meter, everyone))
        self.table.hideColumn(ICON_COL[meter][everyone])
        self.table.hideColumn(ICON_COL[meter][everyone] + 1)

    def queryHealing(self, meter):
        display_query = QSqlQuery()
        everyone = self.source_select.currentData() == AFFILIATION[self.source_affiliation]
        if everyone:
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
        display_query.bindValue(":startTime", self.encounter_select.currentData()[0])
        display_query.bindValue(":endTime", self.encounter_select.currentData()[1])
        display_query.exec()
        self.table.setItemDelegateForColumn(2, DELEGATES[meter][everyone])
        self.table.setModel(meterSqlTableModel(display_query, meter, everyone))
        self.table.hideColumn(ICON_COL[meter][everyone])
        self.table.hideColumn(ICON_COL[meter][everyone] + 1)

    def queryDeaths(self, meter, timestamp = None, unitName = None):
        self.table.setItemDelegateForColumn(2, QStyledItemDelegate())
        display_query = QSqlQuery()
        everyone = self.source_select.currentData() == AFFILIATION[self.source_affiliation]
        if timestamp and unitName:
            with open('queries/deaths_recap.sql', 'r') as f:
                display_query.prepare(f.read())
            display_query.bindValue(":targetName", unitName)
            display_query.bindValue(":endTime", timestamp)
            display_query.bindValue(":startTime", self.encounter_select.currentData()[0])
            display_query.exec()
            self.table.setModel(deathRecapSqlTableModel(display_query))
            for i in range(4, 7):
                self.table.hideColumn(i)
        elif everyone:
            with open('queries/deaths_all.sql', 'r') as f:
                display_query.prepare(f.read())
            display_query.bindValue(":affiliation", self.source_affiliation)
            display_query.bindValue(":endTime", self.encounter_select.currentData()[1])
            display_query.bindValue(":startTime", self.encounter_select.currentData()[0])
            display_query.exec()
            self.table.setModel(deathSqlTableModel(display_query))
            for i in range(5, 10):
                self.table.hideColumn(i)
        else:
            with open('queries/deaths_1.sql', 'r') as f:
                display_query.prepare(f.read())
            display_query.bindValue(":affiliation", self.source_affiliation)
            display_query.bindValue(":endTime", self.encounter_select.currentData()[1])
            display_query.bindValue(":startTime", self.encounter_select.currentData()[0])
            display_query.bindValue(":targetGUID", self.source_select.currentData()[1])
            display_query.exec()
            self.table.setModel(deathSqlTableModel(display_query))
            for i in range(5, 9):
                self.table.hideColumn(i)

    def queryBuffs(self, meter):
        everyone = self.source_select.currentData() == AFFILIATION[self.source_affiliation]
        self.table.setItemDelegateForColumn(2, auraDelegate())
        startTime = self.encounter_select.currentData()[0]
        endTime = self.encounter_select.currentData()[1]
        auraType = 'BUFF' if meter == BUFFS else 'DEBUFF'
        q = QSqlQuery()
        if everyone:
            if self.target_select.currentData() == AFFILIATION[self.source_affiliation if meter == BUFFS else 1 - self.source_affiliation]:
                with open('queries/buffs_taken_all-all.sql', 'r') as f:
                    q.prepare(f.read())
            else:
                with open('queries/buffs_taken_all-1.sql', 'r') as f:
                    q.prepare(f.read())
                q.bindValue(':sourceGUID', self.target_select.currentData()[1])
            q.bindValue(":affiliation", self.source_affiliation)
        else:
            if self.target_select.currentData() == AFFILIATION[self.source_affiliation if meter == BUFFS else 1 - self.source_affiliation]: 
                with open('queries/buffs_taken_1-all.sql', 'r') as f:
                    q.prepare(f.read())
            else:
                with open('queries/buffs_taken_1-1.sql', 'r') as f:
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
                self.auras_current[q.value(1)] = {'spellName': q.value(0), 'intervals': []}
            self.auras_current[q.value(1)]['intervals'].append((q.value(2), q.value(3)))
        t0 = timeparse(startTime)
        encounter_length = timeparse(endTime) - t0
        q.exec("DROP TABLE IF EXISTS temp_buff")
        q.exec("CREATE TEMP TABLE temp_buff (spellID MEDIUMINT UNSIGNED UNIQUE NOT NULL, spellName VARCHAR(50), count SMALLINT UNSIGNED, uptime TIMESTAMP, uptimepct FLOAT, intervals VARCHAR, maxlen FLOAT, spellSchool TINYINT UNSIGNED, icon VARCHAR(50))")
        q.prepare("INSERT INTO temp_buff (spellID, spellName, count, uptime, uptimepct, intervals, maxlen, spellSchool, icon) VALUES (:spellID, :spellName, :count, :uptime, :uptimepct, :intervals, :maxlen, :spellSchool, :icon)")
        q.bindValue(':maxlen', encounter_length.total_seconds())
        spellInfo = QSqlQuery()
        spellInfo.prepare("SELECT school_mask, icon FROM spell_db.spell_data WHERE spellID = :spellID")
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
            spellInfo.bindValue(':spellID', k)
            spellInfo.exec()
            spellInfo.next()
            q.bindValue(':spellSchool', spellInfo.value(0))
            q.bindValue(':icon', spellInfo.value(1))
            q.exec()
            display_query = QSqlQuery()
            display_query.exec("SELECT spellName, PRINTF('%.2f%%', uptimepct) AS pct, intervals, count, uptime, spellID, maxlen, spellSchool, icon FROM temp_buff ORDER BY uptime DESC, spellName")
            self.table.setModel(auraSqlTableModel(display_query))
            for i in range(4, 9):
                self.table.hideColumn(i)

    def updateUnitList(self):
        self.source_select.blockSignals(True)
        self.target_select.blockSignals(True)
        if self.source_select.currentData():
            self.source_current = self.source_select.currentData()
        if self.target_select.currentData():
            self.target_current = self.target_select.currentData()
        self.source_select.clear()
        self.target_select.clear()
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
    
    def updateTargetAffiliation(self):
        meter = self.meter_select.currentText()
        if meter in (DAMAGEDONE, DAMAGETAKEN, DEBUFFS, DEATHS):
            self.target_affiliation = 1 - self.source_affiliation
        elif meter in (HEALING, BUFFS):
            self.target_affiliation = self.source_affiliation
        else:
            self.target_affiliation = 0

    def tableClicked(self, item):
        if (new_source := self.source_select.findText(item.siblingAtColumn(0).data())) != -1:
            self.source_select.setCurrentIndex(new_source)
        elif self.meter_select.currentText() == DEATHS:
            timestamp = item.siblingAtColumn(5).data()
            unitName = item.siblingAtColumn(1).data()
            self.source_select.blockSignals(True)
            self.source_select.setCurrentIndex(self.source_select.findText(unitName))
            self.source_select.blockSignals(False)
            self.queryDeaths(DEATHS, timestamp, unitName)
        elif self.meter_select.currentText() == BUFFS:
            #self.plotAuraGraph(item.siblingAtColumn(5).data())
            pass
    
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

class meterSqlTableModel(QSqlTableModel):
    def __init__(self, query, meter, everyone, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.meter = meter
        self.everyone = everyone
        self.path = PATH_HERO if everyone else PATH_SPELL
        self.setQuery(query)

    def data(self, index, role):
        if index.column() == 0:
            if role == Qt.ItemDataRole.DecorationRole:
                try:
                    icon = QSqlTableModel.data(self, index.siblingAtColumn(ICON_COL[self.meter][self.everyone]), Qt.ItemDataRole.DisplayRole)
                    if icon:
                        return QPixmap(self.path(icon)).scaledToHeight(25)
                    elif QSqlTableModel.data(self, index, Qt.ItemDataRole.DisplayRole).endswith('MeleeSwing'):
                        return QPixmap(self.path('inv_axe_01')).scaledToHeight(25)
                except:
                    pass
            elif role == Qt.ItemDataRole.ForegroundRole and self.meter != DEATHS:
                if self.everyone:
                    try:
                        return QBrush(class_recognition.CLASS_COLOUR[index.siblingAtColumn(ICON_COL[self.meter][self.everyone]).data()[:-2]])
                    except:
                        pass
                else:
                    try:
                        return QBrush(class_recognition.getSchoolColours(int(index.siblingAtColumn(ICON_COL[self.meter][self.everyone] + 1).data()))[-1])
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
                elif QSqlTableModel.data(self, index, Qt.ItemDataRole.DisplayRole).endswith('MeleeSwing'):
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
                elif QSqlTableModel.data(self, index.siblingAtColumn(2), Qt.ItemDataRole.DisplayRole).endswith('MeleeSwing'):
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
    def __init__(self, meter = DAMAGEDONE, everyone = True):
        super().__init__()
        self.meter = meter
        self.everyone = everyone
    
    def paint(self, painter, option, index):
        try:
            scale = float(index.data(Qt.ItemDataRole.DisplayRole))
            try:
                colour = class_recognition.CLASS_COLOUR[index.siblingAtColumn(ICON_COL[self.meter][self.everyone]).data()[:-2]]
            except:
                colour = Qt.GlobalColor.gray
            x = option.rect.topLeft().x()
            y = option.rect.topLeft().y()
            w = option.rect.topRight().x() - x
            h = option.rect.bottomLeft().y() - y
            w = (w - 2 * BAR_OFFSET_X) * scale
            h = (h - 2 * BAR_OFFSET_Y)
            x = x + BAR_OFFSET_X
            y = y + BAR_OFFSET_Y
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(colour))
            try:
                if self.everyone:
                    painter.drawRect(QRectF(x, y, w, h))
                else:
                    colours = class_recognition.getSchoolColours(int(index.siblingAtColumn(ICON_COL[self.meter][self.everyone] + 1).data()))
                    if len(colours) > 1:
                        gradient = QLinearGradient(x, y, x+w, y+h)
                        gradient.setColorAt(0.0, colours[1])
                        gradient.setColorAt(1.0, colours[0])
                        painter.fillRect(QRectF(x, y, w, h), gradient)
                    else:
                        painter.setBrush(QBrush(colours[0]))
                        painter.drawRect(QRectF(x, y, w, h))
            except:
                painter.drawRect(QRectF(x, y, w, h))
        except:
            pass

class auraDelegate(QAbstractItemDelegate):
    def __init__(self):
        super().__init__()

    def paint(self, painter, option, index):
        intervals = re.findall(r"\((\d+\.\d+), (\d+\.\d+)\)", index.data(Qt.ItemDataRole.DisplayRole))
        x = option.rect.topLeft().x() + BAR_OFFSET_X
        y = option.rect.topLeft().y() + BAR_OFFSET_Y
        h = option.rect.bottomLeft().y() - y - BAR_OFFSET_Y
        w = option.rect.topRight().x() - x - BAR_OFFSET_X
        l = float(index.siblingAtColumn(6).data())
        painter.setPen(Qt.PenStyle.NoPen)
        try:
            painter.setBrush(QBrush(class_recognition.getSchoolColours(int(index.siblingAtColumn(7).data()))[-1]))
        except:
            painter.setBrush(QBrush(Qt.GlobalColor.gray))
        for i in intervals:
            x0, x1 = float(i[0]), float(i[1])
            painter.drawRect(QRectF(x + (x0 / l * w), y, (x1 - x0) / l * w, h))

class auraSqlTableModel(QSqlTableModel):
    def __init__(self, query, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setQuery(query)

    def data(self, index, role):
        if index.column() == 0:
            if role == Qt.ItemDataRole.DecorationRole:
                if (icon := QSqlTableModel.data(self, index.siblingAtColumn(8), Qt.ItemDataRole.DisplayRole)):
                    return QPixmap(PATH_SPELL(icon)).scaledToHeight(25)
            elif role == Qt.ItemDataRole.ForegroundRole:
                try:
                    return QBrush(class_recognition.getSchoolColours(int(index.siblingAtColumn(7).data()))[-1])
                except:
                    pass
        elif index.column() == 1 and role == Qt.ItemDataRole.TextAlignmentRole:
            #return Qt.AlignmentFlag.AlignRight
            return 130
        return QSqlTableModel.data(self, index, role)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(style_sheet)
    DELEGATES = {meter: {True: meterDelegate(meter, True), False: meterDelegate(meter, False)} for meter in METERS}
    DB = QSqlDatabase.addDatabase("QSQLITE")
    window = MainWindow()
    sys.exit(app.exec())
