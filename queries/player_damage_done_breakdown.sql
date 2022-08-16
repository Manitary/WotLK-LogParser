SELECT
    spellName
    , dmg
    , hit
    , PRINTF('%d (%2.2f%%)', crit, crit*100.00/hit) AS crit
    , miss
    , resist AS resisted
    , blck AS blocked
    , absorb AS absorbed
FROM
    (
        SELECT
            spellName
            , spellID
            , SUM(amount) AS dmg
            , COUNT(amount) AS hit
            , COUNT(missType) AS miss
            , SUM(absorbed) AS absorb
            , SUM(resisted) AS resist
            , SUM(blocked) AS blck
            , SUM(critical) AS crit
        FROM
            events
        WHERE
            timestamp >= :startTime AND timestamp <= :endTime
        AND sourceName = :sourceName
        AND (eventName LIKE '%DAMAGE%' OR eventName LIKE '%MISSED')
        AND spellName IS NOT NULL 
        GROUP BY spellID
        ORDER BY dmg DESC
    )