SELECT
    sp AS spellName
    , dmg + absorbed AS dmg
    , hit
    , PRINTF('%d (%2.2f%%)', crit, crit*100.00/hit) AS crit
    , miss
    , absorbed
    , blocked
    , resisted
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
        AND
            (
                eventName LIKE '%DAMAGE%'
            OR  eventName LIKE '%MISSED'
            )
        AND spellName IS NOT NULL 
        GROUP BY
            sp
    )
ORDER BY
    dmg DESC