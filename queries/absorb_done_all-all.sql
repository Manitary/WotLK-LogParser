WITH calc AS (
    SELECT
        name
        , absorb
        , absorb * 100.0 / (SUM(absorb) OVER()) AS pct
        , absorb / (JULIANDAY(:endTime) - JULIANDAY(:startTime)) / 86400 AS hps
        , spec
        , COUNT(name) AS num
    FROM (
        SELECT
            COALESCE(ownerName, unitName) AS name
            , SUM(absorb) AS absorb
            , COALESCE(ownerGUID, unitGUID) AS guid
        FROM (
            SELECT
                COALESCE(absorbedByUnitName, 'Unknown') AS unitName
                , COALESCE(absorbedByUnitGUID, 0) AS unitGUID
                , SUM(absorbed) AS absorb
            FROM events e
            LEFT JOIN actors a
            ON e.absorbedByUnitGUID = a.unitGUID
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
                OR a.unitGUID IS NULL
            )
            AND (
                a.encounterTime = :startTime
            OR  a.encounterTime IS NULL
            )
            AND absorbed > 0
            GROUP BY absorbedByUnitGUID
        ) s
        LEFT JOIN pets p
        ON s.unitGUID = p.petGUID
        GROUP BY guid
    ) m
    LEFT JOIN specs
    ON m.guid = specs.unitGUID
    WHERE
        timestamp = :startTime
    OR  timestamp IS NULL
    GROUP BY name
)
SELECT
    name || IIF(num > 1, ' (' || num || ')', '') AS name
    , PRINTF('%.2f%%', pct) AS pct
    , pct / MAX(pct) OVER() AS relpct
    , PRINTF('%,d', absorb) AS absorb
    , PRINTF('%,d', hps) AS hps
    , spec
    , name AS cleanname
FROM calc
UNION ALL
SELECT
    'Total' AS name
    , '-' AS pct
    , NULL AS relpct
    , PRINTF('%,d', SUM(absorb)) AS absorb
    , PRINTF('%,d', SUM(hps)) AS hps
    , NULL AS spec
    , NULL AS cleanname
FROM calc
ORDER BY relpct DESC