CREATE TABLE encounters (
    id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
    unitGUID VARBINARY,
    enemy VARCHAR(50),
    timeStart TIMESTAMP,
    timeEnd TIMESTAMP,
    isKill BOOLEAN
)