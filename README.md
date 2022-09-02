# WotLK-LogParser

A personal mini-project to create a program to parse and view combat logs of World of Warcraft WotLK locally.

It may become deprecated as soon as WotLK Classic is released, except for private servers that run the original WotLK.

## 0.5.5
New:
* Add spec icon to the unit selection menu
* The death log now filter deaths based on the selected unit. Visualising the death recap still requires interaction with the displayed table

Bugfix:
* Opening more than one parse in the same session does not longer result in unwanted behaviour of the application
* The currently selected unit no longer resets when selecting a different meter or encounter (provided it is still a suitable unit)
* The currently select unit now resets when opening another parse, even in the case of a valid unit

----

## Known issues:

* Hunter's Feign Death does not appear in the CombatLog -> extra 'deaths' in the Death Log
* Parsing is very slow (1M entries take 30+ minutes)
* Aura tracking may be inaccurate, possibly due to bugs, but mostly due to how poor the Combat Log is in this regard.
* Encounter parsing has some issues, like identifying wipe or kill on multi-target fights (e.g. The Four Horsemen)

----

## Upcoming features (hopefully)

* Add pet <-> owner pairing of creatures summoned by Snake Trap 
* Improve auras analysis (e.g. uptime)
* Improve encounter parsing
* Add absorb log
* Add a graph for the currently selected meter
* Add a button to re-parse pet <-> owner coupling, to rewind mistakes done with manual pairing
* Add passing a .rar or .zip file containing the WoWCombatLog.txt to analyse
* Beautify even more

----

## Example pictures:

Unit selection menu

![Unit selection menu](https://i.imgur.com/81S4x5B.png)

Damage meter

![Damage meter](https://i.imgur.com/la1Hike.png)

Damage breakdown

![Damage breakdown](https://i.imgur.com/47KA9Qn.png)

Damage Taken meter

![Damage Taken meter](https://i.imgur.com/Y0GRlb2.png)

Damage Taken breakdown

![Damage Taken breakdown](https://i.imgur.com/g0Rcgt2.png)

Healing Meter

![Healing Meter](https://i.imgur.com/6Fhmk7x.png)

Healing breakdown

![Healing breakdown](https://i.imgur.com/J8lZm61.png)

Death log

![Death log](https://i.imgur.com/wDBTpgr.png)

Death log of a unit

![Death log of a unit](https://i.imgur.com/B89l2pn.png)

Death recap

![Death recap](https://i.imgur.com/4KDNtYw.png)

Buff uptime

![Buff uptime](https://i.imgur.com/jrOAFid.png)

Manual pet assignment

![Manual pet assignment](https://i.imgur.com/YWHBwKF.png)

----

## Past versions

### 0.5.4
New:
* Display a bar visualisation of damage and healing meters
* Improve graphics across all meters and death log

Bugfix:
* The death log now behaves properly when multiple events are registered with the same timestamp
* Unassigned pets are now displayed appropriately in global damage and healing meters

### 0.5.3
New:
* Added spec tracking, for each encounter
* Added spec/spell icon on meters/breakdown
* Improved visual display of meters/breakdown

### 0.5.2
New:
* Added buff uptime tracking, and a simple uptime graph. Has some limitations mostly due to how the Combat Log works.

Tweaks:
* Death recap: now it shows all possibly relevant events since the unit was at full HP (last overhealing received / beginning of the encounter).
* Death recap: Improved readability of damage/healing information.

Bugfix:
* Fixed an issue with encounter parsing.

### 0.5.1
New:
* Added the possibility to manually (re)assign pets to an owner. Useful for named pets (Warlock, Hunter, Unholy DK) or for single-class temporary pets (e.g. Treants with a single Balance Druid among friendly units).

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

