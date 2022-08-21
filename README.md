## WotLK-LogParser

A personal mini-project to create a program to parse and view combat logs of World of Warcraft WotLK locally.
It may become deprecated as soon as WotLK Classic is released, except for private servers that run the original WotLK.

### 0.4.1
New:
* Added automatic coupling of pet <-> pet owner during parsing. It will not always work, for example with permanent pets that never interact with their owner (through buffs/heals) or with temporary pets for which the summon event is not registered in the combat log for any reason.
* Pets are now merged with their owner in the meter, both damage and healing. Pets with an unknown owner will still be displayed separately.

### 0.3.1
New:
* Added Deaths log, including death breakdown up until 5 seconds before the killing blow.
Known bug:
* Hunter's Feign Death is not tracked in the the Combat Log, resulting in false positives in the Deaths log. They can be spotted as the killing blow deals 0 overkill damage.
Bugfix:
* Fixed timestamp parsing.

### 0.2.1
New:
* Added healing meter. Absorbs are not included until auras are implemented (WotLK does not have proper absorb tracking, only amount of spell/swing damage absorbed with no additional info).
Bugfix:
* Affiliation of the target list should change according to the chosen meter (A<->A for healing, A<->B for damage).

### 0.1.3
Bugfix:
* Fixed parsing of fully absorbed hits.
* The swap button now forces a refresh of the table.
* Damage Done/Taken meters now should work properly in all cases (1/all sources/targets selected).

### 0.1.2
New:
* Added setup for target selection (currently inactive, will only query 'all targets'), with a button to return to global selection.
* Added a meter selection.
* Added Damage Taken meter.

Tweaks:
* Improved source/target list handling.

### 0.1.1
New:
* When on the global damage meter, clicking on a row will open the damage breakdown of the selected character/pet.
* Added a button to return to the global damage meter (for the selected encounter).
* Changing encounter updates the source to characters that participated in the fight (instead of grabbing a list from the whole log).
* Changing encounter will keep the current player selected, even if they did not participate, to prevent having to re-select them.

### 0.1.0

Functionalities:
* Parse a WoWCombatLog.txt file into a usable database for quick data retrieval. This includes computing supplementary information, like identifying player- and server-controlled entities, establishing start/end time of boss encounters (in WotLK there is no event API for it), etc.
* Visualise the damage meter of a pre-parsed log. Currently limited to selecting an encounter, and displaying either the damage meter of the raid or the damage breakdown of a selected friendly unit (players and pets are currently decoupled).

----

## To do (hopefully)

Upcoming tasks:
* Add auras analysis (e.g. uptime)
* Add absorb log
* Add a graph for the currently selected meter
* Add recognition of player classes
* Add a widget to manually pair pet <-> owner - useful when automatic recognition is not possible (e.g. permanent pet never interacting with its owner)
* Add bars on meters, display total and percentage on meters additionally to raw numbers
* Improve detailed death log by including all events since the last time the unit was at full health (start of fight or latest overheal)
* Add passing a .rar or .zip file containing the WoWCombatLog.txt to analyse
* Beautify

Known issues:
* Hunter's Feign Death does not appear in the CombatLog -> extra 'deaths' in the Death Log
* Parsing is very slow (1M entries take 30+ minutes)

----

## Example pictures:

Encounter selection

![Encounter selection](https://i.imgur.com/zCeNXpq.png)

Overall / player selection

![Overall / player selection](https://i.imgur.com/DrPTkjl.png)

Damage breakdown

![Damage breakdown](https://i.imgur.com/aPmSNZf.png)

Damage Taken breakdown

![Damage Taken breakdown](https://i.imgur.com/9JswaVI.png)

Healing breakdown

![Healing breakdown](https://i.imgur.com/9YaiUOS.png)

Death log

![Death log](https://i.imgur.com/4tavP9Q.png)

Death recap

![Death recap](https://i.imgur.com/5A4wv6b.png)
