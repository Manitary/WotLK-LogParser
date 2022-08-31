WITH calc AS (
    SELECT
        t.sp AS spellName
        , (heal - overheal) * 100.0 / (SUM(heal) OVER() - SUM(overheal) OVER()) AS pct
        , heal - overheal AS heal
        , overheal
        , CASE WHEN hit > 0 THEN hit ELSE '-' END AS hit
        , CASE  WHEN casts > 0 THEN casts
                WHEN t.sp NOT LIKE '%(HoT)' THEN IFNULL(hit, 0)
                ELSE '-'
                END AS numcasts
        , CASE WHEN crit > 0 THEN PRINTF('%,d (%2.2f%%)', crit, crit * 100.0 / hit) ELSE '-' END AS crit
        , icon
        , school
    FROM (
        SELECT
            IIF(sourceName = :sourceName, '', '(' || sourceName || ') ') || spellName || IIF(eventName LIKE 'SPELL_PERIODIC%', ' (HoT)', '') AS sp
            , s.spellID AS spellID
            , SUM(amount) + SUM(absorbed) AS heal
            , COUNT(amount) AS hit
            , SUM(overhealing) AS overheal
            , SUM(critical) AS crit
            , icon
            , MAX(spellSchool) AS school
        FROM events
        LEFT JOIN pets
        ON events.sourceGUID = pets.petGUID
        LEFT JOIN spell_db.spell_data s
        ON events.spellID = s.spellID
        WHERE
            timestamp >= :startTime
        AND timestamp <= :endTime
        AND (
                sourceName = :sourceName
            OR  ownerName = :sourceName
        )
        AND eventName LIKE '%HEAL'
        AND spellName IS NOT NULL
        GROUP BY sp
    ) t
    LEFT JOIN (
        SELECT
            IIF(sourceName = :sourceName, '', '(' || sourceName || ') ') || spellName || IIF(eventName LIKE 'SPELL_PERIODIC%', ' (HoT)', '') AS sp
            , COUNT(eventName) AS casts
        FROM events
        LEFT JOIN pets
        ON events.sourceGUID = pets.petGUID
        WHERE
            timestamp >= :startTime
        AND timestamp <= :endTime
        AND (
                sourceName = :sourceName
            OR  ownerName = :sourceName
        )
        AND (
                eventName = 'SPELL_CAST_SUCCESS'
            OR  eventName = 'SPELL_CAST_START'
        )
        AND spellName IS NOT NULL
        GROUP BY sp
    ) c
    ON t.sp = c.sp
)
SELECT
    spellName
    , PRINTF('%.2f%%', pct) AS pct
    , pct / MAX(pct) OVER() AS relpct
    , PRINTF('%,d', heal) AS heal
    , PRINTF('%,d (%2.2f%%)', overheal, overheal * 100.00 / heal) AS overheal
    , hit
    , numcasts
    , crit
    , icon
    , school
FROM calc
ORDER BY relpct DESC