## WotLK-LogParser

Parse and view combat logs of World of Warcraft WotLK

### 0.1.3
Bugfix:
* Fixed parsing of fully absorbed hits
* The swap button now forces a refresh of the table
* Damage Done/Taken meters now should work properly in all cases (1/all sources/targets selected)

### 0.1.2
New:
* Added setup for target selection (currently inactive, will only query 'all targets'), with a button to return to global selection
* Added a meter selection
* Added Damage Taken meter

Tweaks:
* Improved source/target list handling

### 0.1.1
New:
* When on the global damage meter, clicking on a row will open the damage breakdown of the selected character/pet
* Added a button to return to the global damage meter (for the selected encounter)
* Changing encounter updates the source to characters that participated in the fight (instead of grabbing a list from the whole log)
* Changing encounter will keep the current player selected, even if they did not participate, to prevent having to re-select them

### 0.1.0

Functionalities:
* Parse a WoWCombatLog.txt file into a usable database for quick data retrieval. This includes computing supplementary information, like identifying player- and server-controlled entities, establishing start/end time of boss encounters (in WotLK there is no event API for it), etc.
* Visualise the damage meter of a pre-parsed log. Currently limited to selecting an encounter, and displaying either the damage meter of the raid or the damage breakdown of a selected friendly unit (players and pets are currently decoupled).

----

Upcoming tasks:
* Add healing log
* Add death log
* Add auras analysis (e.g. uptime)
* Add absorb log
* Add a graph for the currently selected meter
* Add recognition of player classes
* Coupling of pets/owners - permanent pets may require additional widgets to manually select their owner
* Add bars on meters, display total and percentage on meters additionally to raw numbers
* Add passing a .rar or .zip file containing the WoWCombatLog.txt to analyse
