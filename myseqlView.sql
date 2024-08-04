CREATE VIEW sorted_faculty_names AS
SELECT name
FROM faculty
WHERE name IS NOT NULL AND name <> ""
ORDER BY name ASC;
