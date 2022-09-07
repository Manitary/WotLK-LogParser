WITH calc AS (
    SELECT
        sp AS spellName
        , (heal - overheal) * 100.0 / (SUM(heal) OVER() - SUM(overheal) OVER()) AS pct
        , heal - overheal AS heal
        , icon
        , school
    FROM (
        SELECT
            IIF(sourceName = :sourceName, '', '(' || sourceName || ') ') || spellName || IIF(eventName LIKE 'SPELL_PERIODIC%', ' (HoT)', '') AS sp
            , SUM(amount) + SUM(absorbed) AS heal
            , SUM(overhealing) AS overheal
            , icon
            , spellSchool AS school
        FROM events
        LEFT JOIN pets
        ON events.sourceGUID = pets.petGUID
        LEFT JOIN spell_db.spell_data s
        ON events.spellID = s.spellID
        WHERE
            timestamp >= :startTime
        AND timestamp <= :endTime
        AND targetName = :targetName
        AND (
                sourceName = :sourceName
            OR  ownerName = :sourceName
        )
        AND eventName LIKE '%HEAL'
        GROUP BY sp, s.spellID
    )
)
SELECT
    spellName
    , PRINTF('%.2f%%', pct) AS pct
    , pct / MAX(pct) OVER() AS relpct
    , PRINTF('%,d', heal) AS heal
    , icon
    , school
FROM calc
ORDER BY relpct DESC
LIMIT 5