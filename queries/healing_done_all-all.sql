WITH calc AS (
    SELECT
        name
        , heal - overheal AS heal
        , overheal
        , overheal * 100.0 / heal AS overhealpct
        , (heal - overheal) * 100.0 / (SUM(heal) OVER() - SUM(overheal) OVER()) AS healpct
        , heal / (JULIANDAY(:endTime) - JULIANDAY(:startTime)) / 86400 AS hps
        , (heal - overheal) / (JULIANDAY(:endTime) - JULIANDAY(:startTime)) / 86400 AS ehps
        , spec
    FROM (
        SELECT
            s.name AS name
            , SUM(s.heal) AS heal
            , SUM(s.overheal) AS overheal
            , COALESCE(p.ownerGUID, s.sguid) AS owner
        FROM (
            SELECT
                events.sourceName AS name
                , SUM(events.amount) + SUM(events.absorbed) AS heal
                , SUM(events.overhealing) AS overheal
                , events.sourceGUID AS sguid
            FROM events
            JOIN actors
            ON events.sourceGUID = actors.unitGUID
            WHERE
                events.timestamp >= :startTime
            AND events.timestamp <= :endTime
            AND (
                    actors.isPlayer = :affiliation
                OR  actors.isPet = :affiliation
                OR (
                        :affiliation = 0
                    AND actors.isNPC = 1
                )
            )
            AND events.eventName LIKE '%HEAL'
            GROUP BY
                events.sourceGUID
        ) s
        LEFT JOIN pets p
        ON s.sguid = p.petGUID
        GROUP BY
            owner
    ) m
    LEFT JOIN specs
    ON m.owner = specs.unitGUID
    GROUP BY
        owner
)
SELECT
    name
    , PRINTF('%.2f', healpct) AS pct
    , PRINTF('%,d', heal) AS heal
    , PRINTF('%,d', ehps) AS ehps
    , PRINTF('%,d (%2.2f%%)', overheal, overhealpct) AS overheal
    , PRINTF('%,d', hps) AS hps
    , spec
    , healpct
FROM calc
UNION ALL
SELECT
    'Total' AS name
    , '-' AS pct
    , PRINTF('%,d', SUM(heal)) AS heal
    , PRINTF('%,d', SUM(ehps)) AS ehps
    , PRINTF('%,d (%2.2f%%)', SUM(overheal), SUM(overheal) * 100.0 / SUM(heal)) AS overheal
    , PRINTF('%,d', SUM(hps)) AS hps
    , NULL AS spec
    , NULL AS healpct
FROM calc
ORDER BY
    healpct DESC
