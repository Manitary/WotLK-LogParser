SELECT
    t.sp AS spellName
    , PRINTF('%05.2f%% | %d', (dmg + absorbed) * 100.0 / (SUM(dmg) OVER() + SUM(absorbed) OVER()), dmg + absorbed) AS dmg
    , CASE WHEN hit > 0 THEN hit ELSE '-' END AS hit
    , CASE  WHEN casts > 0 THEN casts
            WHEN (
                    t.sp LIKE '%MeleeSwing'
                OR  t.sp = 'Auto Shot'
                OR  t.sp = 'Shoot'
                OR  t.sp NOT LIKE '%(DoT)'
                )
                THEN IFNULL(hit, 0) + IFNULL(miss, 0)
            ELSE '-'
            END AS numcasts
    , CASE WHEN crit > 0 THEN PRINTF('%d (%2.2f%%)', crit, crit * 100.0 / hit) ELSE '-' END AS crit
    , CASE WHEN miss > 0 THEN PRINTF('%d (%2.2f%%)', miss, miss * 100.0 / (hit + miss)) ELSE '-' END AS miss
    , CASE WHEN absorbed > 0 THEN PRINTF('%d (%2.2f%%)', absorbed, absorbed * 100.0 / (dmg + absorbed)) ELSE '-' END AS absorbed
    , CASE WHEN blocked > 0 THEN PRINTF('%d (%2.2f%%)', blocked, blocked * 100.0 / (blocked + dmg + absorbed)) ELSE '-' END AS blocked
    , CASE WHEN resisted > 0 THEN PRINTF('%d (%2.2f%%)', resisted, resisted * 100.0 / (resisted + dmg + absorbed)) ELSE '-' END AS resisted
FROM
    (
        SELECT
            IIF(sourceName = :sourceName, '', '(' || sourceName || ') ') || spellName || IIF(eventName LIKE 'SPELL_PERIODIC%', ' (DoT)', '') AS sp
            , spellID
            , SUM(amount) AS dmg
            , COUNT(amount) AS hit
            , COUNT(missType) AS miss
            , SUM(absorbed) AS absorbed
            , SUM(resisted) AS resisted
            , SUM(blocked) AS blocked
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
        AND 
            (
                sourceName = :sourceName
            OR  ownerName = :sourceName
            )
        AND
            (
                eventName LIKE '%DAMAGE%'
            OR  eventName LIKE '%MISSED'
            )
        AND spellName IS NOT NULL
        GROUP BY
            sp
    ) t
LEFT JOIN
    (
        SELECT
            IIF(sourceName = :sourceName, '', '(' || sourceName || ') ') || spellName || IIF(eventName LIKE 'SPELL_PERIODIC%', ' (DoT)', '') AS sp
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
    dmg DESC