WITH calc AS (
    SELECT
        IIF(crit > 0, 'Crit', 'Hit') AS crit
        , SUM(eheal) * 100.0 / (SUM(SUM(eheal)) OVER()) AS pct
        , SUM(eheal) AS eheal
        , SUM(oheal) AS oheal
        , MIN(eheal) AS mineheal
        , MAX(eheal) AS maxeheal
        , AVG(eheal) AS avgeheal
        , MIN(heal) AS minheal
        , MAX(heal) AS maxheal
        , AVG(heal) AS avgheal
        , MAX(school & 1) + MAX(school & 2) + MAX(school & 4) + MAX(school & 8) + MAX(school & 16) + MAX(school & 32) + MAX(school & 64) AS school
    FROM (
        SELECT
            COALESCE(critical, 0) AS crit
            , COALESCE(amount, 0) + COALESCE(absorbed, 0) - COALESCE(overhealing, 0) AS eheal
            , COALESCE(overhealing, 0) AS oheal
            , COALESCE(amount, 0) + COALESCE(absorbed, 0) AS heal
            , spellSchool AS school
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
        AND eventName = :eventName
    )
    GROUP BY crit
)
SELECT
    crit
    , PRINTF('%.2f%%', pct) AS pct
    , pct / MAX(pct) OVER() AS relpct
    , PRINTF('%,d', eheal) AS eheal
    , PRINTF('%,d', oheal) AS oheal
    , PRINTF('%,d', mineheal) AS mineheal
    , PRINTF('%,d', maxeheal) AS maxeheal
    , PRINTF('%,d', avgeheal) AS avgeheal
    , PRINTF('%,d', minheal) AS minheal
    , PRINTF('%,d', maxheal) AS maxheal
    , PRINTF('%,d', avgheal) AS avgheal
    , school
FROM calc
ORDER BY relpct DESC