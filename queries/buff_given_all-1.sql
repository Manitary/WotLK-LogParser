SELECT
    sourceGUID
    , targetGUID
    , COALESCE(MAX(timeStart, :startTime), :startTime)
    , COALESCE(MIN(timeEnd, :endTime), :endTime)
FROM auras
JOIN actors
ON auras.sourceGUID = actors.unitGUID
WHERE
    spellID = :spellID
AND targetGUID = :sourceGUID
AND auraType = :auraType
AND (
        timeStart <= :endTime
    OR  timeStart IS NULL
)
AND (
        timeEnd >= :startTime
    OR  timeEnd IS NULL
)
AND (
        actors.isPlayer = :affiliation
    OR  actors.isPet = :affiliation
    OR (
            :affiliation = 0
        AND actors.isNPC = 1
    )
)