SELECT
    spellName
    , dmg + absorbed + blocked AS dmg
    , hit
    , PRINTF('%d (%2.2f%%)', miss, miss*100/(hit+miss)) AS miss
    , absorbed
    , blocked
    , resisted
    , crit
FROM
    (
        SELECT
            spellName
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
        WHERE
            timestamp >= :startTime
        AND timestamp <= :endTime
        AND sourceName = :sourceName
        AND targetName = :targetName
        AND
            (
                eventName LIKE '%DAMAGE%'
            OR  eventName LIKE '%MISSED'
            )
        AND spellName IS NOT NULL
        GROUP BY
            spellID
        ORDER BY
            dmg DESC
    )