SELECT
    spellName
    , a.spellID
    , COALESCE(MAX(timeStart, :startTime), :startTime)
    , COALESCE(MIN(timeEnd, :endTime), :endTime)
    , a.spellSchool
    , s.icon
FROM auras a
JOIN actors
ON a.targetGUID = actors.unitGUID
JOIN spell_db.spell_data s
ON a.spellID = s.spellID
WHERE
    sourceGUID = :sourceGUID
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