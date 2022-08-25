import sys
from turtle import width
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox, QTextEdit, QFileDialog, QInputDialog, QFontDialog, QColorDialog, QComboBox, QLabel, QVBoxLayout, QWidget, QTableView, QHeaderView, QHBoxLayout, QAbstractItemView, QPushButton, QSizePolicy
from PyQt6.QtGui import QAction, QFont
from PyQt6.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel
from PyQt6.QtCore import Qt, QTime
import pyqtgraph as pg
from tools import flattenIntervals, plotAuras
import time, datetime
from dateutil.parser import parse as timeparse
import zipfile, rarfile
import parser, pet_recognition

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
            self.db = QSqlDatabase.addDatabase("QSQLITE")
            self.db.setDatabaseName(self.file_name)
            if not self.db.open():
                print("Unable to open data source file.")
                sys.exit(1) # Error code 1 - signifies error
            tables_needed = {"events", "encounters", "actors"}
            tables_not_found = tables_needed - set(self.db.tables())
            if tables_not_found:
                QMessageBox.critical(None, "Error", f"<p>The following tables are missing from the database: {tables_not_found}</p>")
                sys.exit(1) # Error code 1 - signifies error
            self.setUpMainWindow()
    
    def setUpMainWindow(self):
        self.create_pet_editing_window = None
        self.encounter_select = QComboBox()
        self.main_vbox.addWidget(self.encounter_select)
        encounter_query = QSqlQuery()
        encounter_query.exec("SELECT enemy, timeStart, timeEnd, isKill FROM encounters ORDER BY timeStart")
        while (encounter_query.next()):
            self.encounter_select.addItem(f"{encounter_query.value(0)} ({'kill' if encounter_query.value(3) else 'wipe'}) - {encounter_query.value(1)} | {encounter_query.value(2)}", (encounter_query.value(1), encounter_query.value(2)))
        self.encounter_select.currentTextChanged.connect(self.updateMainQuery)
        self.encounter_select.currentTextChanged.connect(self.updateUnitList)

        self.meter_select = QComboBox()
        self.main_vbox.addWidget(self.meter_select)
        self.meter_select.addItems(METERS)
        self.meter_select.currentTextChanged.connect(self.updateUnitList)

        self.source_select = QComboBox()
        self.source_select.currentTextChanged.connect(self.updateMainQuery)
        self.target_select = QComboBox()
        self.target_select.currentTextChanged.connect(self.updateMainQuery)
        self.source_current = FRIENDLY
        self.target_current = HOSTILE
        self.source_affiliation = 1
        self.target_affiliation = 0
        self.source_clear_button = QPushButton("X", self)
        self.source_clear_button.setMaximumSize(24, 24)
        self.source_clear_button.clicked.connect(self.resetSourceSelection)
        self.target_clear_button = QPushButton("X", self)
        self.target_clear_button.setMaximumSize(24, 24)
        self.target_clear_button.clicked.connect(self.resetTargetSelection)
        self.actors_swap_button = QPushButton(AFFILIATION[self.source_affiliation], self)
        self.actors_swap_button.setMaximumSize(75, 24)
        self.actors_swap_button.clicked.connect(self.swapAffiliation)

        self.actors_hbox = QHBoxLayout()
        self.actors_hbox.addWidget(self.source_clear_button)
        self.actors_hbox.addWidget(self.source_select)
        self.actors_hbox.addWidget(self.actors_swap_button)
        self.actors_hbox.addWidget(self.target_select)
        self.actors_hbox.addWidget(self.target_clear_button)
        self.main_vbox.addLayout(self.actors_hbox)

        self.graph = pg.PlotWidget()
        self.main_vbox.addWidget(self.graph)

        self.model = QSqlTableModel()
        self.table = QTableView()
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.clicked.connect(self.tableClicked)
        self.table.setModel(self.model)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.model.select()
        self.main_vbox.addWidget(self.table)

        self.updateUnitList()
        print('setup done')

    def updateMainQuery(self):
        meter = self.meter_select.currentText()
        self.graph.hide()
        if meter == DAMAGEDONE:
            self.queryDamageDone()
        elif meter == DAMAGETAKEN:
            self.queryDamageTaken()
        elif meter == HEALING:
            self.queryHealing()
        elif meter == DEATHS:
            self.queryDeaths()
        elif meter == BUFFS:
            self.queryBuffs()
        else:
            self.display_query = QSqlQuery()
            self.model.setQuery(self.display_query)
        print('query done')

    def queryDamageDone(self):
        display_query = QSqlQuery()
        if self.source_select.currentData() == AFFILIATION[self.source_affiliation]:
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
        self.model.setQuery(display_query)

    def queryDamageTaken(self):
        display_query = QSqlQuery()
        if self.source_select.currentData() == AFFILIATION[self.source_affiliation]:
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
        self.model.setQuery(display_query)

    def queryHealing(self):
        display_query = QSqlQuery()
        if self.source_select.currentData() == AFFILIATION[self.source_affiliation]:
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
        self.model.setQuery(display_query)

    def queryDeaths(self, timestamp = None):
        display_query = QSqlQuery()
        if timestamp:
            with open('queries/deaths_1.sql', 'r') as f:
                display_query.prepare(f.read())
            display_query.bindValue(":targetName", self.source_select.currentText())
            display_query.bindValue(":endTime", timestamp)
            display_query.bindValue(":startTime", self.encounter_select.currentData()[0])
            display_query.exec()
            self.model.setQuery(display_query)
        elif self.source_select.currentData() == AFFILIATION[self.source_affiliation]:
            with open('queries/deaths_all.sql', 'r') as f:
                display_query.prepare(f.read())
            display_query.bindValue(":affiliation", self.source_affiliation)
            display_query.bindValue(":endTime", self.encounter_select.currentData()[1])
            display_query.bindValue(":startTime", self.encounter_select.currentData()[0])
            display_query.exec()
            self.model.setQuery(display_query)
        else:
            self.source_select.setCurrentIndex(0)

    def queryBuffs(self):
        q = QSqlQuery()
        with open('queries/buffs_taken_1-all.sql', 'r') as f:
            q.prepare(f.read())
        q.bindValue(":startTime", self.encounter_select.currentData()[0])
        q.bindValue(":endTime", self.encounter_select.currentData()[1])
        q.bindValue(":targetGUID", self.source_select.currentData())
        q.exec()
        self.auras_current = {}
        while q.next():
            if q.value(1) not in self.auras_current:
                self.auras_current[q.value(1)] = {'spellName': q.value(0), 'intervals': []}
            self.auras_current[q.value(1)]['intervals'].append((q.value(2), q.value(3)))
        encounter_length = timeparse(self.encounter_select.currentData()[1]) - timeparse(self.encounter_select.currentData()[0])
        q.exec("DROP TABLE IF EXISTS temp_buff")
        q.exec("CREATE TEMP TABLE temp_buff (spellID MEDIUMINT UNSIGNED UNIQUE NOT NULL, spellName VARCHAR(50), count SMALLINT UNSIGNED, uptime TIMESTAMP, uptimepct FLOAT)")
        q.prepare("INSERT INTO temp_buff (spellID, spellName, count, uptime, uptimepct) VALUES (:spellID, :spellName, :count, :uptime, :uptimepct)")
        for k in self.auras_current:
            self.auras_current[k]['count'] = len(self.auras_current[k]['intervals'])
            self.auras_current[k]['intervals'] = flattenIntervals(self.auras_current[k]['intervals'])
            uptime = datetime.timedelta()
            for x in self.auras_current[k]['intervals']:
                uptime += timeparse(x[1]) - timeparse(x[0])
            self.auras_current[k]['uptime'] = uptime
            self.auras_current[k]['uptimepct'] = uptime / encounter_length * 100
            q.bindValue(':spellID', k)
            q.bindValue(':spellName', self.auras_current[k]['spellName'])
            q.bindValue(':count', self.auras_current[k]['count'])
            q.bindValue(':uptime', str(self.auras_current[k]['uptime']))
            q.bindValue(':uptimepct', self.auras_current[k]['uptimepct'])
            q.exec()
        display_query = QSqlQuery()
        display_query.exec("SELECT spellName, uptimepct, uptime, count, spellID FROM temp_buff ORDER BY uptimepct DESC")
        self.model.setQuery(display_query)

    def updateUnitList(self):
        self.source_select.disconnect()
        self.target_select.disconnect()
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
        while (unit_query.next()):
            #Take into account mind controlled NPC as friendly (isPet = 1, isNPC = 1)
            if unit_query.value(1) == self.source_affiliation or unit_query.value(3) == 1 - self.source_affiliation or (unit_query.value(2) and self.source_affiliation):
                self.source_select.addItem(f"{'(pet) ' if unit_query.value(2) and not unit_query.value(3) else ''}{unit_query.value(0)}", unit_query.value(4))
            if unit_query.value(1) == self.target_affiliation or unit_query.value(3) == 1 - self.target_affiliation or (unit_query.value(2) and self.target_affiliation):
                self.target_select.addItem(f"{'(pet) ' if unit_query.value(2) and not unit_query.value(3) else ''}{unit_query.value(0)}", unit_query.value(4))
        self.source_select.currentTextChanged.connect(self.updateMainQuery)
        self.target_select.currentTextChanged.connect(self.updateMainQuery)
        if self.source_current:
            index = self.source_select.findData(self.source_current)
            self.source_select.setCurrentIndex(0 if index == -1 else index)
        else:
            self.source_select.setCurrentIndex(0)
        if self.target_current:
            index = self.target_select.findData(self.target_current)
            self.target_select.setCurrentIndex(0 if index == -1 else index)
        self.updateMainQuery()

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
        if meter in (DAMAGEDONE, DAMAGETAKEN):
            self.target_affiliation = 1 - self.source_affiliation
        elif meter in (HEALING):
            self.target_affiliation = self.source_affiliation
        else:
            self.target_affiliation = 0

    def tableClicked(self, item):
        if (new_source := self.source_select.findText(item.siblingAtColumn(0).data())) != -1:
            self.source_select.setCurrentIndex(new_source)
        elif self.meter_select.currentText() == DEATHS:
            ts = item.siblingAtColumn(5).data()
            #Hacky disconnect, may want to revisit the source list selector (and add death timestamp to the data)
            self.source_select.disconnect()
            self.source_select.setCurrentIndex(self.source_select.findText(item.siblingAtColumn(1).data()))
            self.source_select.currentTextChanged.connect(self.updateMainQuery)
            self.queryDeaths(ts)
        elif self.meter_select.currentText() == BUFFS:
            self.plotAuraGraph(item.siblingAtColumn(4).data())
    
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
            

class TimeAxisItem(pg.AxisItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def tickStrings(self, values, scale, spacing):
        return [QTime().addMSecs(value).toString('mm:ss') for value in values]



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())
