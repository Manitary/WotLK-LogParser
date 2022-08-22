from PyQt6.QtWidgets import QDialog, QLabel, QPushButton, QMessageBox, QVBoxLayout, QCheckBox, QComboBox, QGridLayout, QHBoxLayout, QStyle, QLineEdit
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from PyQt6.QtSql import QSqlQuery
from pathlib import Path

permanent_pet_spells = {
    #Death Knight
    'Ghoul Frenzy': {
        'spellID': (63560,),
        'eventName': ('SPELL_AURA_APPLIED', 'SPELL_AURA_REMOVED', 'SPELL_PERIODIC_HEAL',),
        'owner': 'source',
    },
    'Death Coil': {
        'spellID': (47541, 49892, 49893, 49894, 49895,),
        'eventName': ('SPELL_HEAL',),
        'owner': 'source',
    },
    #Warlock
    'Soul Link': {
        'spellID': (25228,),
        'eventName': ('SPELL_AURA_APPLIED', 'SPELL_AURA_REMOVED',),
        'owner': 'target',
    },
    'Demonic Knowledge': {
        'spellID': (35696,),
        'eventName': ('SPELL_AURA_APPLIED', 'SPELL_AURA_REMOVED',),
        'owner': 'target',
    },
    'Master Demonologist': {
        'spellID': (35702, 35703, 35704, 35705, 35706,),
        'eventName': ('SPELL_AURA_APPLIED', 'SPELL_AURA_REMOVED',),
        'owner': 'target',
    },
    'Empowered Imp': {
        'spellID': (47283,),
        'eventName': ('SPELL_AURA_APPLIED', 'SPELL_AURA_REMOVED',),
        'owner': 'target',
    },
    'Health Funnel': {
        'spellID': (755, 3698, 3699, 3700, 11693, 11694, 11695, 27259, 47856,),
        'eventName': ('SPELL_AURA_APPLIED', 'SPELL_AURA_REMOVED, SPELL_PERIODIC_HEAL',),
        'owner': 'source',
    },
    #Hunter
    'Feed Pet': {
        'spellID': (1539,),
        'eventName': ('SPELL_AURA_APPLIED', 'SPELL_AURA_REMOVED',),
        'owner': 'source',
    },
    'Mend Pet': {
        'spellID': (136, 3111, 3661, 3662, 13542, 13543, 13544, 27046, 48989, 48990,),
        'eventName': ('SPELL_AURA_APPLIED', 'SPELL_AURA_REMOVED', 'SPELL_PERIODIC_HEAL',),
        'owner': 'source',
    },
    'Culling the Herd': {
        'spellID': (70893,),
        'eventName': ('SPELL_AURA_APPLIED', 'SPELL_AURA_REMOVED'),
        'owner': 'target',
    },
    'Call of the Wild': {
        'spellID': (53434,),
        'eventName': ('SPELL_AURA_APPLIED', 'SPELL_AURA_REMOVED'),
        'owner': 'target',
    },
    'Furious Howl': {
        'spellID': (24604, 64491, 64492, 64493, 64494, 64495,),
        'eventName': ('SPELL_AURA_APPLIED', 'SPELL_AURA_REMOVED'),
        'owner': 'target',
    },
}

temporary_pet_spells = {
    #Mage
    'Mirror Image1': (58831,),
    'Mirror Image2': (58832,),
    'Mirror Image3': (58833,),
    'Mirror Image4': (58834,),
    #Shaman
    'Cleansing Totem': (8170,),
    'Earth Elemental Totem': (2062,),
    'Earthbind Totem': (2484,),
    'Feral Spirit': (51533,),
    'Fire Elemental Totem': (2894,),
    'Fire Resistance Totem': (8184, 10537, 10538, 25563, 58737, 58739,),
    'Flametongue Totem': (8227, 8249, 10526, 16387, 25557, 58649, 58652, 58656,),
    'Frost Resistance Totem': (8181, 10478, 10479, 25560, 58741, 58745,),
    'Grounding Totem': (8177,),
    'Healing Stream Totem': (5394, 6375, 6377, 10462, 10463, 25567, 58755, 58756, 58757,),
    'Magma Totem': (8190, 10585, 10586, 10587, 25552, 58731, 58734,),
    'Mana Spring Totem': (5675, 10495, 10496, 10497, 25570, 58771, 58773, 58774),
    'Mana Tide Totem': (16190,),
    'Nature Resistance Totem': (10595, 10600, 10601, 25574, 58746, 58749,),
    'Searing Totem': (3599, 6363, 6364, 6365, 10437, 10438, 25533, 58699, 58703, 58704,),
    'Stoneclaw Totem': (5730, 6390, 6391, 6392, 10427, 10428, 25525, 58580, 58581, 58582,),
    'Stoneskin Totem': (8071, 8154, 8155, 10406, 10407, 10408, 25508, 25509, 58751, 58753,),
    'Strength of Earth Totem': (8075, 8160, 8161, 10442, 25361, 25528, 57622, 58643,),
    'Totem of Wrath': (30706, 57720, 57721, 57722,),
    'Tremor Totem': (8143,),
    'Windfury Totem': (8512,),
    'Wrath of Air Totem': (3738,),
    #Death Knight
    'Dancing Rune Weapon': (49028,),
    'Summon Gargoyle': (49206,),
    'Raise Dead': (46585,),
    'Army of the Dead': (42651,),
    #Priest
    'Shadowfiend': (34433,),
    #Druid
    'Force of Nature': (33831,),
}

pet_summon_pet = {
    'Fire Elemental Totem': (32982,),
    'Earth Elemental Totem': (33663,),
}

class PetEditing(QDialog):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.initializeUI()

    def initializeUI(self):
        self.setMinimumWidth(700)
        self.setFixedHeight(200)
        self.setWindowTitle(Path(self.parent().file_name).name)
        self.setUpWindow()
    
    def setUpWindow(self):
        self.allGUID = True
        self.unassignedOnly = False
        self.main_vbox = QVBoxLayout()
        self.all_pets_cb = QCheckBox("Unassigned pets only", self)
        self.all_pets_cb.toggled.connect(self.toggleUnassigned)
        self.show_guid_cb = QCheckBox("Separate pets by GUID", self)
        self.show_guid_cb.toggled.connect(self.toggleAllGUID)
        self.pet_label = QLabel("Pet")
        self.pet_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pet_selector = QComboBox()
        self.current_owner_label = QLabel("Current owner")
        self.current_owner_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.current_owner = QLineEdit('-')
        self.current_owner.setEnabled(False)
        self.owner_label = QLabel("Owner")
        self.owner_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.owner_selector = QComboBox()
        self.owner_clear = QPushButton("X", self)
        self.owner_clear.setMaximumSize(24, 24)
        self.owner_clear.clicked.connect(self.clearOwner)
        self.owner_layout = QHBoxLayout()
        self.owner_layout.addWidget(self.owner_selector)
        self.owner_layout.addWidget(self.owner_clear)
        self.main_grid = QGridLayout()
        self.main_grid.addWidget(self.pet_label, 0, 0)
        self.main_grid.addWidget(self.current_owner_label, 0, 1)
        self.main_grid.addWidget(self.owner_label, 0, 2)
        self.main_grid.addWidget(self.pet_selector, 1, 0)
        self.main_grid.addWidget(self.current_owner, 1, 1)
        self.main_grid.addLayout(self.owner_layout, 1, 2)
        self.link_button = QPushButton("Update", self)
        self.link_button.clicked.connect(self.updateOwnership)
        self.ok_button = QPushButton("Done", self)
        self.ok_button.clicked.connect(self.close)
        self.main_vbox.addWidget(self.all_pets_cb)
        self.main_vbox.addWidget(self.show_guid_cb)
        self.main_vbox.addLayout(self.main_grid)
        self.main_vbox.addWidget(self.link_button)
        self.main_vbox.addWidget(self.ok_button)
        self.setLayout(self.main_vbox)
        self.all_pets_cb.toggle()
        self.show_guid_cb.toggle()
        self.updateOwnersList()
        self.pet_selector.textActivated.connect(self.currentOwner)
        
    def updateOwnersList(self):
        q = QSqlQuery()
        q.exec("SELECT unitName, unitGUID FROM actors WHERE isPlayer = 1 ORDER BY unitName")
        self.owner_selector.clear()
        self.owner_selector.addItem('-', (None, None))
        while (q.next()):
            self.owner_selector.addItem(q.value(0), (q.value(0), q.value(1)))

    def clearOwner(self):
        self.owner_selector.setCurrentIndex(0)

    def currentOwner(self):
        q = QSqlQuery()
        if self.allGUID:
            q.prepare("SELECT ownerName FROM pets WHERE petName = :petName AND petGUID = :petGUID")
            q.bindValue(':petGUID', self.pet_selector.currentData()[1])
            q.bindValue(':petName', self.pet_selector.currentData()[0])
            q.exec()
            if (q.next()):
                self.current_owner.setText(q.value(0))
            else:
                self.current_owner.setText('-')
        else:
            q.prepare("SELECT a.unitName, p.ownerName FROM actors a LEFT JOIN pets p ON a.unitGUID = p.petGUID WHERE a.isPet = 1 AND a.unitName = :petName")
            q.bindValue(':petName', self.pet_selector.currentData()[0])
            q.exec()
            owners = {}
            while (q.next()):
                owner = q.value(1) or 'Unknown'
                if owner in owners:
                    owners[owner] += 1
                else:
                    owners[owner] = 1
            self.current_owner.setText(', '.join(f"{owner} ({owners[owner]})" for owner in owners))

    def updatePetList(self):
        q = QSqlQuery()
        if self.allGUID:
            if self.unassignedOnly:
                q.exec("SELECT unitName, unitGUID FROM actors LEFT JOIN pets ON actors.unitGUID = pets.petGUID WHERE actors.isPet = 1 AND pets.ownerGUID IS NULL ORDER BY unitName, unitGUID")
            else:
                q.exec("SELECT unitName, unitGUID FROM actors LEFT JOIN pets ON actors.unitGUID = pets.petGUID WHERE actors.isPet = 1 ORDER BY unitName, unitGUID")
        else:
            if self.unassignedOnly:
                q.exec("SELECT unitName, unitGUID FROM actors LEFT JOIN pets ON actors.unitGUID = pets.petGUID WHERE actors.isPet = 1 AND pets.ownerGUID IS NULL GROUP BY unitName ORDER BY unitName")
            else:
                q.exec("SELECT unitName, unitGUID FROM actors LEFT JOIN pets ON actors.unitGUID = pets.petGUID WHERE actors.isPet = 1 GROUP BY unitName ORDER BY unitName")
        self.pet_selector.clear()
        self.pet_selector.addItem('-', (None, None))
        while (q.next()):
            self.pet_selector.addItem(f"{q.value(0)}{f' ({q.value(1)})' if self.allGUID else ''}", (q.value(0), q.value(1)))
    
    def toggleAllGUID(self, checked):
        self.allGUID = checked
        self.updatePetList()
    
    def toggleUnassigned(self, checked):
        self.unassignedOnly = checked
        self.updatePetList()

    def updateOwnership(self):
        answer = QMessageBox.question(self, "Confirm?", "Confirm changes?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if answer == QMessageBox.StandardButton.Yes:
            self.parent().db.transaction()
            q = QSqlQuery()
            name, guid = self.owner_selector.currentData()
            if self.allGUID:
                if name:
                    q.prepare("INSERT INTO pets (petGUID, petName, ownerGUID, ownerName) VALUES (:petGUID, :petName, :ownerGUID, :ownerName) ON DUPLICATE KEY UPDATE ownerGUID = :ownerGUID, ownerName = :ownerName")
                    q.bindValue(':petName', self.pet_selector.currentData()[0])
                    q.bindValue(':petGUID', self.pet_selector.currentData()[1])
                    q.bindValue(':ownerName', name)
                    q.bindValue(':ownerGUID', guid)
                else:
                    q.prepare("DELETE FROM pets WHERE petName = :petName AND petGUID = :petGUID")
                    q.bindValue(':petName', self.pet_selector.currentData()[0])
                    q.bindValue(':petGUID', self.pet_selector.currentData()[1])
                q.exec()
            else:
                if name:
                    s = QSqlQuery()
                    s.prepare("SELECT unitName, unitGUID FROM actors WHERE isPet = 1 AND unitName = :petName")
                    s.bindValue(':petName', self.pet_selector.currentData()[0])
                    s.exec()
                    q.prepare("INSERT OR REPLACE INTO pets (petGUID, petName, ownerGUID, ownerName) VALUES (:petGUID, :petName, :ownerGUID, :ownerName)")
                    while (s.next()):
                        q.bindValue(':petName', s.value(0))
                        q.bindValue(':petGUID', s.value(1))
                        q.bindValue(':ownerName', name)
                        q.bindValue(':ownerGUID', guid)
                        q.exec()
                else:
                    q.prepare("DELETE FROM pets WHERE petName = :petName")
                    q.bindValue(':petName', self.pet_selector.currentData()[0])
                    q.exec()
            self.parent().db.commit()
            QMessageBox.information(self, "Done", "Done", QMessageBox.StandardButton.Ok)
            self.currentOwner()

