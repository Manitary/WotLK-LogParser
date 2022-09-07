WITH calc AS (
    SELECT
        IIF(crit > 0, 'Crit', 'Hit') AS crit
        , (dmg + absorbed) * 100.0 / (SUM(dmg) OVER() + SUM(absorbed) OVER()) AS pct
        , dmg + absorbed AS dmg
        , mindmg
        , maxdmg
        , avgdmg
        , school
    FROM (
        SELECT
            critical AS crit
            , SUM(amount) AS dmg
            , SUM(absorbed) AS absorbed
            , MIN(amount + absorbed) AS mindmg
            , MAX(amount + absorbed) AS maxdmg
            , AVG(amount + absorbed) AS avgdmg
            , MAX(school & 1) + MAX(school & 2) + MAX(school & 4) + MAX(school & 8) + MAX(school & 16) + MAX(school & 32) + MAX(school & 64) AS school
        FROM events
        WHERE
            spellID = :spellID
        AND timestamp >= :startTime
        AND timestamp <= :endTime
        AND targetName = :targetName
        AND (
                eventName LIKE '%DAMAGE%'
            OR  missType = 'ABSORB'
        )
        GROUP BY critical
    )
)
SELECT
    crit
    , PRINTF('%.2f%%', pct) AS pct
    , pct / MAX(pct) OVER() AS relpct
    , PRINTF('%,d', dmg) AS dmg
    , mindmg
    , maxdmg
    , avgdmg
    , school
FROM calc
WHERE dmg > 0
ORDER BY relpct DESC