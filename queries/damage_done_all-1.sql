WITH calc AS (
    SELECT
        name
        , dmg
        , dmg * 100.00 / (SUM(dmg) OVER()) AS dmgpct
        , dmg / (JULIANDAY(:endTime) - JULIANDAY(:startTime)) / 86400 AS dps
        , spec
    FROM (
        SELECT
            s.name AS name
            , SUM(s.dmg) AS dmg
            , COALESCE(p.ownerGUID, s.sguid) AS owner
        FROM (
            SELECT
                events.sourceName AS name
                , SUM(events.amount) + SUM(events.absorbed) AS dmg
                , events.sourceGUID AS sguid
            FROM events
            JOIN actors
            ON events.sourceGUID = actors.unitGUID
            WHERE
                events.timestamp >= :startTime
            AND events.timestamp <= :endTime
            AND (
                    actors.isPlayer = :affiliation
                OR  actors.isPet = :affiliation
                OR  (
                        :affiliation = 0
                    AND actors.isNPC = 1
                )
            )
            AND events.targetName = :targetName
            AND events.eventName LIKE '%DAMAGE'
            GROUP BY
                events.sourceGUID
        ) s
        LEFT JOIN pets p
        ON s.sguid = p.petGUID
        GROUP BY
            owner
    ) m
    LEFT JOIN specs
    ON m.owner = specs.unitGUID
    GROUP BY
        owner
)
SELECT
    name
    , PRINTF('%.2f', dmgpct) AS pct
    , PRINTF('%,d', dmg) AS dmg
    , PRINTF('%,d', dps) AS dps
    , spec
    , dmgpct
FROM calc
UNION ALL
SELECT
    'Total' AS name
    , '-' AS pct
    , PRINTF('%,d', SUM(dmg)) AS dmg
    , PRINTF('%,d', SUM(dps)) AS dps
    , NULL AS spec
    , NULL AS dmgpct
FROM calc
ORDER BY
    dmgpct DESC
