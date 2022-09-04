SELECT
    sourceGUID
    , targetGUID
    , COALESCE(MAX(timeStart, :startTime), :startTime)
    , COALESCE(MIN(timeEnd, :endTime), :endTime)
FROM auras
WHERE
    sourceGUID = :targetGUID
AND spellID = :spellID
AND auraType = :auraType
AND (
        timeStart <= :endTime
    OR  timeStart IS NULL
)
AND (
        timeEnd >= :startTime
    OR  timeEnd IS NULL
)
