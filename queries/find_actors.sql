SELECT
    actors.unitName
    , actors.isPlayer
    , actors.isPet
    , actors.isNPC
    , actors.unitGUID
    , spec
FROM (
    SELECT sourceName
    FROM events
    WHERE
            events.timestamp >= :startTime
        AND events.timestamp <= :endTime
    GROUP BY sourceName
    UNION
    SELECT targetName
    FROM events
    WHERE
            events.timestamp >= :startTime
        AND events.timestamp <= :endTime
    GROUP BY targetName
) n
INNER JOIN actors
ON actors.unitName = n.sourceName
LEFT JOIN specs
ON actors.unitGUID = specs.unitGUID
WHERE
    specs.timestamp = :startTime
OR  specs.timestamp IS NULL
GROUP BY actors.unitName
ORDER BY
    actors.isPlayer DESC
    , actors.unitName
