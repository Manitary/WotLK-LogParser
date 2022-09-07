WITH calc AS (
    SELECT
        targetName
        , heal * 100.0 / (SUM(heal) OVER()) AS pct
        , heal
        , spec
    FROM (
        SELECT
            targetName
            , SUM(amount) - SUM(overhealing) AS heal
            , spec
        FROM events e
        LEFT JOIN pets
        ON e.sourceGUID = pets.petGUID
        LEFT JOIN specs s
        ON e.targetGUID = s.unitGUID
        WHERE
            e.timestamp >= :startTime
        AND e.timestamp <= :endTime
        AND (
                sourceName = :sourceName
            OR  ownerName = :sourceName
        )
        AND eventName LIKE '%HEAL'
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
    , PRINTF('%,d', heal) AS heal
    , spec
FROM calc
ORDER BY relpct DESC
LIMIT 5