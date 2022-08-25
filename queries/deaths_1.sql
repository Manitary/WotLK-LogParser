SELECT
    PRINTF('%.2f', (JULIANDAY(timestamp) - JULIANDAY(:endTime)) * 86400) AS time
    , eventName
    , sourceName AS source
    , spellName AS spell
    , IIF(critical > 0, '*' || amount || '*', amount) || IIF(absorbed > 0, ' (A:' || absorbed || ')', '') || IIF(overhealing > 0, ' (O:' || overhealing || ')', '') || IIF(overkill > 0, ' (O:' || overkill ||')', '') AS 'dmg/heal'
FROM
    events
WHERE
    targetName = :targetName
AND timestamp >= (
    SELECT
        MAX(t.timestamp)
    FROM
        (
            SELECT timestamp
            FROM events
            WHERE
                targetName = :targetName
            AND overhealing > 0
            AND timestamp < :endTime
            UNION ALL
            SELECT :startTime AS timestamp
        ) t
    )
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
AND eventName NOT LIKE '%ENERGIZE'
ORDER BY
    timestamp DESC