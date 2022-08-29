CREATE TABLE specs (
    unitGUID VARBINARY NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    spec VARCHAR(10),
    PRIMARY KEY (unitGUID, timestamp)
)