CREATE TABLE actors (
    unitGUID VARBINARY NOT NULL,
    unitName VARCHAR(50) NOT NULL,
    isPlayer BOOLEAN,
    isPet BOOLEAN,
    isNPC BOOLEAN,
    isBoss BOOLEAN,
    encounterTime TIMESTAMP NOT NULL,
    PRIMARY KEY (unitGUID, encounterTime)
)