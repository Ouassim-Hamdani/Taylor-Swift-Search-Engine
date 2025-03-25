from neo4j import GraphDatabase
import os
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
from dotenv import load_dotenv
def add_segment_embeddings(env_file="../../.env",embedding_model_name='all-mpnet-base-v2'):
    """Adds embeddings to existing Segment nodes in Neo4j."""
    load_dotenv(env_file)
    driver = GraphDatabase.driver(
        os.environ["NEO4J_URI"],
        auth=(os.environ["NEO4J_USERNAME"], os.environ["NEO4J_PASSWORD"])
    )
    model = SentenceTransformer(embedding_model_name)

    with driver.session() as session:
        # Retrieve all Segment nodes without embeddings
        results = session.run("""
            MATCH (seg:Segment)
            RETURN seg.text, seg.id
        """)

        for record in tqdm(results):
            segment_text = record["seg.text"]
            segment_id = record["seg.id"]

            # Generate Embedding
            embedding = model.encode([segment_text])[0].tolist()

            # Update Segment node with embedding
            session.run("""
                MATCH (seg:Segment {id: $segment_id})
                SET seg.embedding = $embedding
            """, segment_id=segment_id, embedding=embedding)
            print(f"Added embedding to segment: {segment_id}")

add_segment_embeddings()