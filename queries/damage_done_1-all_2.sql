WITH calc AS (
    SELECT
        IIF(crit > 0, 'Crit', 'Hit') AS crit
        , SUM(dmg) * 100.0 / (SUM(SUM(dmg)) OVER()) AS pct
        , SUM(dmg) AS dmg
        , MIN(dmg) AS mindmg
        , MAX(dmg) AS maxdmg
        , AVG(dmg) AS avgdmg
        , MAX(school & 1) + MAX(school & 2) + MAX(school & 4) + MAX(school & 8) + MAX(school & 16) + MAX(school & 32) + MAX(school & 64) AS school
    FROM (
        SELECT
            COALESCE(critical, 0) AS crit
            , COALESCE(amount, 0) + COALESCE(absorbed, 0) AS dmg
            , school
        FROM events
        LEFT JOIN pets
        ON events.sourceGUID = pets.petGUID
        LEFT JOIN actors
        ON events.sourceGUID = actors.unitGUID
        WHERE
            spellID = :spellID
        AND timestamp >= :startTime
        AND timestamp <= :endTime
        AND sourceName = :sourceName
        AND (
                isPet IS NULL
            OR  ownerName = :ownerName
        )
        AND (
                eventName LIKE '%DAMAGE%'
            OR  missType = 'ABSORB'
        )
    )
    GROUP BY crit
)
SELECT
    crit
    , PRINTF('%.2f%%', pct) AS pct
    , pct / MAX(pct) OVER() AS relpct
    , PRINTF('%,d', dmg) AS dmg
    , PRINTF('%,d', mindmg) AS mindmg
    , PRINTF('%,d', maxdmg) AS maxdmg
    , PRINTF('%,d', avgdmg) AS avgdmg
    , school
FROM calc
ORDER BY relpct DESC