WITH calc AS (
    SELECT
        targetName
        , SUM(absorb) AS absorb
        , SUM(absorb) * 100.0 / (SUM(SUM(absorb)) OVER()) AS pct
        , spec
    FROM (
        WITH t AS (
            SELECT
                e.targetName
                , e.absorbed
                , COALESCE(q.ownerName, e.absorbedByUnitName) AS unitName
                , x.ownerName
                , x.amount AS link
                , spec
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
            LEFT JOIN pets q
            ON e.absorbedByUnitGUID = q.petGUID
            LEFT JOIN specs s
            ON e.targetGUID = s.unitGUID
            WHERE e.absorbed > 0
            AND e.timestamp >= :startTime
            AND e.timestamp <= :endTime
            AND (
                    e.absorbedByUnitName = :sourceName
                OR  q.ownerName = :sourceName
                OR  x.ownerName = :sourceName
            )
            AND (
                    s.timestamp = :startTime
                OR  s.timestamp IS NULL
            )
        )
        SELECT
            SUM(absorbed - COALESCE(link, 0)) AS absorb
            , targetName
            , spec
        FROM t
        WHERE unitName = :sourceName
        GROUP BY targetName
        HAVING absorb > 0
        UNION ALL
        SELECT
            SUM(link) AS absorb
            , targetName
            , spec
        FROM t
        WHERE ownerName = :sourceName
        GROUP BY targetName
        HAVING absorb > 0
    )
    GROUP BY targetName
)
SELECT
    targetName
    , PRINTF('%.2f%%', pct) AS pct
    , pct / MAX(pct) OVER() AS relpct
    , PRINTF('%,d', absorb) AS absorb
    , spec
FROM calc
ORDER BY relpct DESC
LIMIT 5