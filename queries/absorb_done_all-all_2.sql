WITH calc AS (
    SELECT
        spellName
        , SUM(absorb) AS absorb
        , SUM(absorb) * 100.0 / (SUM(SUM(absorb)) OVER()) AS pct
        , icon
        , spellSchool
    FROM (
        WITH t AS (
            SELECT
                e.spellName
                , e.spellID
                , e.absorbed
                , COALESCE(q.ownerName, e.absorbedByUnitName) AS unitName
                , x.ownerName
                , x.amount AS link
                , icon
                , spellSchool
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
            LEFT JOIN spell_db.spell_data s
            ON e.spellID = s.spellID
            WHERE e.absorbed > 0
            AND e.timestamp >= :startTime
            AND e.timestamp <= :endTime
            AND (
                    e.absorbedByUnitName = :sourceName
                OR  q.ownerName = :sourceName
                OR  x.ownerName = :sourceName
            )
        )
        SELECT
            SUM(absorbed - COALESCE(link, 0)) AS absorb
            , spellName
            , spellID
            , icon
            , spellSchool
        FROM t
        WHERE unitName = :sourceName
        GROUP BY spellID
        HAVING absorb > 0
        UNION ALL
        SELECT
            SUM(link) AS absorb
            , spellName
            , spellID
            , icon
            , spellSchool
        FROM t
        WHERE ownerName = :sourceName
        GROUP BY spellID
        HAVING absorb > 0
    )
    GROUP BY spellID
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