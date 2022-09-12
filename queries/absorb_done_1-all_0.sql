WITH calc AS (
    SELECT
        targetName
        , absorb * 100.0 / (SUM(absorb) OVER()) AS pct
        , absorb
        , spec
    FROM (
        SELECT
            targetName
            , SUM(absorbed) AS absorb
            , spec
        FROM events e
        LEFT JOIN pets
        ON e.absorbedByUnitGUID = pets.petGUID
        LEFT JOIN specs s
        ON e.targetGUID = s.unitGUID
        WHERE
            e.timestamp >= :startTime
        AND e.timestamp <= :endTime
        AND (
                absorbedByUnitName = :sourceName
            OR  ownerName = :sourceName
        )
        AND absorbed > 0
        AND (
                s.timestamp = :startTime
            OR  s.timestamp IS NULL
        )
        AND absorbedBySpellID = :spellID
        GROUP BY targetName
    )
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