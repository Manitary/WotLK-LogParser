## WotLK-LogParser

Parse and view combat logs of World of Warcraft WotLK

### 0.1.0

Functionalities:
* Parse a WoWCombatLog.txt file into a usable database for quick data retrieval. This includes computing supplementary information, like identifying player- and server-controlled entities, establishing start/end time of boss encounters (in WotLK there is no event API for it), etc.
* Visualise the damage meter of a pre-parsed log. Currently limited to selecting an encounter, and displaying either the damage meter of the raid or the damage breakdown of a selected friendly unit (players and pets are currently decoupled).

Upcoming tasks:
* Add widget interactions (e.g. click on a player in the table to see their breakdown for the fight)
* Add healing log, and a widget to swap between various types of logs
* Add death log
* Add damage taken log
* Add auras analysis (e.g. uptime)
* Add absorb log
* Add a graph for the currently selected meter
* Add recognition of player classes
* Coupling of pets/owners - permanent pets may require additional widgets to manually select their owner
* Add bars on meters, display total and percentage on meters additionally to raw numbers
* Add passing a .rar or .zip file containing the WoWCombatLog.txt to analyse
