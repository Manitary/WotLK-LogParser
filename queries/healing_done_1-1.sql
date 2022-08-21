SELECT
    t.sp AS spellName
    , PRINTF('%05.2f%% | %d', (heal - overheal) * 100.0 / (SUM(heal) OVER() - SUM(overheal) OVER()), heal - overheal) AS heal
    , PRINTF('%d (%2.2f%%)', overheal, overheal * 100.00 / heal) AS overheal
    , CASE WHEN hit > 0 THEN hit ELSE '-' END AS hit
    , CASE  WHEN casts > 0 THEN casts
            WHEN t.sp NOT LIKE '%(HoT)' THEN IFNULL(hit, 0)
            ELSE '-'
            END AS numcasts
    , CASE WHEN crit > 0 THEN PRINTF('%d (%2.2f%%)', crit, crit * 100.0 / hit) ELSE '-' END AS crit
FROM
    (
        SELECT
            IIF(sourceName = :sourceName, '', '(' || sourceName || ') ') || spellName || IIF(eventName LIKE 'SPELL_PERIODIC%', ' (HoT)', '') AS sp
            , spellID
            , SUM(amount) + SUM(absorbed) AS heal
            , COUNT(amount) AS hit
            , SUM(overhealing) AS overheal
            , SUM(critical) AS crit
        FROM
            events
        LEFT JOIN
            pets
        ON
            events.sourceGUID = pets.petGUID
        WHERE
                timestamp >= :startTime
            AND timestamp <= :endTime
            AND (
                    sourceName = :sourceName
                OR  ownerName = :sourceName
                )
            AND targetName = :targetName
            AND eventName LIKE '%HEAL'
            AND spellName IS NOT NULL
        GROUP BY
            sp
    ) t
LEFT JOIN
    (
        SELECT
            IIF(sourceName = :sourceName, '', '(' || sourceName || ') ') || spellName || IIF(eventName LIKE 'SPELL_PERIODIC%', ' (HoT)', '') AS sp
            , COUNT(eventName) AS casts
        FROM
            events
        LEFT JOIN
            pets
        ON
            events.sourceGUID = pets.petGUID
        WHERE
            timestamp >= :startTime
        AND timestamp <= :endTime
        AND 
            (
                sourceName = :sourceName
            OR  ownerName = :sourceName
            )
        AND
            (
                eventName = 'SPELL_CAST_SUCCESS'
            OR  eventName = 'SPELL_CAST_START'
            )
        AND spellName IS NOT NULL
        GROUP BY
            sp
    ) c
ON
    t.sp = c.sp
ORDER BY
    heal DESC