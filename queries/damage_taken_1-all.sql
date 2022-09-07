WITH calc AS (
    SELECT
        sp AS spellName
        , (dmg + absorbed) * 100.0 / (SUM(dmg) OVER() + SUM(absorbed) OVER()) AS pct
        , dmg + absorbed AS dmg
        , hit
        , miss
        , absorbed
        , blocked
        , resisted
        , icon
        , school
        , spellID
        , targetName
    FROM (
        SELECT
            spellName || IIF(eventName LIKE 'SPELL_PERIODIC%', ' (DoT)', '') AS sp
            , s.spellID AS spellID
            , SUM(amount) AS dmg
            , COUNT(amount) AS hit
            , COUNT(missType) AS miss
            , SUM(absorbed) AS absorbed
            , SUM(resisted) AS resisted
            , SUM(blocked) AS blocked
            , icon
            , MAX(school & 1) + MAX(school & 2) + MAX(school & 4) + MAX(school & 8) + MAX(school & 16) + MAX(school & 32) + MAX(school & 64) AS school
            , s.spellID
            , targetName
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
        GROUP BY sp, s.spellID
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
    , PRINTF('%,d (%.2f%%)', blocked, blocked * 100.0 / (dmg + blocked)) AS blocked
    , PRINTF('%,d (%.2f%%)', resisted, resisted * 100.0 / (dmg + blocked + resisted)) AS resisted
    , icon
    , school
    , spellID
    , targetName
FROM calc
ORDER BY relpct DESC