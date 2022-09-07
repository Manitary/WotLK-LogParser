WITH calc AS (
    SELECT
        name
        , total
        , total * 100.0 / (SUM(total) OVER()) AS totalpct
        , total / (JULIANDAY(:endTime) - JULIANDAY(:startTime)) / 86400 AS dtps
        , mitigated
        , spec
        , COUNT(name) AS num
    FROM (
        SELECT
            name
            , effective + absorbed AS total
            , effective
            , mitigated
            , guid
        FROM (
            SELECT
                targetName AS name
                , SUM(amount) AS effective
                , SUM(absorbed) AS absorbed
                , SUM(blocked) + SUM(events.resisted) AS mitigated
                , targetGUID AS guid
            FROM events
            JOIN actors
            ON events.targetGUID = actors.unitGUID
            LEFT JOIN pets
            ON events.sourceGUID = pets.petGUID
            WHERE
                timestamp >= :startTime
            AND timestamp <= :endTime
            AND (
                    isPlayer = :affiliation
                OR  isPet = :affiliation
                OR (
                        :affiliation = 0
                    AND isNPC = 1
                )
            )
            AND (
                    sourceName = :sourceName
                OR  ownerName = :sourceName
            )
            AND (
                    eventName LIKE '%DAMAGE'
                OR  eventName LIKE '%MISSED'
            )
            GROUP BY targetGUID
        )
    ) m
    LEFT JOIN specs
    ON m.guid = specs.unitGUID
    WHERE
        total > 0
    AND (
            specs.timestamp = :startTime
        OR  specs.timestamp IS NULL
    )
    GROUP BY name
)
SELECT
    name || IIF(num > 1, ' (' || num || ')', '') AS name
    , PRINTF('%.2f%%', totalpct) AS pct
    , totalpct / MAX(totalpct) OVER() AS relpct
    , PRINTF('%,d', total) AS total
    , PRINTF('%,d', dtps) AS dtps
    , PRINTF('%,d (%.2f%%)', mitigated, mitigated * 100.0 / total) AS mitigated
    , spec
    , name AS cleanname
FROM calc
UNION ALL
SELECT
    'Total' AS name
    , '-' AS pct
    , NULL AS relpct
    , PRINTF('%,d', SUM(total)) AS total
    , PRINTF('%,d', SUM(dtps)) AS dtps
    , PRINTF('%,d (%.2f%%)', SUM(mitigated), SUM(mitigated) * 100.0 / SUM(total)) AS mitigated
    , NULL AS spec
    , NULL AS cleanname
FROM calc
ORDER BY relpct DESC