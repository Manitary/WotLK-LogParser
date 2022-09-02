SELECT
    spellName, spellID, COALESCE(MAX(timeStart, :startTime), :startTime), COALESCE(MIN(timeEnd, :endTime), :endTime)
FROM auras
WHERE
    targetGUID = :targetGUID
AND sourceGUID = :sourceGUID
AND auraType = 'BUFF'
AND (
        timeStart <= :endTime
    OR  timeStart IS NULL
)
AND (
        timeEnd >= :startTime
    OR  timeEnd IS NULL
)
