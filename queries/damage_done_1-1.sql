SELECT
    t.sp AS spellName
    , PRINTF('%05.2f%% | %d', (dmg + absorbed) * 100.00 / (SUM(t.dmg) OVER() + SUM(t.absorbed) OVER()), dmg + absorbed) AS dmg
    , hit
    , CASE  WHEN c.casts > 0 THEN c.casts
            WHEN (
                    t.sp LIKE '%MeleeSwing'
                OR  t.sp = 'Auto Shot'
                OR  t.sp = 'Shoot'
                )
                THEN IFNULL(hit, 0) + IFNULL(miss, 0)
            ELSE '-'
            END AS numcasts
    , CASE WHEN crit > 0 THEN PRINTF('%d (%2.2f%%)', crit, crit * 100.00 / hit) ELSE '-' END AS crit
    , CASE WHEN miss > 0 THEN PRINTF('%d (%2.2f%%)', miss, miss * 100.00 / (hit + miss)) ELSE '-' END AS miss
    , CASE WHEN absorbed > 0 THEN PRINTF('%d (%2.2f%%)', absorbed, absorbed * 100.0 / (dmg + absorbed)) ELSE '-' END AS absorbed
    , CASE WHEN blocked > 0 THEN PRINTF('%d (%2.2f%%)', blocked, blocked * 100.0 / (blocked + dmg + absorbed)) ELSE '-' END AS blocked
    , CASE WHEN resisted > 0 THEN PRINTF('%d (%2.2f%%)', resisted, resisted * 100.0 / (resisted + dmg + absorbed)) ELSE '-' END AS resisted
FROM
    (
        SELECT
            CASE WHEN sourceName = :sourceName THEN spellName ELSE '(' || sourceName || ') ' || spellName END AS sp
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
        AND targetName = :targetName
        AND
            (
                eventName LIKE '%DAMAGE%'
            OR  eventName LIKE '%MISSED'
            OR  eventName = 'SPELL_CAST_SUCCESS'
            )
        AND spellName IS NOT NULL
        GROUP BY
            sp
    ) t
LEFT JOIN
    (
        SELECT
            CASE WHEN sourceName = :sourceName THEN spellName ELSE '(' || sourceName || ') ' || spellName END AS sp
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
        AND eventName = 'SPELL_CAST_SUCCESS'
        AND spellName IS NOT NULL
        GROUP BY
            sp
    ) c
ON
    t.sp = c.sp
ORDER BY
    dmg DESC