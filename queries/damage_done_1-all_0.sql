WITH calc AS (
    SELECT
        targetName
        , dmg * 100.0 / (SUM(dmg) OVER()) AS pct
        , dmg
        , spec
    FROM (
        SELECT
            targetName
            , SUM(amount) + SUM(absorbed) AS dmg
            , spec
        FROM events e
        LEFT JOIN pets
        ON e.sourceGUID = pets.petGUID
        LEFT JOIN specs s
        ON e.targetGUID = s.unitGUID
        WHERE
            spellID = :spellID
        AND e.timestamp >= :startTime
        AND e.timestamp <= :endTime
        AND (
                sourceName = :sourceName
            OR  ownerName = :sourceName
        )
        AND (
                eventName LIKE '%DAMAGE%'
            OR  missType = 'ABSORB'
        )
        AND (
                s.timestamp = :startTime
            OR  s.timestamp IS NULL
        )
        GROUP BY targetName
    )
)
SELECT
    targetName
    , PRINTF('%.2f%%', pct) AS pct
    , pct / MAX(pct) OVER() AS relpct
    , PRINTF('%,d', dmg) AS dmg
    , spec
FROM calc
ORDER BY relpct DESC
LIMIT 5