WITH calc AS (
    SELECT
        sp AS spellName
        , heal * 100.0 / (SUM(heal) OVER()) AS pct
        , heal
        , icon
        , school
    FROM (
        SELECT
            CASE
                WHEN eventName LIKE '%HEAL' AND p1.ownerName IS NOT NULL THEN '(' || sourceName || ') '
        		WHEN absorbed > 0 AND p2.ownerName IS NOT NULL THEN '(' || absorbedByUnitName || ') '
        		ELSE ''
            END
            || IIF(eventName LIKE '%HEAL', spellName, COALESCE(absorbedBySpellName, 'Unknown'))
            || IIF(eventName LIKE 'SPELL_PERIODIC%' AND NOT absorbed > 0, ' (HoT)', '') AS sp
            , SUM(IIF(eventName LIKE '%HEAL', amount - overhealing, absorbed)) AS heal
            , IIF(eventName LIKE '%HEAL', s1.icon, s2.icon) AS icon
            , IIF(eventName LIKE '%HEAL', spellSchool, absorbedBySpellSchool) AS school
        FROM events e
        LEFT JOIN pets p1 ON e.sourceGUID = p1.petGUID
        LEFT JOIN pets p2 ON e.absorbedByUnitGUID = p2.petGUID
        LEFT JOIN spell_db.spell_data s1 ON e.spellID = s1.spellID
        LEFT JOIN spell_db.spell_data s2 ON e.absorbedBySpellID = s2.spellID
        WHERE
            timestamp >= :startTime
        AND timestamp <= :endTime
        AND (
                (
                    eventName LIKE '%HEAL'
                AND (
                        sourceName = :sourceName
                    OR	p1.ownerName = :sourceName
                )
            ) OR (
                    absorbed > 0
                AND (
                        absorbedByUnitName = :sourceName
                    OR	p2.ownerName = :sourceName
                )
            )
        )
        GROUP BY sp
    )
    WHERE heal > 0
)
SELECT
    spellName
    , PRINTF('%.2f%%', pct) AS pct
    , pct / MAX(pct) OVER() AS relpct
    , PRINTF('%,d', heal) AS heal
    , icon
    , school
FROM calc
ORDER BY relpct DESC
LIMIT 5