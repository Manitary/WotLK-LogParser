WITH calc AS (
	SELECT	
  	targetName
    , heal * 100.0 / (SUM(heal) OVER()) AS pct
    , heal
    , spec
	FROM (
		SELECT
			targetName
			, SUM(IIF(eventName LIKE '%HEAL', amount - overhealing, absorbed)) AS heal
			, spec
		FROM events e
		LEFT JOIN specs s ON (e.targetGUID = s.unitGUID AND s.timestamp = :startTime)
		LEFT JOIN pets p1 ON e.sourceGUID = p1.petGUID
		LEFT JOIN pets p2 ON e.absorbedByUnitGUID = p2.petGUID
		WHERE
				e.timestamp >= :startTime
		AND	e.timestamp <= :endTime
		AND (
					(
					eventName = :eventName
			AND sourceName = :sourceName
			AND spellID = :spellID
			AND (
						p1.ownerName IS NULL
					OR p1.ownerName = :ownerName
				)
			) OR (
					:eventName = 'absorb'
			AND	absorbed > 0
			AND absorbedByUnitName = :sourceName
			AND absorbedBySpellID = :spellID
			AND	(
						p2.ownerName IS NULL
					OR p2.ownerName = :ownerName
				)
			)
		)
		GROUP BY targetName
	)
)
SELECT
    targetName
    , PRINTF('%.2f%%', pct) AS pct
    , pct / MAX(pct) OVER() AS relpct
    , PRINTF('%,d', heal) AS heal
    , spec
FROM calc
ORDER BY relpct DESC
LIMIT 5