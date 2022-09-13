WITH calc AS (
	SELECT
		SUM(eheal) AS eheal
		, SUM(overheal) AS overheal
		, x.unitName AS name
		, spec
		, SUM(eheal) * 100.0 / (SUM(eheal) OVER()) AS pct
		, SUM(overheal) * 100.0 / SUM(eheal + overheal) AS overhealpct
		, SUM(eheal) / (JULIANDAY(:endTime) - JULIANDAY(:startTime)) / 86400 AS ehps
    	, SUM(eheal + overheal) / (JULIANDAY(:endTime) - JULIANDAY(:startTime)) / 86400 AS hps
    	, COUNT(x.unitName) AS num
	FROM (
		SELECT
			SUM(eheal) AS eheal
			, SUM(overheal) AS overheal
			, COALESCE(ownerGUID, unitGUID) AS unitGUID
			, COALESCE(ownerName, unitName) AS unitName
		FROM (	
			SELECT
				COALESCE(SUM(IIF(eventName LIKE '%HEAL', amount - overhealing, absorbed)), 0) AS eheal
				, COALESCE(SUM(overhealing), 0) AS overheal
				, IIF(eventName LIKE '%HEAL', sourceGUID, absorbedByUnitGUID) AS unitGUID
				, IIF(eventName LIKE '%HEAL', sourceName, absorbedByUnitName) AS unitName
			FROM events e
			JOIN actors a1 ON (e.sourceGUID = a1.unitGUID AND a1.encounterTime = :startTime)
			JOIN actors a2 ON (e.targetGUID = a2.unitGUID AND a2.encounterTime = :startTime)
			WHERE
				e.timestamp >= :startTime
			AND	e.timestamp <= :endTime
            AND targetName = :targetName
			AND (
					(
						eventName LIKE '%HEAL'
					AND (
							a1.isPlayer = :affiliation
						OR	a1.isPet = :affiliation
						OR	(
								:affiliation = 0
							AND a1.isNPC = 1
							)
					)
					AND a1.encounterTime = :startTime
				) OR (
						absorbed > 0
					AND	(
							a2.isPlayer = :affiliation
						OR	a2.isPet = :affiliation
						OR	(
								:affiliation = 0
							AND a2.isNPC = 1
						)
					)
					AND a2.encounterTime = :startTime
				)
			)
			GROUP BY IIF(eventName LIKE '%HEAL', sourceGUID, absorbedByUnitGUID)
		) x
		LEFT JOIN pets p ON x.unitGUID = p.petGUID
		GROUP BY COALESCE(ownerName, unitName)
	) x
	LEFT JOIN specs s ON x.unitGUID = s.unitGUID
	WHERE s.timestamp = :startTime OR s.timestamp IS NULL
	GROUP BY x.unitName
)
SELECT
   name || IIF(num > 1, ' (' || num || ')', '') AS name
    , PRINTF('%.2f%%', pct) AS pct
    , pct / MAX(pct) OVER() AS relpct
    , PRINTF('%,d', eheal) AS eheal
    , PRINTF('%,d', ehps) AS ehps
    , PRINTF('%,d (%2.2f%%)', overheal, overhealpct) AS overheal
    , PRINTF('%,d', hps) AS hps
    , spec
    , name AS cleanname
FROM calc
UNION ALL
SELECT
    'Total' AS name
    , '-' AS pct
    , NULL AS relpct
    , PRINTF('%,d', SUM(eheal)) AS heal
    , PRINTF('%,d', SUM(ehps)) AS ehps
    , PRINTF('%,d (%2.2f%%)', SUM(overheal), SUM(overheal) * 100.0 / (SUM(eheal + overheal))) AS overheal
    , PRINTF('%,d', SUM(hps)) AS hps
    , NULL AS spec
    , NULL AS cleanname
FROM calc
ORDER BY relpct DESC