WITH calc AS (
    SELECT
        missType
        , miss * 100.0 / (SUM(miss) OVER()) AS pct
        , miss
        , spellSchool
    FROM (
        SELECT
            missType
            , COUNT(missType) AS miss
            , spellSchool
        FROM events
        WHERE
            spellID = :spellID
        AND timestamp >= :startTime
        AND timestamp <= :endTime
        AND sourceName = :sourceName
        AND targetName = :targetName
        AND eventName LIKE '%MISSED'
        GROUP BY missType
    )
)
SELECT
    missType
    , PRINTF('%.2f%%', pct) AS pct
    , pct / MAX(pct) OVER() AS relpct
    , PRINTF('%,d', miss) AS miss
    , spellSchool
FROM calc
ORDER BY relpct DESC