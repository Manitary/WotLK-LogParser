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
            COALESCE(ownerName, name) AS name
            , SUM(heal) AS heal
            , SUM(overheal) AS overheal
            , COALESCE(ownerGUID, sourceGUID) AS owner
        FROM (
            SELECT
                sourceName AS name
                , SUM(amount) + SUM(absorbed) AS heal
                , SUM(overhealing) AS overheal
                , sourceGUID
            FROM events
            JOIN actors
            ON events.sourceGUID = actors.unitGUID
            WHERE
                timestamp >= :startTime
            AND timestamp <= :endTime
            AND (
                    isPlayer = :affiliation
                OR  isPet = :affiliation
                OR (
                        :affiliation = 0
                    AND isNPC = 1
                )
            )
            AND encounterTime = :startTime
            AND eventName LIKE '%HEAL'
            GROUP BY sourceGUID
        ) s
        LEFT JOIN pets p
        ON s.sourceGUID = p.petGUID
        GROUP BY owner
    ) m
    LEFT JOIN specs
    ON m.owner = specs.unitGUID
    WHERE
        timestamp = :startTime
    OR  timestamp IS NULL
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
    , name AS cleanname
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
    , NULL AS cleanname
FROM calc
ORDER BY relpct DESC