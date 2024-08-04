SELECT f.name AS professor, COUNT(DISTINCT fp.publication_Id) AS num_publications
FROM faculty f, university u, faculty_publication fp
WHERE f.university_id = u.id AND f.id = fp.faculty_Id AND u.name = 'University of Illinois at Urbana Champaign'
GROUP BY f.id
ORDER BY num_publications DESC
LIMIT 10;

SELECT p.title
FROM faculty f, publication p, faculty_publication fp
WHERE f.name = "Jim Martin" AND f.id = fp.faculty_Id AND p.ID = fp.publication_Id;

SELECT f.name AS professor, SUM(p.num_citations) AS num_citations
FROM faculty f, university u, publication p, faculty_publication fp
WHERE f.university_id = u.id AND f.id = fp.faculty_Id AND p.ID = fp.publication_ID AND u.name = 'University of illinois at Urbana Champaign'
GROUP BY f.id
ORDER BY num_citations DESC
LIMIT 10;
