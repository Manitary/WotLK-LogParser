WITH calc AS (
    SELECT
        x.sp AS spellName
        , heal * 100.0 / (SUM(heal) OVER()) AS pct
        , heal
        , icon
        , school
        , IIF(hit > 0, hit, '-') AS hit
        , IIF(crit > 0, PRINTF('%,d (%.2f%%)', crit, crit * 100.0 / hit), '-') AS crit
        , IIF(overheal IS NULL, '-', PRINTF('%,d (%.2f%%)', overheal, overheal * 100.0 / (overheal + heal))) AS overheal
        , source
        , owner
        , IIF(casts > 0, casts, '-') casts
        , eventName
        , spellID
    FROM (
        (SELECT
            CASE
              WHEN eventName LIKE '%HEAL' AND p1.ownerName IS NOT NULL THEN '(' || sourceName || ') '
        			WHEN absorbed > 0 AND p2.ownerName IS NOT NULL THEN '(' || absorbedByUnitName || ') '
        			ELSE ''
            END
            || IIF(eventName LIKE '%HEAL', spellName, COALESCE(absorbedBySpellName, 'Unknown'))
            || IIF(eventName LIKE 'SPELL_PERIODIC%' AND NOT absorbed > 0, ' (HoT)', '') AS sp
            , SUM(IIF(eventName LIKE '%HEAL', amount - overhealing, absorbed)) AS heal
            , SUM(overhealing) AS overheal
            , IIF(eventName LIKE '%HEAL', SUM(critical), NULL) AS crit
            , COUNT(IIF(eventName LIKE '%HEAL', 1, 0)) AS hit
            , IIF(eventName LIKE '%HEAL', s1.icon, s2.icon) AS icon
            , IIF(eventName LIKE '%HEAL', spellSchool, absorbedBySpellSchool) AS school
            , IIF(eventName LIKE '%HEAL', sourceName, absorbedByUnitName) AS source
            , IIF(eventName LIKE '%HEAL', eventName, 'absorb') AS eventName
            , IIF(eventName LIKE '%HEAL', e.spellID, e.absorbedBySpellID) AS spellID
          	, IIF(eventName LIKE '%HEAL', p1.ownerName, p2.ownerName) AS owner
        FROM events e
        LEFT JOIN pets p1 ON e.sourceGUID = p1.petGUID
        LEFT JOIN pets p2 ON e.absorbedByUnitGUID = p2.petGUID
        LEFT JOIN spell_db.spell_data s1 ON e.spellID = s1.spellID
        LEFT JOIN spell_db.spell_data s2 ON e.absorbedBySpellID = s2.spellID
        WHERE
            timestamp >= :startTime
        AND timestamp <= :endTime
        AND targetName = :targetName
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
        GROUP BY sp) x
        LEFT JOIN
        (SELECT
            IIF(sourceName = :sourceName, '', '(' || sourceName || ') ') || spellName || IIF(eventName LIKE 'SPELL_PERIODIC%', ' (HoT)', '') AS sp
            , COUNT(eventName) AS casts
        FROM events e
        LEFT JOIN pets p
        ON e.sourceGUID = p.petGUID
        WHERE
            e.timestamp >= :startTime
        AND e.timestamp <= :endTime
        AND (
                sourceName = :sourceName
            OR  ownerName = :sourceName
        )
        AND (
                eventName = 'SPELL_CAST_SUCCESS'
            OR  eventName = 'SPELL_CAST_START'
        )
        GROUP BY sp) c
    		ON x.sp = c.sp
    )
    WHERE heal > 0
)
SELECT
    spellName
    , PRINTF('%.2f%%', pct) AS pct
    , pct / MAX(pct) OVER() AS relpct
    , PRINTF('%,d', heal) AS heal
    , overheal
    , hit
    , crit
    , casts
    , icon
    , school
	  , spellID
    , source
    , owner
    , eventName
FROM calc
ORDER BY relpct DESC