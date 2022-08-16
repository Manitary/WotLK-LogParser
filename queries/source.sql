SELECT actors.unitName, actors.isPet
FROM 
    actors
INNER JOIN
    (
        SELECT sourceName
        FROM events
        WHERE events.timestamp >= :startTime
        AND events.timestamp <= :endTime
        GROUP BY sourceName
    ) e
ON actors.unitName = e.sourceName
WHERE actors.isPlayer = 1 OR actors.isPet = 1
GROUP BY actors.unitName
ORDER BY actors.isPlayer DESC, actors.unitName