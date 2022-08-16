import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox, QTextEdit, QFileDialog, QInputDialog, QFontDialog, QColorDialog, QComboBox, QLabel, QVBoxLayout, QWidget, QTableView, QHeaderView, QHBoxLayout, QAbstractItemView, QPushButton, QSizePolicy
from PyQt6.QtGui import QAction, QFont
from PyQt6.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel
from PyQt6.QtCore import Qt
import zipfile, rarfile
import parser, parser

ALL = "AllUnits"
FRIENDLY = "Friendlies"
HOSTILE = "Enemies"
AFFILIATION = [HOSTILE, FRIENDLY]

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initializeUI()

    def initializeUI(self):
        self.setMinimumSize(450, 350)
        self.setWindowTitle("Parser")
        self.createActions()
        self.createMenu()
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.main_vbox = QVBoxLayout(self.centralWidget)
        self.show()

    def createActions(self):
        self.quit_act = QAction("Quit")
        self.quit_act.triggered.connect(self.close)
        self.parse_act = QAction("Parse a log")
        self.parse_act.triggered.connect(self.parseFile)
        self.open_act = QAction("Open a parse")
        self.open_act.triggered.connect(self.openParse)

    def createMenu(self):
        self.menuBar().setNativeMenuBar(False)
        file_menu = self.menuBar().addMenu("File")
        file_menu.addAction(self.open_act)
        file_menu.addAction(self.parse_act)
        #file_menu.addAction(self.quit_act)

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
        file_name, _ = QFileDialog.getOpenFileName(self, "Select parse", "parses/", "Databases (*.db)")
        db = QSqlDatabase.addDatabase("QSQLITE")
        db.setDatabaseName(file_name)
        if not db.open():
            print("Unable to open data source file.")
            sys.exit(1) # Error code 1 - signifies error
        tables_needed = {"events", "encounters", "actors"}
        tables_not_found = tables_needed - set(db.tables())
        if tables_not_found:
            QMessageBox.critical(None, "Error", f"<p>The following tables are missing from the database: {tables_not_found}</p>")
            sys.exit(1) # Error code 1 - signifies error
        self.setUpMainWindow()
        self.show()
    
    def setUpMainWindow(self):
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
        meters = ['Damage Done', 'Healing', 'Damage Taken', 'Deaths']
        self.meter_select.addItems(meters)
        self.meter_select.currentTextChanged.connect(self.updateMainQuery)

        self.actors_hbox = QHBoxLayout()
        self.source_select = QComboBox()
        self.target_select = QComboBox()
        self.source_clear_button = QPushButton("X", self)
        self.source_clear_button.setMaximumSize(24, 24)
        self.source_clear_button.clicked.connect(self.resetSourceSelection)
        self.target_clear_button = QPushButton("X", self)
        self.target_clear_button.setMaximumSize(24, 24)
        self.target_clear_button.clicked.connect(self.resetTargetSelection)
        self.affiliation = 1
        self.actors_swap_button = QPushButton(AFFILIATION[self.affiliation], self)
        self.actors_swap_button.setMaximumSize(75, 24)
        self.actors_swap_button.clicked.connect(self.swapActorsAffiliation)
        self.actors_hbox.addWidget(self.source_clear_button)
        self.actors_hbox.addWidget(self.source_select)
        self.actors_hbox.addWidget(self.actors_swap_button)
        self.actors_hbox.addWidget(self.target_select)
        self.actors_hbox.addWidget(self.target_clear_button)
        self.main_vbox.addLayout(self.actors_hbox)
        self.source_select.currentTextChanged.connect(self.updateMainQuery)
        self.source_current = FRIENDLY
        self.target_select.currentTextChanged.connect(self.updateMainQuery)
        self.target_current = HOSTILE

        self.model = QSqlTableModel()
        self.table = QTableView()
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.clicked.connect(self.tableClicked)
        self.table.setModel(self.model)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.model.select()
        self.main_vbox.addWidget(self.table)

        self.updateUnitList()
        self.updateMainQuery()
        print('done')

    def updateMainQuery(self):
        meter = self.meter_select.currentText()
        if meter == 'Damage Done':
            print('done')
            self.queryDamageDone()
        elif meter == 'Damage Taken':
            print('taken')
            self.queryDamageTaken()
        else:
            self.display_query = QSqlQuery()
            self.model.setQuery(self.display_query)

    def queryDamageDone(self):
        display_query = QSqlQuery()
        if self.source_select.currentData() == FRIENDLY:
            with open('queries/global_damage_done.sql', 'r') as f:
                display_query.prepare(f.read())
        else:
            with open('queries/player_damage_done_breakdown.sql', 'r') as f:
                display_query.prepare(f.read())
            display_query.bindValue(":sourceName", self.source_select.currentData())
        display_query.bindValue(":startTime", self.encounter_select.currentData()[0])
        display_query.bindValue(":endTime", self.encounter_select.currentData()[1])
        display_query.exec()
        self.model.setQuery(display_query)

    def queryDamageTaken(self):
        display_query = QSqlQuery()
        if self.source_select.currentData() == FRIENDLY:
            with open('queries/global_damage_taken.sql', 'r') as f:
                display_query.prepare(f.read())
        else:
            with open('queries/player_damage_taken_breakdown.sql', 'r') as f:
                display_query.prepare(f.read())
            display_query.bindValue(":targetName", self.source_select.currentData())
        display_query.bindValue(":startTime", self.encounter_select.currentData()[0])
        display_query.bindValue(":endTime", self.encounter_select.currentData()[1])
        display_query.exec()
        self.model.setQuery(display_query)

    def queryHealing(self):
        pass

    def queryDeaths(self):
        pass

    def updateUnitList(self):
        self.source_select.disconnect()
        self.target_select.disconnect()
        if self.source_select.currentData():
            self.source_current = self.source_select.currentData()
        if self.target_select.currentData():
            self.target_current = self.target_select.currentData()
        self.source_select.clear()
        self.target_select.clear()

        self.source_select.addItem(f"All {AFFILIATION[self.affiliation]}", AFFILIATION[self.affiliation])
        self.target_select.addItem(f"All {AFFILIATION[1 - self.affiliation]}", AFFILIATION[1 - self.affiliation])
        
        unit_query = QSqlQuery()
        with open('queries/find_actors.sql', 'r') as f:
            unit_query.prepare(f.read())
        unit_query.bindValue(":startTime", self.encounter_select.currentData()[0])
        unit_query.bindValue(":endTime", self.encounter_select.currentData()[1])
        unit_query.exec()
        while (unit_query.next()):
            #Take into account mind controlled NPC as friendly (isPet = 1, isNPC = 1)
            if unit_query.value(1) == self.affiliation or unit_query.value(3) == 1 - self.affiliation or (unit_query.value(2) and self.affiliation):
                self.source_select.addItem(f"{'(pet) ' if unit_query.value(2) and not unit_query.value(3) else ''}{unit_query.value(0)}", unit_query.value(0))
            if (unit_query.value(3) or 0) == self.affiliation or (unit_query.value(2) and not self.affiliation):
                self.target_select.addItem(f"{'(pet) ' if unit_query.value(2) and not unit_query.value(3) else ''}{unit_query.value(0)}", unit_query.value(0))
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

    def resetSourceSelection(self):
        self.source_select.setCurrentIndex(0)
    
    def resetTargetSelection(self):
        self.target_select.setCurrentIndex(0)

    def swapActorsAffiliation(self):
        self.affiliation = 1 - self.affiliation
        self.actors_swap_button.setText(AFFILIATION[self.affiliation])
        self.updateUnitList()

    def tableClicked(self, item):
        if (new_source := self.source_select.findText(item.siblingAtColumn(0).data())) != -1:
            self.source_select.setCurrentIndex(new_source)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())
