SELECT
    name
    , PRINTF('%05.2f%% | %d', (heal - overheal) * 100.0 / (SUM(heal) OVER() - SUM(overheal) OVER()), heal - overheal) AS heal
    , PRINTF('%d (%2.2f%%)', overheal, overheal * 100.0 / heal) AS overheal
FROM
    (
        SELECT
            s.name AS name
            , SUM(s.heal) AS heal
            , SUM(s.overheal) AS overheal
            , COALESCE(p.ownerGUID, s.sguid) AS owner
        FROM
            (
                SELECT
                    events.sourceName AS name
                    , SUM(events.amount) + SUM(events.absorbed) AS heal
                    , SUM(events.overhealing) AS overheal
                    , events.sourceGUID AS sguid
                FROM
                    events
                JOIN
                    actors
                ON
                    events.sourceGUID = actors.unitGUID
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
                    events.sourceGUID
            ) s
        LEFT JOIN
            pets p
        ON
            s.sguid = p.petGUID
        GROUP BY
            owner
    )
ORDER BY
    heal DESC