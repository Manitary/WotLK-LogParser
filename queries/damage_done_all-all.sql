SELECT
    name
    , PRINTF('%05.2f%% | %d', dmg * 100.00 / (SUM(dmg) OVER()), dmg ) AS dmg
FROM
    (
        SELECT
            s.name AS name
            , SUM(s.dmg) AS dmg
            , COALESCE(p.ownerGUID, s.sguid) AS owner
        FROM
            (
                SELECT
                    events.sourceName AS name
                    , SUM(events.amount) + SUM(events.absorbed) AS dmg
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
                    AND events.eventName LIKE '%DAMAGE'
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
    dmg DESC