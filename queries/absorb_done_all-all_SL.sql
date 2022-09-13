WITH calc AS (
    SELECT
        z.unitName AS name
        , SUM(absorb) AS absorb
        , SUM(absorb) * 100.0 / (SUM(SUM(absorb)) OVER()) AS pct
        , SUM(absorb) / (JULIANDAY(:endTime) - JULIANDAY(:startTime)) / 86400 AS hps
        , spec
        , COUNT(z.unitName) AS num
    FROM (
        WITH t AS (
            SELECT
                e.absorbed
                , COALESCE(q.ownerName, e.absorbedByUnitName) AS unitName
                , x.ownerName
                , x.amount AS link
            FROM events e
            LEFT JOIN (
                SELECT
                    f.timestamp
                    , f.amount
                    , p.ownerName
                    , p.ownerGUID
                FROM events f
                JOIN pets p ON f.targetGUID = p.petGUID
                WHERE f.eventName = 'SPELL_DAMAGE' AND f.spellID = 25228
            ) x
            ON (e.timestamp = x.timestamp AND e.targetGUID = x.ownerGUID)
            LEFT JOIN actors a1
            ON e.absorbedByUnitGUID = a1.unitGUID
            LEFT JOIN actors a2
            ON x.ownerGUID = a1.unitGUID
            LEFT JOIN pets q
            ON e.absorbedByUnitGUID = q.petGUID
            WHERE e.absorbed > 0
            AND e.timestamp >= :startTime
            AND e.timestamp <= :endTime
            AND (
                    a1.isPlayer = :affiliation
                OR  a1.isPet = :affiliation
                OR  (
                        :affiliation = 0
                    AND a1.isNPC = 1
                )
                OR a1.unitGUID IS NULL
            )
            AND (
                    a1.encounterTime = :startTime
                OR  a1.encounterTime IS NULL
            )
            AND (
                    a2.isPlayer = :affiliation
                OR  (
                        :affiliation = 0
                    AND a2.isNPC = 1
                )
                OR  a2.unitGUID IS NULL
            )
            AND (
                    a2.encounterTime = :startTime
                OR  a2.encounterTime IS NULL
            )
        )
        SELECT
            SUM(absorbed - COALESCE(link, 0)) AS absorb
            , unitName
        FROM t
        GROUP BY unitName
        HAVING absorb > 0
        UNION ALL
        SELECT
            SUM(link) AS absorb
            , ownerName AS unitName
        FROM t
        GROUP BY ownerName
        HAVING absorb > 0
    ) z
    LEFT JOIN specs s
    ON z.unitName = s.unitName
    WHERE
        s.timestamp = :startTime
    OR  s.timestamp IS NULL
    GROUP BY z.unitName
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