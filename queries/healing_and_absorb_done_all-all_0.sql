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
		WHERE
				e.timestamp >= :startTime
		AND	e.timestamp <= :endTime
		AND (
					(
					eventName LIKE '%HEAL'
			AND sourceName = :sourceName
			) OR (
					absorbed > 0
			AND absorbedByUnitName = :sourceName
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