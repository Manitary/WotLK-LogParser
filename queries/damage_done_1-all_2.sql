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
            , MIN(amount) AS mindmg
            , MAX(amount) AS maxdmg
            , AVG(amount) AS avgdmg
            , spellSchool AS school
        FROM events
        LEFT JOIN pets
        ON events.sourceGUID = pets.petGUID
        WHERE
            spellID = :spellID
        AND timestamp >= :startTime
        AND timestamp <= :endTime
        AND sourceName = :sourceName
        AND (
                eventName LIKE '%DAMAGE%'
            OR  missType = 'ABSORBED'
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
ORDER BY relpct DESC