SELECT
    PRINTF('%.2f', (JULIANDAY(e.timestamp) - JULIANDAY(:endTime)) * 86400) AS time
    , COALESCE(missType, '')
    || IIF(eventName = 'UNIT_DIED', '(Previous death)', '')
    || IIF(eventName LIKE '%DOSE', 'x', '')
    || IIF(critical > 0, '*' || amount || '*', COALESCE(amount, ''))
    || IIF(absorbed > 0, ' (A:' || absorbed || ')', '')
    || IIF(overhealing > 0, ' (O:' || overhealing || ')', '')
    || IIF(overkill > 0, ' (O:' || overkill ||')', '')
    || IIF(eventName LIKE '%PERIODIC%', ' (Tick)', '')
    || IIF(eventName LIKE '%APPLIED', 'Applied', '')
    || IIF(eventName LIKE '%REMOVED', 'Expired', '')
    || IIF(eventName LIKE '%REFRESH', 'Refreshed', '')
    AS 'dmg/heal'
    , COALESCE(spellName, environmentalType) AS spell
    , sourceName AS source
    , eventName
    , spec
    , icon
    , spellSchool
FROM events e
LEFT JOIN specs
ON e.sourceGUID = specs.unitGUID
LEFT JOIN spell_db.spell_data s
ON e.spellID = s.spellID
WHERE
    targetName = :targetName
AND id >= (
    SELECT
        MAX(t.id)
    FROM (
        SELECT id
        FROM events
        WHERE
            targetName = :targetName
        AND timestamp < :endTime
        AND (
                overhealing > 0
            OR  eventName = 'UNIT_DIED'
        )
        UNION ALL
        SELECT id
        FROM events
        WHERE timestamp = :startTime
    ) t
)
AND (
        e.timestamp < :endTime
    OR (
            e.timestamp = :endTime
        AND (
                eventName LIKE '%DAMAGE%'
            OR  eventName LIKE '%HEAL'
            OR  eventName LIKE '%MISSED'
        )
    )
)
AND eventName NOT LIKE '%ENERGIZE'
AND (
        specs.timestamp = :startTime
    OR  specs.timestamp IS NULL
)
ORDER BY id DESC