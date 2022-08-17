SELECT
    name
    , heal - overheal AS heal
    , PRINTF('%d (%2.2f%%)', overheal, overheal*100.00/heal) AS overheal
FROM
    (
        SELECT
            events.sourceName AS name
            , SUM(events.amount) + SUM(events.absorbed) AS heal
            , SUM(events.overhealing) AS overheal
        FROM
            events
        JOIN
            actors
        ON
            (events.sourceGUID = actors.unitGUID)
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
            AND events.eventName LIKE '%HEAL'
        GROUP BY
            events.sourceName
    )
ORDER BY
    heal DESC