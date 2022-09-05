WITH calc AS (
    SELECT
        sp AS spellName
        , (dmg + absorbed) * 100.0 / (SUM(dmg) OVER() + SUM(absorbed) OVER()) AS pct
        , dmg + absorbed AS dmg
        , icon
        , school
    FROM (
        SELECT
            IIF(sourceName = :sourceName, '', '(' || sourceName || ') ') || spellName || IIF(eventName LIKE 'SPELL_PERIODIC%', ' (DoT)', '') AS sp
            , SUM(amount) AS dmg
            , SUM(absorbed) AS absorbed
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
        AND (
                sourceName = :sourceName
            OR  ownerName = :sourceName
        )
        AND events.targetName = :targetName
        AND eventName LIKE '%DAMAGE%'
        AND spellName IS NOT NULL
        GROUP BY sp
        ORDER BY dmg + absorbed DESC
    )
)
SELECT
    spellName
    , PRINTF('%.2f%%', pct) AS pct
    , pct / MAX(pct) OVER() AS relpct
    , PRINTF('%,d', dmg) AS dmg
    , icon
    , school
FROM calc
ORDER BY relpct DESC
LIMIT 5