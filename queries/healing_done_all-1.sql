WITH calc AS (
    SELECT
        name
        , SUM(heal) - SUM(overheal) AS heal
        , SUM(overheal) AS overheal
        , SUM(overheal) * 100.0 / SUM(heal) AS overhealpct
        , (SUM(heal) - SUM(overheal)) * 100.0 / (SUM(heal) OVER() - SUM(overheal) OVER()) AS healpct
        , SUM(heal) / (JULIANDAY(:endTime) - JULIANDAY(:startTime)) / 86400 AS hps
        , (SUM(heal) - SUM(overheal)) / (JULIANDAY(:endTime) - JULIANDAY(:startTime)) / 86400 AS ehps
        , spec
        , COUNT(name) AS num
    FROM (
        SELECT
            COALESCE(p.ownerName, s.name) AS name
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
            AND targetName = :targetName
            AND events.eventName LIKE '%HEAL'
            GROUP BY events.sourceGUID
        ) s
        LEFT JOIN pets p
        ON s.sguid = p.petGUID
        GROUP BY owner
    ) m
    LEFT JOIN specs
    ON m.owner = specs.unitGUID
    WHERE
        specs.timestamp = :startTime
    OR  specs.timestamp IS NULL
    GROUP BY name
)
SELECT
    name || IIF(num > 1, ' (' || num || ')', '') AS name
    , PRINTF('%.2f%%', healpct) AS pct
    , healpct / MAX(healpct) OVER() AS relpct
    , PRINTF('%,d', heal) AS heal
    , PRINTF('%,d', ehps) AS ehps
    , PRINTF('%,d (%2.2f%%)', overheal, overhealpct) AS overheal
    , PRINTF('%,d', hps) AS hps
    , spec
FROM calc
UNION ALL
SELECT
    'Total' AS name
    , '-' AS pct
    , NULL AS relpct
    , PRINTF('%,d', SUM(heal)) AS heal
    , PRINTF('%,d', SUM(ehps)) AS ehps
    , PRINTF('%,d (%2.2f%%)', SUM(overheal), SUM(overheal) * 100.0 / (SUM(heal) + SUM(overheal))) AS overheal
    , PRINTF('%,d', SUM(hps)) AS hps
    , NULL AS spec
FROM calc
ORDER BY relpct DESC
