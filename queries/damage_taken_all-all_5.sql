WITH calc AS (
    SELECT
        type
        , tot * 100.0 / (SUM(tot) OVER()) AS pct
        , tot
    FROM (
        SELECT 'Damage' AS type, SUM(amount) AS tot
        FROM events
        WHERE targetName = :targetName
        AND timestamp >= :startTime
        AND timestamp <= :endTime
        AND eventName LIKE '%DAMAGE'
        UNION ALL
        SELECT 'Absorbed' AS type, SUM(absorbed) AS tot
        FROM events
        WHERE targetName = :targetName
        AND timestamp >= :startTime
        AND timestamp <= :endTime
        AND (
                eventName LIKE '%DAMAGE'
            OR  missType = 'ABSORB'
        )
        UNION ALL
        SELECT 'Blocked' AS type, SUM(blocked) AS tot
        FROM events
        WHERE targetName = :targetName
        AND timestamp >= :startTime
        AND timestamp <= :endTime
        AND (
                eventName LIKE '%DAMAGE'
            OR  missType = 'BLOCK'
        )
        UNION ALL
        SELECT 'Resisted' AS type, SUM(resisted) AS tot
        FROM events
        WHERE targetName = :targetName
        AND timestamp >= :startTime
        AND timestamp <= :endTime
        AND (
                eventName LIKE '%DAMAGE'
            OR  missType = 'RESIST'
        )
    )
)
SELECT
    type
    , PRINTF('%.2f%%', pct) AS pct
    , pct / MAX(pct) OVER() AS relpct
    , PRINTF('%,d', tot) AS tot
FROM calc
WHERE tot > 0
ORDER BY relpct DESC