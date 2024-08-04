CALL db.labels()
CALL db.relationshipTypes()
CALL db.propertyKeys()


MATCH (f:FACULTY)-[:INTERESTED_IN]->(k:KEYWORD)
RETURN k.name AS k_name, count(f.name) AS f_count
ORDER BY f_count DESC
LIMIT 10


// List all node labels
CALL db.labels()

// List all relationship types
CALL db.relationshipTypes()

// List properties for FACULTY nodes
MATCH (n:FACULTY)
RETURN keys(n) AS properties LIMIT 1

// List properties for KEYWORD nodes
MATCH (n:KEYWORD)
RETURN keys(n) AS properties LIMIT 1

// List properties for INSTITUTE nodes
MATCH (n:INSTITUTE)
RETURN keys(n) AS properties LIMIT 1

// List properties for PUBLICATION nodes
MATCH (n:PUBLICATION)
RETURN keys(n) AS properties LIMIT 1

// Fetch sample FACULTY nodes
MATCH (n:FACULTY)
RETURN n LIMIT 5

// Fetch sample KEYWORD nodes
MATCH (n:KEYWORD)
RETURN n LIMIT 5

// Fetch sample INSTITUTE nodes
MATCH (n:INSTITUTE)
RETURN n LIMIT 5

// Fetch sample PUBLICATION nodes
MATCH (n:PUBLICATION)
RETURN n LIMIT 5

// Fetch sample relationships
MATCH (n:FACULTY)-[r]->(m)
RETURN n, r, m LIMIT 5
