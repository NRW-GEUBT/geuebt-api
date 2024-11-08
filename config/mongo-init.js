print("Starting mongo-init");

// Create root user
db.getSiblingDB('admin').auth(process.env.MONGO_INITDB_ROOT_USERNAME, process.env.MONGO_INITDB_ROOT_PASSWORD)

// Create API user
print("Creating default user");
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
print("Indexing database");
db.createCollection("isolates")
db.isolates.createIndex({"isolate_id": 1})

db.createCollection("clusters")
db.isolates.createIndex({"cluster_id": 1})

db.createCollection("runs")
db.isolates.createIndex({"run_metadata.run_name": 1})

db.createCollection("sequences")
db.isolates.createIndex({"isolate_id": 1})

print("mongo-init done");