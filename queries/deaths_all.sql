SELECT
    PRINTF('%d:%02d',
        (JULIANDAY(time) - JULIANDAY(:startTime)) * 86400 / 60,
        ((JULIANDAY(time) - JULIANDAY(:startTime)) * 86400 % 60)) AS time
    , name
    , murderer
    , COALESCE(spell, environment) AS spell
    , IIF(overkill > 0, PRINTF('%,d (O: %,d)', dmg, overkill), PRINTF('%,d', dmg)) AS dmg
    , time
    , spec
    , icon
    , school
    , id
FROM (
    SELECT
        LAST_VALUE(e.timestamp) OVER (
            PARTITION BY ed.timestamp, ed.targetName
            ORDER BY e.id
            RANGE BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING
        ) AS time
        , LAST_VALUE(e.targetName) OVER (
            PARTITION BY ed.timestamp, ed.targetName
            ORDER BY e.id
            RANGE BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING
        ) AS name
        , LAST_VALUE(e.sourceName) OVER (
            PARTITION BY ed.timestamp, ed.targetName
            ORDER BY e.id
            RANGE BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING
        ) AS murderer
        , LAST_VALUE(e.spellName) OVER (
            PARTITION BY ed.timestamp, ed.targetName
            ORDER BY e.id
            RANGE BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING
        ) AS spell
        , LAST_VALUE(e.amount) OVER (
            PARTITION BY ed.timestamp, ed.targetName
            ORDER BY e.id
            RANGE BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING
        ) AS dmg
        , LAST_VALUE(e.overkill) OVER (
            PARTITION BY ed.timestamp, ed.targetName
            ORDER BY e.id
            RANGE BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING
        ) AS overkill
        , LAST_VALUE(e.environmentalType) OVER (
            PARTITION BY ed.timestamp, ed.targetName
            ORDER BY e.id
            RANGE BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING
        ) AS environment
        , LAST_VALUE(spec) OVER (
            PARTITION BY ed.timestamp, ed.targetName
            ORDER BY e.id
            RANGE BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING
        ) AS spec
        , LAST_VALUE(icon) OVER (
            PARTITION BY ed.timestamp, ed.targetName
            ORDER BY e.id
            RANGE BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING
        ) AS icon
        , LAST_VALUE(e.spellSchool) OVER (
            PARTITION BY ed.timestamp, ed.targetName
            ORDER BY e.id
            RANGE BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING
        ) AS school
        , LAST_VALUE(e.id) OVER (
            PARTITION BY ed.timestamp, ed.targetName
            ORDER BY e.id
            RANGE BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING
        ) AS id
    FROM events e
    JOIN (
        SELECT
            id
            , timestamp
            , targetName
            , targetGUID
        FROM events
        JOIN actors
        ON events.targetGUID = actors.unitGUID
        WHERE
            eventName = 'UNIT_DIED'
        AND timestamp >= :startTime
        AND timestamp <= :endTime
        AND (
                isPlayer = :affiliation
            OR (
                    :affiliation = 0
                AND isNPC = 1
            )
        )
    ) ed
    ON
        e.targetGUID = ed.targetGUID
    AND e.timestamp <= ed.timestamp
    LEFT JOIN specs
    ON
        e.targetGUID = specs.unitGUID
    LEFT JOIN spell_db.spell_data s
    ON e.spellID = s.spellID
    WHERE
        e.timestamp >= :startTime
    AND e.eventName LIKE '%DAMAGE%'
    AND (
            specs.timestamp = :startTime
        OR  specs.timestamp IS NULL
    )
)
GROUP BY time, name
ORDER BY time, id
