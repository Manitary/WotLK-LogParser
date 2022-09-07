WITH calc AS (
    SELECT
        COALESCE(ownerName, sourceName) AS name
        , SUM(dmg) * 100.0 / (SUM(dmg) OVER()) AS pct
        , SUM(dmg) AS dmg
        , MAX(spec) AS spec
    FROM (
        SELECT
            sourceName
            , ownerName
            , SUM(amount) + SUM(absorbed) AS dmg
            , spec
        FROM events e
        LEFT JOIN pets
        ON e.sourceGUID = pets.petGUID
        LEFT JOIN specs s
        ON e.sourceGUID = s.unitGUID
        WHERE
            e.timestamp >= :startTime
        AND e.timestamp <= :endTime
        AND targetName = :targetName
        AND (
                eventName LIKE '%DAMAGE%'
            OR  missType = 'ABSORB'
        )
        AND (
                s.timestamp = :startTime
            OR  s.timestamp IS NULL
        )
        GROUP BY sourceName
    )
    GROUP BY name
)
SELECT
    name
    , PRINTF('%.2f%%', pct) AS pct
    , pct / MAX(pct) OVER() AS relpct
    , PRINTF('%,d', dmg) AS dmg
    , spec
FROM calc
ORDER BY relpct DESC
LIMIT 5