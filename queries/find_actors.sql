SELECT
    actors.unitName
    , actors.isPlayer
    , actors.isPet
    , actors.isNPC
FROM
    (
        SELECT
            sourceName
        FROM
            events
        WHERE
                events.timestamp >= :startTime
            AND events.timestamp <= :endTime
        GROUP BY
            sourceName
    UNION
        SELECT
            targetName
        FROM
            events
        WHERE
                events.timestamp >= :startTime
            AND events.timestamp <= :endTime
        GROUP BY
            targetName
    ) n
INNER JOIN
    actors
ON
    actors.unitName = n.sourceName
GROUP BY
    actors.unitName
ORDER BY
    actors.isPlayer DESC
    , actors.unitName
