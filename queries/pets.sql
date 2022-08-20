CREATE TABLE pets (
    petGUID VARBINARY NOT NULL,
    petName VARCHAR(50) NOT NULL,
    ownerGUID VARBINARY,
    ownerName VARCHAR(50),
    PRIMARY KEY (petGUID, petName)
)
