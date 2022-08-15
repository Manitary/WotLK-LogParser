from email.parser import Parser
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox, QTextEdit, QFileDialog, QInputDialog, QFontDialog, QColorDialog, QComboBox, QLabel, QVBoxLayout, QWidget, QTableView, QHeaderView, QHBoxLayout
from PyQt6.QtGui import QAction, QFont
from PyQt6.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel
from PyQt6.QtCore import Qt
import zipfile, rarfile
import parser, parser

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

        self.actors_hbox = QHBoxLayout()
        self.source_select = QComboBox()
        self.target_select = QComboBox()
        self.actors_hbox.addWidget(self.source_select)
        self.actors_hbox.addWidget(self.target_select)
        self.main_vbox.addLayout(self.actors_hbox)
        self.source_select.addItem("All friendly", "AllFriendlyUnits")
        source_query = QSqlQuery()
        source_query.exec("SELECT unitName, isPet FROM actors WHERE isPlayer = 1 OR isPet = 1 GROUP BY unitName ORDER BY isPlayer DESC, unitName")
        while (source_query.next()):
            self.source_select.addItem(f"{'(pet) ' if source_query.value(1) else ''}{source_query.value(0)}", source_query.value(0))
        self.source_select.currentTextChanged.connect(self.updateMainQuery)
        
        self.model = QSqlTableModel()
        #self.model.setQuery(QSqlQuery("SELECT events.sourceName AS char, SUM(events.amount) AS dmg FROM events JOIN actors ON (events.sourceGUID = actors.unitGUID) WHERE events.timestamp >= '12/13 20:06:22.323' AND events.timestamp <= '12/13 20:09:45.129' AND (actors.isPlayer = 1 OR actors.isPet = 1) AND events.eventName LIKE '%DAMAGE' GROUP BY events.sourceName ORDER BY dmg DESC"))
        table = QTableView()
        table.setModel(self.model)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.model.select()
        self.main_vbox.addWidget(table)
        print('done')

    def updateMainQuery(self):
        self.display_query = QSqlQuery()
        if self.source_select.currentData() == "AllFriendlyUnits":
            self.display_query.prepare("SELECT events.sourceName AS char, SUM(events.amount) AS dmg FROM events JOIN actors ON (events.sourceGUID = actors.unitGUID) WHERE events.timestamp >= :startTime AND events.timestamp <= :endTime AND (actors.isPlayer = 1 OR actors.isPet = 1) AND events.eventName LIKE '%DAMAGE' GROUP BY events.sourceName ORDER BY dmg DESC")
        else:
            with open('queries/player_damage_breakdown.sql', 'r') as f:
                self.display_query.prepare(f.read())
            self.display_query.bindValue(":sourceName", self.source_select.currentData())
        self.display_query.bindValue(":startTime", self.encounter_select.currentData()[0])
        self.display_query.bindValue(":endTime", self.encounter_select.currentData()[1])
        self.display_query.exec()
        self.model.setQuery(self.display_query)
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())
