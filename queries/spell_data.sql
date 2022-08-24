CREATE TABLE spell_data (
    expansion_id TINYINT,
    spellID MEDIUMINT UNSIGNED PRIMARY KEY UNIQUE NOT NULL,
    localization_id MEDIUMINT UNSIGNED,
    subtext_localization_id MEDIUMINT UNSIGNED,
    cost MEDIUMINT UNSIGNED,
    cost_in_percent TINYINT UNSIGNED,
    power_type TINYINT,
    cast_time MEDIUMINT UNSIGNED,
    school_mask TINYINT UNSIGNED,
    dispel_type TINYINT UNSIGNED,
    range_max MEDIUMINT UNSIGNED,
    cooldown INT UNSIGNED,
    duration INT UNSIGNED,
    icon VARCHAR(50),
    description_localization_id MEDIUMINT UNSIGNED,
    aura_localization_id MEDIUMINT UNSIGNED
)