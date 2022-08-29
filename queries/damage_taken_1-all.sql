SELECT
    spellName
    , PRINTF('%05.2f%% | %d', (dmg + absorbed + blocked + resisted) * 100.0 / (SUM(dmg) OVER() + SUM(absorbed) OVER() + SUM(blocked) OVER() + SUM(resisted) OVER()), dmg + absorbed + blocked + resisted) AS dmg
    , hit
    , PRINTF('%,d (%.2f%%)', miss, miss * 100 / (hit + miss)) AS miss
    , PRINTF('%,d (%.2f%%)', absorbed, absorbed * 100 / (dmg + absorbed + blocked)) AS absorbed
    , PRINTF('%,d (%.2f%%)', blocked, blocked * 100 / (dmg + absorbed + blocked)) AS blocked
    , PRINTF('%,d (%.2f%%)', resisted, resisted * 100 / (dmg + absorbed + blocked)) AS resisted
    , crit
    , icon
FROM (
    SELECT
        spellName
        , s.spellID AS spellID
        , SUM(amount) AS dmg
        , COUNT(amount) AS hit
        , COUNT(missType) AS miss
        , SUM(absorbed) AS absorbed
        , SUM(resisted) AS resisted
        , SUM(blocked) AS blocked
        , SUM(critical) AS crit
        , icon
    FROM events
    LEFT JOIN spell_db.spell_data s
    ON events.spellID = s.spellID
    WHERE
        timestamp >= :startTime
    AND timestamp <= :endTime
    AND targetName = :targetName
    AND
        (
            eventName LIKE '%DAMAGE%'
        OR  eventName LIKE '%MISSED'
        )
    AND spellName IS NOT NULL
    GROUP BY
        s.spellID
)
ORDER BY
    dmg DESC