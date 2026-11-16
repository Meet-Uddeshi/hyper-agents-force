// Hyper Agents Force - Codebase Knowledge Graph (Cypher Export)
// Execute in Neo4j Browser or cypher-shell (Zero environment configuration required)

// Constraints & Indices
CREATE CONSTRAINT IF NOT EXISTS FOR (n:CodeNode) REQUIRE n.node_id IS UNIQUE;

MERGE (n:File {node_id: "file:main.py"}) SET n.name = "main.py", n.file_path = "main.py", n.start_line = 1, n.language = "python";
MERGE (n:Class {node_id: "file:main.py#Core"}) SET n.name = "Core", n.file_path = "main.py", n.start_line = 1, n.language = "python";

// Relationships
MATCH (s {node_id: "file:main.py"}), (t {node_id: "file:main.py#Core"}) MERGE (s)-[:DEFINES {context: "class definition"}]->(t);