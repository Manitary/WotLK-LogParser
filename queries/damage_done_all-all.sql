SELECT
    events.sourceName AS name
    , SUM(events.amount) + SUM(events.absorbed) AS dmg
FROM
    events
JOIN
    actors
ON
    (events.sourceGUID = actors.unitGUID)
WHERE
    events.timestamp >= :startTime
    AND events.timestamp <= :endTime
    AND
        (
            actors.isPlayer = :affiliation
        OR  actors.isPet = :affiliation
        OR
            (
                :affiliation = 0
            AND actors.isNPC = 1
            )
        )
    AND
        (
            events.eventName LIKE '%DAMAGE'
        OR  events.eventName LIKE '%MISSED'
        )
GROUP BY
    events.sourceName
ORDER BY
    dmg DESC