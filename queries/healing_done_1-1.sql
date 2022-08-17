SELECT
    spellName
    , heal - overheal AS heal
    , PRINTF('%d (%2.2f%%)', overheal, overheal*100.00/heal) AS overheal
    , hit
    , PRINTF('%d (%2.2f%%)', crit, crit*100.00/hit) AS crit
FROM
    (
        SELECT
            spellName
            , spellID
            , SUM(amount) + SUM(absorbed) AS heal
            , COUNT(amount) AS hit
            , SUM(overhealing) AS overheal
            , SUM(critical) AS crit
        FROM
            events
        WHERE
            timestamp >= :startTime
            AND timestamp <= :endTime
            AND sourceName = :sourceName
            AND targetName = :targetName
            AND eventName LIKE '%HEAL'
        GROUP BY
            spellID
    )
ORDER BY
    heal DESC