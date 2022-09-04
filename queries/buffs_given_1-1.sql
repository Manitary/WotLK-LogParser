SELECT
    spellName
    , a.spellID
    , COALESCE(MAX(timeStart, :startTime), :startTime)
    , COALESCE(MIN(timeEnd, :endTime), :endTime)
    , a.spellSchool
    , s.icon
FROM auras a
JOIN spell_db.spell_data s
ON a.spellID = s.spellID
WHERE
    targetGUID = :sourceGUID
AND sourceGUID = :targetGUID
AND auraType = :auraType
AND (
        timeStart <= :endTime
    OR  timeStart IS NULL
)
AND (
        timeEnd >= :startTime
    OR  timeEnd IS NULL
)
