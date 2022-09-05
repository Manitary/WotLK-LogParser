WITH calc AS (
    SELECT
        spellName
        , (dmg + absorbed + blocked + resisted) * 100.0 / (SUM(dmg) OVER() + SUM(absorbed) OVER() + SUM(blocked) OVER() + SUM(resisted) OVER()) AS pct
        , dmg + absorbed + blocked + resisted AS dmg
        , hit
        , miss
        , absorbed
        , blocked
        , resisted
        , crit
        , icon
        , school
    FROM (
        SELECT
            spellName || IIF(eventName LIKE 'SPELL_PERIODIC%', ' (DoT)', '') AS spellName
            , s.spellID AS spellID
            , SUM(amount) AS dmg
            , COUNT(amount) AS hit
            , COUNT(missType) AS miss
            , SUM(absorbed) AS absorbed
            , SUM(resisted) AS resisted
            , SUM(blocked) AS blocked
            , SUM(critical) AS crit
            , icon
            , MAX(school) AS school
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
)
SELECT
    spellName
    , PRINTF('%.2f%%', pct) AS pct
    , pct / MAX(pct) OVER() AS relpct
    , PRINTF('%,d', dmg) AS dmg
    , hit
    , PRINTF('%,d (%.2f%%)', miss, miss * 100.0 / (hit + miss)) AS miss
    , PRINTF('%,d (%.2f%%)', absorbed, absorbed * 100.0 / dmg) AS absorbed
    , PRINTF('%,d (%.2f%%)', blocked, blocked * 100.0 / dmg) AS blocked
    , PRINTF('%,d (%.2f%%)', resisted, resisted * 100.0 / dmg) AS resisted
    , crit
    , icon
    , school
FROM calc
ORDER BY relpct DESC