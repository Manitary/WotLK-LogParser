WITH calc AS (
    SELECT
        missType
        , miss * 100.0 / (SUM(miss) OVER()) AS pct
        , miss
        , school
    FROM (
        SELECT
            missType
            , COUNT(missType) AS miss
            , MAX(spellSchool & 1) + MAX(spellSchool & 2) + MAX(spellSchool & 4) + MAX(spellSchool & 8) + MAX(spellSchool & 16) + MAX(spellSchool & 32) + MAX(spellSchool & 64) AS school
        FROM events
        LEFT JOIN pets
        ON events.sourceGUID = pets.petGUID
        LEFT JOIN actors
        ON events.sourceGUID = actors.unitGUID
        WHERE
            spellID = :spellID
        AND timestamp >= :startTime
        AND timestamp <= :endTime
        AND targetName = :targetName
        AND sourceName = :sourceName
        AND (
                isPet IS NULL
            OR  ownerName = :ownerName
        )
        AND eventName LIKE '%MISSED'
        GROUP BY missType
    )
)
SELECT
    missType
    , PRINTF('%.2f%%', pct) AS pct
    , pct / MAX(pct) OVER() AS relpct
    , PRINTF('%,d', miss) AS miss
    , school
FROM calc
ORDER BY relpct DESC