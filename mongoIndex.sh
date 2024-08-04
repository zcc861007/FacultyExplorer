# Connect to your MongoDB instance
mongosh

# Use the database
use academicworld

# Create an index on the 'year' field
db.publications.createIndex({ year: 1 })

# Create an index on the 'keywords.name' field
db.publications.createIndex({ "keywords.name": 1 })
