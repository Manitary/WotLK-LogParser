WITH calc AS (
    SELECT
        spellName
        , absorb * 100.0 / (SUM(absorb) OVER()) AS pct
        , absorb
        , icon
        , spellSchool
    FROM (
        SELECT
            spellName
            , SUM(absorbed) AS absorb
            , icon
            , spellSchool
        FROM events e
        LEFT JOIN pets
        ON e.absorbedByUnitGUID = pets.petGUID
        LEFT JOIN spell_db.spell_data s
        ON e.spellID = s.spellID
        WHERE
            e.timestamp >= :startTime
        AND e.timestamp <= :endTime
        AND (
                absorbedByUnitName = :sourceName
            OR  ownerName = :sourceName
        )
        AND absorbedBySpellID = :spellID
        AND absorbed > 0
        GROUP BY e.spellID
    )
)
SELECT
    spellName
    , PRINTF('%.2f%%', pct) AS pct
    , pct / MAX(pct) OVER() AS relpct
    , PRINTF('%,d', absorb) AS absorb
    , icon
    , spellSchool
FROM calc
ORDER BY relpct DESC
LIMIT 5