# WotLK-LogParser

A personal mini-project to create a program to parse and view combat logs of World of Warcraft WotLK locally.

It may become deprecated as soon as WotLK Classic is released, except for private servers that run the original WotLK.

## 0.6.1
New:
* The pet assignment window now allows filtering by encounter, and shows the correct spec icon of possible owners accordingly. This should considerably simplify the process of manually assigning an owner to stranded pets
* The Deaths log loads noticeably faster
* Pets summoned by Snake Trap are automatically assigned an owner when parsing the combat log
* Improved detection of Frost Mage spec

Bugfix:
* Shadowfiend's and Greater Fire Elemental's melee attacks now should display the correct school (Shadow and Fire, respectively)
* The unit selection menu now shows the correct spec based on the selected encounter

----

## Known issues:

* Hunter's Feign Death does not appear in the CombatLog -> extra 'deaths' in the Death Log
* Snake Trap's pets may be incorrectly assigned in specific edge cases
* Pets meter do not display correctly
* Aura tracking may be inaccurate, possibly due to bugs, but mostly due to how poor the Combat Log is in this regard.
* Aura tracking may result in unwanted additional results for certain permanent auras (e.g. stance changes for DK, various permanent auras on pets)
* Encounter parsing has some issues, like identifying wipe or kill on multi-target fights (e.g. The Four Horsemen)
* Parsing is very slow (1M entries take 30+ minutes)

----

## Upcoming features (hopefully)

* Add a undo-redo function to quickly move through recently applied filters
* Add absorb log
* Add a graph for the currently selected meter
* Add a button to re-parse pet <-> owner coupling, to rewind mistakes done with manual pairing
* Add passing a .rar or .zip file containing the WoWCombatLog.txt to analyse
* Beautify even more

----

## Example pictures:

Unit selection menu

![Unit selection menu](https://i.imgur.com/WR6Wr6Z.png)

Damage breakdown, with tooltip example

![Damage breakdown](https://i.imgur.com/uSTir2f.png)

Damage Taken meter (includes a non-assigned pet)

![Damage Taken meter](https://i.imgur.com/ZTsnnZc.png)

Damage Taken breakdown, with tooltip example

![Damage Taken breakdown](https://i.imgur.com/u3vqOu5.png)

Healing Meter (does not include absorbs)

![Healing Meter](https://i.imgur.com/VbmHalh.png)

Healing breakdown, with tooltip example

![Healing breakdown](https://i.imgur.com/f7LeTlE.png)

Death log

![Death log](https://i.imgur.com/wDBTpgr.png)

Death log of a unit

![Death log of a unit](https://i.imgur.com/B89l2pn.png)

Death recap

![Death recap](https://i.imgur.com/4KDNtYw.png)

Buff uptime

![Buff uptime](https://i.imgur.com/jrOAFid.png)

----

## Example of manual pet assignment

In this fight (Patchwerk) there are 8 stranded Army of the Dead Ghoul, summoned by a DK through Army of the Dead:

![The combat log shows 8 stranded pets](https://i.imgur.com/eOrhCKO.png)

Opening the pet assigment window, we can select the encounter, and see that 16 Army of the Dead Ghoul participated in the fight, 8 of which are the stranded ones, while the other 8 are already assigned to a DK:

![Check the pet owners](https://i.imgur.com/MQOrqSL.png)

We can assign an owner to the 8 stranded Army of the Dead Ghoul by selecting the other DK from the player list and updating:

![Assign an owner to the pets without one](https://i.imgur.com/bCrBzOa.png)

After closing the pet assignment window, we can confirm the successfull assignment:

![The stranded pets now appear in the correct owner's meter](https://i.imgur.com/qFm6KUf.png)

----

## Past versions

### 0.6
New:
* Added tooltip tables on relevant columns of various meters (Damage Done/Taken, Healing Done)
* Added a toggle to swap between gained and applied (de)buffs
* Added the option to filter a single buff
* Interacting with the buff table should now filter results properly

Bugfix:
* Fixed an issue with simultaneous death events that resulted in missing entries
* Fixed an issue with sorting simultaneous events in death logs
* Crit % is now displayed in damage breakdown tables
* Damage Done calculations now take fully absorbed hits into account
* Fully blocked or resisted hits are now parsed correctly
* Table columns should now automatically resize in the intended way
* Changed damage taken calculations: the total amount only includes effective and absorbed damage, as blocked and resisted damage need not to be healed or shielded from
* Fixed various other calculations in the breakdown tables
* Units with the same name should now be merged in both damage and healing global meters
* Fixed some issues with displaying the colour of multi-school spells, or of aggregated spells with the same name but different school (e.g. some creatures deal non-physical damage with their auto-attacks)
* Fixed an issue that caused manual pet pairing not to work

### 0.5.4
New:
* Add spec icon to the unit selection menu
* The death log now filter deaths based on the selected unit. Visualising the death recap still requires interaction with the displayed table

Bugfix:
* Opening more than one parse in the same session does not longer result in unwanted behaviour of the application
* The currently selected unit no longer resets when selecting a different meter or encounter (provided it is still a valid unit)
* The currently select unit now resets when opening another parse, even in the case of a valid unit

### 0.5.3
New:
* Display a bar visualisation of damage and healing meters
* Improve graphics across all meters and death log

Bugfix:
* The death log now behaves properly when multiple events are registered with the same timestamp
* Unassigned pets are now displayed appropriately in global damage and healing meters

### 0.5.2
New:
* Added spec tracking, for each encounter
* Added spec/spell icon on meters/breakdown
* Improved visual display of meters/breakdown

### 0.5.1
New:
* Added buff uptime tracking, and a simple uptime graph. Has some limitations mostly due to how the Combat Log works.

Tweaks:
* Death recap: now it shows all possibly relevant events since the unit was at full HP (last overhealing received / beginning of the encounter).
* Death recap: Improved readability of damage/healing information.

Bugfix:
* Fixed an issue with encounter parsing.

### 0.5
New:
* Added the possibility to manually (re)assign pets to an owner. Useful for named pets (Warlock, Hunter, Unholy DK) or for single-class temporary pets (e.g. Treants with a single Balance Druid among friendly units).

### 0.4
New:
* Added automatic coupling of pet <-> pet owner during parsing. It will not always work, for example with permanent pets that never interact with their owner (through buffs/heals) or with temporary pets for which the summon event is not registered in the combat log for any reason.
* Pets are now merged with their owner in the meter, both damage and healing. Pets with an unknown owner will still be displayed separately.

### 0.3
New:
* Added Deaths log, including death breakdown up until 5 seconds before the killing blow.
Known bug:
* Hunter's Feign Death is not tracked in the the Combat Log, resulting in false positives in the Deaths log. They can be spotted as the killing blow deals 0 overkill damage.
Bugfix:
* Fixed timestamp parsing.

### 0.2
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

### 0.1

Functionalities:
* Parse a WoWCombatLog.txt file into a usable database for quick data retrieval. This includes computing supplementary information, like identifying player- and server-controlled entities, establishing start/end time of boss encounters (in WotLK there is no event API for it), etc.
* Visualise the damage meter of a pre-parsed log. Currently limited to selecting an encounter, and displaying either the damage meter of the raid or the damage breakdown of a selected friendly unit (players and pets are currently decoupled).

