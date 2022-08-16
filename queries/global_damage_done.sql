SELECT events.sourceName AS name
    , SUM(events.amount) AS dmg
FROM events
JOIN actors
ON (events.sourceGUID = actors.unitGUID)
WHERE
    events.timestamp >= :startTime
    AND events.timestamp <= :endTime
    AND (actors.isPlayer = 1 OR actors.isPet = 1)
    AND events.eventName LIKE '%DAMAGE'
GROUP BY events.sourceName
ORDER BY dmg DESC