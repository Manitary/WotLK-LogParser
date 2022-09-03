SELECT
    spellName, spellID, COALESCE(MAX(timeStart, :startTime), :startTime), COALESCE(MIN(timeEnd, :endTime), :endTime)
FROM auras
JOIN actors
ON auras.targetGUID = actors.unitGUID
WHERE
    auraType = :auraType
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