CREATE TABLE auras (
    id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
    spellName VARCHAR(50),
    spellID MEDIUMINT UNSIGNED,
    spellSchool TINYINT UNSIGNED,
    sourceName VARCHAR(50),
    sourceGUID VARBINARY,
    targetName VARCHAR(50),
    targetGUID VARBINARY,
    auraType VARCHAR(6),
    timeStart TIMESTAMP,
    timeEnd TIMESTAMP,
    eventType SMALLINT UNSIGNED
)