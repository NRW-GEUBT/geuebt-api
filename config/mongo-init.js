// Create root user
db.getSiblingDB('admin').auth(process.env.MONGO_INITDB_ROOT_USERNAME, process.env.MONGO_INITDB_ROOT_PASSWORD)

// Create API user
db = db.getSiblingDB(process.env.MONGO_INITDB_DATABASE)
db.createUser({
    user: process.env.MONGODB_USERNAME,
    pwd: process.env.MONGODB_PASSWORD,
    roles: [
      {
        role: 'readWrite',
        db: process.env.MONGO_INITDB_DATABASE
      }
    ]
  });

//   Setting up collections and indexing
db.createCollection("isolates")
db.isolates.createIndex({"isolate_id"})

db.createCollection("clusters")
db.isolates.createIndex({"cluster_id"})

db.createCollection("runs")
db.isolates.createIndex({"run_metadata.run_name"})

db.createCollection("sequences")
db.isolates.createIndex({"isolate_id"})
