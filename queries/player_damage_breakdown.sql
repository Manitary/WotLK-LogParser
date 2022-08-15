SELECT ed.spellName, ed.dmg, ed.hit, 
PRINTF('%2.2f%%', ed.crit*100.00/ed.hit) AS crit, 
em.miss, ed.resist AS resisted, ed.blck AS blocked, ed.absorb AS absorbed
FROM
    (
        SELECT spellName, spellID, SUM(amount) AS dmg, COUNT(amount) AS hit, SUM(absorbed) AS absorb, SUM(resisted) AS resist, SUM(blocked) AS blck, SUM(critical) AS crit
        FROM events
        WHERE timestamp >= :startTime AND timestamp <= :endTime
        AND sourceName = :sourceName
        AND (eventName LIKE '%DAMAGE%' OR eventName LIKE '%MISSED')
        AND spellName IS NOT NULL 
        GROUP BY spellID
        ORDER BY dmg DESC
    ) ed
LEFT JOIN
    (
        SELECT spellName, spellID, COUNT(spellID) AS miss
        FROM events
        WHERE timestamp >= :startTime AND timestamp <= :endTime
        AND sourceName = :sourceName
        AND eventName LIKE '%MISSED'
        AND spellName IS NOT NULL 
        GROUP BY spellID
    ) em
ON ed.spellID = em.spellID