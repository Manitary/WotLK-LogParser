SELECT
    name
    , effective + mitigated AS total
    , effective
    , mitigated AS nullified
FROM
    (
        SELECT events.targetName AS name
            , SUM(events.amount) AS effective
            , SUM(events.resisted) + SUM(events.blocked) + SUM(events.absorbed) AS mitigated
        FROM events
        JOIN actors
        ON (events.targetGUID = actors.unitGUID)
        WHERE
            events.timestamp >= :startTime
            AND events.timestamp <= :endTime
            AND (actors.isPlayer = 1 OR actors.isPet = 1)
            AND events.eventName LIKE '%DAMAGE'
        GROUP BY events.targetName
    )
ORDER BY total DESC