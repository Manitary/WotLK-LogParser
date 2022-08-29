WITH calc AS (
    SELECT
        name
        , total
        , total * 100.0 / (SUM(total) OVER()) AS totalpct
        , total / (JULIANDAY(:endTime) - JULIANDAY(:startTime)) / 86400 AS dtps
        , mitigated
        , spec
    FROM (
        SELECT
            name
            , effective + mitigated AS total
            , effective
            , mitigated
            , guid
        FROM (
            SELECT
                events.targetName AS name
                , SUM(events.amount) AS effective
                , SUM(events.blocked) + SUM(events.absorbed) + SUM(events.resisted) AS mitigated
                , events.targetGUID AS guid
            FROM events
            JOIN actors
            ON events.targetGUID = actors.unitGUID
            WHERE
                events.timestamp >= :startTime
                AND events.timestamp <= :endTime
                AND (
                        actors.isPlayer = :affiliation
                    OR  actors.isPet = :affiliation
                    OR (
                            :affiliation = 0
                        AND actors.isNPC = 1
                    )
                )
            AND sourceName = :sourceName
            AND (
                    events.eventName LIKE '%DAMAGE'
                OR  events.eventName LIKE '%MISSED'
            )
            GROUP BY events.targetName
        )
    ) m
    LEFT JOIN specs
    ON m.guid = specs.unitGUID
    GROUP BY guid
)
SELECT
    name
    , PRINTF('%.2f', totalpct) AS pct
    , PRINTF('%,d', total) AS total
    , PRINTF('%,d', dtps) AS dtps
    , PRINTF('%,d (%.2f%%)', mitigated, mitigated * 100.0 / total) AS mitigated
    , spec
    , totalpct
FROM calc
UNION ALL
SELECT
    'Total' AS name
    , '-' AS pct
    , PRINTF('%,d', SUM(total)) AS total
    , PRINTF('%,d', SUM(dtps)) AS dtps
    , PRINTF('%,d (%.2f%%)', SUM(mitigated), SUM(mitigated) * 100.0 / SUM(total)) AS mitigated
    , NULL AS spec
    , NULL AS totalpct
FROM calc
ORDER BY totalpct DESC