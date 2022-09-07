WITH calc AS (
    SELECT
       sp AS spellName
        , effective * 100.0 / (SUM(effective) OVER()) AS pct
        , effective
        , icon
        , school
    FROM (
        SELECT
            IIF(ownerName IS NOT NULL, '(' || sourceName || ') ', '') || spellName || IIF(eventName LIKE 'SPELL_PERIODIC%', ' (DoT)', '') AS sp
            , SUM(amount) + SUM(absorbed) AS effective
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
        AND (
                eventName LIKE '%DAMAGE%'
            OR  missType = 'ABSORB'
        )
        GROUP BY sp, s.spellID
        ORDER BY effective DESC
    )
)
SELECT
    spellName
    , PRINTF('%.2f%%', pct) AS pct
    , pct / MAX(pct) OVER() AS relpct
    , PRINTF('%,d', effective) AS effective
    , icon
    , school
FROM calc
ORDER BY relpct DESC
LIMIT 5