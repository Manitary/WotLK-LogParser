WITH calc AS (
    SELECT
        name AS spellName
        , absorb * 100.0 / (SUM(absorb) OVER()) AS pct
        , absorb
        , absorb / (JULIANDAY(:endTime) - JULIANDAY(:startTime)) / 86400 AS hps
        , icon
        , school
        , spellID
        , source
    FROM (
        SELECT
            absorbedBySpellName AS name
            , absorbedBySpellSchool AS school
            , SUM(absorbed) AS absorb
            , icon
            , absorbedBySpellID AS spellID
            , absorbedByUnitName AS source
        FROM events e
        LEFT JOIN pets
        ON e.absorbedByUnitGUID = pets.petGUID
        LEFT JOIN spell_db.spell_data s
        ON e.absorbedBySpellID = s.spellID
        WHERE
            timestamp >= :startTime
        AND timestamp <= :endTime
        AND (
                absorbedByUnitName = :sourceName
            OR  ownerName = :sourceName
        )
        AND targetName = :targetName
        AND absorbed > 0
        GROUP BY absorbedBySpellID
    )
)
SELECT
    spellName
    , PRINTF('%.2f%%', pct) AS pct
    , pct / MAX(pct) OVER() AS relpct
    , PRINTF('%,d', absorb) AS absorb
    , PRINTF('%,d', hps) AS hps
    , icon
    , school
    , spellID
    , source
FROM calc
UNION ALL
SELECT
    'Total' AS spellName
    , '-' AS pct
    , NULL AS relpct
    , PRINTF('%,d', SUM(absorb)) AS absorb
    , PRINTF('%,d', SUM(hps)) AS hps
    , NULL AS icon
    , NULL AS school
    , NULL AS spellID
    , NULL AS source
FROM calc
ORDER BY relpct DESC