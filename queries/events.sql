CREATE TABLE events (
    id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    eventName VARCHAR(30) NOT NULL,
    sourceGUID VARBINARY,
    sourceName VARCHAR(50),
    sourceFlags VARBINARY,
    targetGUID VARBINARY,
    targetName VARCHAR(50),
    targetFlags VARBINARY,
    spellID MEDIUMINT UNSIGNED,
    environmentalType VARCHAR(8),
    spellName VARCHAR(30),
    spellSchool TINYINT UNSIGNED,
    amount MEDIUMINT UNSIGNED,
    overkill MEDIUMINT UNSIGNED,
    school TINYINT UNSIGNED,
    resisted MEDIUMINT UNSIGNED,
    blocked MEDIUMINT UNSIGNED,
    absorbed MEDIUMINT UNSIGNED,
    critical BOOLEAN,
    glancing BOOLEAN,
    crushing BOOLEAN,
    missType VARCHAR(7),
    overhealing MEDIUMINT UNSIGNED,
    overEnergize MEDIUMINT UNSIGNED,
    powerType TINYINT,
    extraAmount MEDIUMINT UNSIGNED,
    extraSpellID MEDIUMINT UNSIGNED,
    extraSpellName VARCHAR(30),
    extraSchool TINYINT UNSIGNED,
    auraType VARCHAR(6),
    itemID SMALLINT UNSIGNED,
    itemName VARCHAR(50),
    absorbedByUnitGUID VARBINARY,
    absorbedByUnitName VARCHAR(50),
    absorbedBySpellID MEDIUMINT UNSIGNED,
    absorbedBySpellName VARCHAR(30),
    absorbedBySpellSchool TINYINT UNSIGNED
)