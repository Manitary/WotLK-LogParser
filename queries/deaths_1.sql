SELECT
    PRINTF('%.2f', (JULIANDAY(timestamp) - JULIANDAY(:endTime)) * 86400) AS time
    , sourceName AS source
    , spellName AS spell
    , targetName AS target
    , amount AS 'dmg/heal'
    , absorbed
    , overkill
FROM
    events
WHERE
    targetName = :targetName
AND timestamp >= :startTime
AND (
        timestamp < :endTime
    OR
        (
            timestamp = :endTime
        AND
            (
                eventName LIKE '%DAMAGE%'
            OR  eventName LIKE '%HEAL'
            )
        )
)
AND (JULIANDAY(:endTime) - JULIANDAY(timestamp)) * 86400 <= 5
ORDER BY
    timestamp DESC