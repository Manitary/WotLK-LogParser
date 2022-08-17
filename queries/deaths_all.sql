SELECT
    PRINTF('%d:%02d',
        (JULIANDAY(dtime) - JULIANDAY(:startTime)) * 86400 / 60,
        ((JULIANDAY(dtime) - JULIANDAY(:startTime)) * 86400 % 60)) AS time
    , name
    , murderer
    , spell
    , PRINTF('%d (%d)', dmg, overkill) AS dmg
    , etime AS timestamp
FROM
    (
        SELECT
            ed.time AS dtime
            , LAST_VALUE(e.time) OVER (
                PARTITION BY ed.time, ed.name
                ORDER BY e.time
                RANGE BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING
            ) AS etime
            , LAST_VALUE(ed.name) OVER (
                PARTITION BY ed.time, ed.name
                ORDER BY e.time
                RANGE BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING
            ) AS name
            , LAST_VALUE(e.murderer) OVER (
                PARTITION BY ed.time, ed.name
                ORDER BY e.time
                RANGE BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING
            ) AS murderer
            , LAST_VALUE(e.spell) OVER (
                PARTITION BY ed.time, ed.name
                ORDER BY e.time
                RANGE BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING
            ) AS spell
            , LAST_VALUE(e.dmg) OVER (
                PARTITION BY ed.time, ed.name
                ORDER BY e.time
                RANGE BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING
            ) AS dmg
            , LAST_VALUE(e.overkill) OVER (
                PARTITION BY ed.time, ed.name
                ORDER BY e.time
                RANGE BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING
            ) AS overkill
        FROM
            (
                SELECT
                    events.timestamp AS time
                    , events.eventName AS event
                    , events.spellName AS spell
                    , events.targetGUID AS guid
                    , events.amount AS dmg
                    , events.overkill AS overkill
                    , events.sourceName AS murderer
                FROM
                    events
                JOIN
                    (   
                        SELECT
                            unitGUID
                        FROM
                            actors
                        WHERE
                        (
                            actors.isPlayer = :affiliation
                            OR
                                (
                                    :affiliation = 0
                                AND actors.isNPC = 1
                                )
                        )
                    ) a
                ON
                    events.targetGUID = a.unitGUID
                WHERE
                    event LIKE '%DAMAGE'
                    AND events.timestamp >= :startTime
                    AND events.timestamp <= :endTime
            ) e
        JOIN
            (
                SELECT
                    events.timestamp AS time
                    , events.targetName AS name
                    , events.targetGUID AS guid
                FROM
                    events
                JOIN
                    (   
                        SELECT
                            unitGUID
                        FROM
                            actors
                        WHERE
                            (
                                actors.isPlayer = :affiliation
                                OR
                                    (
                                        :affiliation = 0
                                    AND actors.isNPC = 1
                                    )
                            )
                    ) a
                ON
                    events.targetGUID = a.unitGUID
                WHERE
                    events.eventName = 'UNIT_DIED'
                    AND events.timestamp >= :startTime
                    AND events.timestamp <= :endTime
            ) ed
        ON
            e.guid = ed.guid
        AND e.time <= ed.time
    )
GROUP BY
    time
ORDER BY
    time