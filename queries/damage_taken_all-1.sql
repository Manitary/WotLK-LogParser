SELECT
    name
    , effective + mitigated AS total
    , effective
    , mitigated AS nullified
    , resisted
FROM
    (
        SELECT
            events.targetName AS name
            , SUM(events.amount) AS effective
            , SUM(events.resisted) AS resisted
            , SUM(events.blocked) + SUM(events.absorbed) AS mitigated
        FROM
            events
        JOIN
            actors
        ON
            (events.targetGUID = actors.unitGUID)
        WHERE
                events.timestamp >= :startTime
            AND events.timestamp <= :endTime
            AND
                (
                    actors.isPlayer = :affiliation
                OR  actors.isPet = :affiliation
                OR
                    (
                        :affiliation = 0
                    AND actors.isNPC = 1
                    )
                )
            AND events.eventName LIKE '%DAMAGE'
            AND sourceName = :sourceName
        GROUP BY
            events.targetName
    )
ORDER BY
    total DESC