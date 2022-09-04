CREATE TABLE specs (
    unitGUID VARBINARY NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    unitName VARCHAR(50),
    spec VARCHAR(10),
    PRIMARY KEY (unitGUID, timestamp)
)