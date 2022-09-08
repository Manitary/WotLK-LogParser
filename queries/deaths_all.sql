SELECT
    PRINTF('%d:%02d',
        (JULIANDAY(time) - JULIANDAY(:startTime)) * 86400 / 60,
        ((JULIANDAY(time) - JULIANDAY(:startTime)) * 86400 % 60)) AS time
    , targetName
    , sourceName
    , COALESCE(spellName, environmentalType) AS spell
    , IIF(overkill > 0, PRINTF('%,d (O: %,d)', amount, overkill), PRINTF('%,d', amount)) AS dmg
    , time AS timeaccurate
    , spec
    , icon
    , spellSchool
    , id
FROM (
    SELECT
        e.timestamp AS time, targetName, sourceName, spellName, amount, overkill, environmentalType, spec, icon, spellSchool, id
    FROM events e
    LEFT JOIN specs
    ON e.targetGUID = specs.unitGUID
    LEFT JOIN spell_db.spell_data s
    ON e.spellID = s.spellID
    WHERE
        id IN (
            SELECT DISTINCT
                LAST_VALUE(e.id) OVER (
                    PARTITION BY ed.timestamp, ed.targetName
                    ORDER BY e.id
                    RANGE BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING
                )
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
            WHERE
                e.timestamp >= :startTime
            AND e.eventName LIKE '%DAMAGE%'
        )
    AND (
            specs.timestamp = :startTime
        OR  specs.timestamp IS NULL
    )
)
GROUP BY timeaccurate, targetName
ORDER BY id