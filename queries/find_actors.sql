SELECT
    a.unitName
    , isPlayer
    , isPet
    , isNPC
    , a.unitGUID
    , spec
FROM actors a
LEFT JOIN specs s
ON a.unitGUID = s.unitGUID
WHERE
    encounterTIme = :startTime
AND (
        timestamp = :startTime
    OR  timestamp IS NULL
)
GROUP BY a.unitName
ORDER BY
    a.isPlayer DESC
    , a.unitName
