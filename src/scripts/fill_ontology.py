from dotenv import load_dotenv
import os
from neo4j import GraphDatabase
import logging
import pandas as pd
from tqdm import tqdm


def create_populate_ontology(csv_file="../../data/songs_full.csv",env_file="../../.env"):
    
    load_dotenv(env_file)
    logging.info("Environement variables for Neo4j Access codes is loaded")
    driver = GraphDatabase.driver(
        os.environ["NEO4J_URI"],
        auth=(os.environ["NEO4J_USERNAME"], os.environ["NEO4J_PASSWORD"])
    )
    print("LOG : Driver connected to database")
    
    df = pd.read_csv(csv_file)
    
    with driver.session() as session:
        for idx, row in tqdm(df.iterrows(),total=df.shape[0]):
            title = row["SONG"]
            album_name = row["ALBUM"]
            segment_text = row["CHUNK"]
            emotions = row["EMOTIONS"].split(", ") if pd.notna(row["EMOTIONS"]) else []
            themes = row["THEMES"].split(", ") if pd.notna(row["THEMES"]) else []

            # Create Song Node
            session.run("MERGE (s:Song {title: $title})", title=title)

            # Create Album Node
            session.run("MERGE (a:Album {name: $album_name})", album_name=album_name)

            # Create Segment Node
            session.run("MERGE (seg:Segment {text: $segment_text, id: $segment_id})", segment_text=segment_text, segment_id=f"{title}_segment_{row['CHUNK_ID']}")

            # Create Relationships
            session.run("MATCH (s:Song {title: $title}), (a:Album {name: $album_name}) MERGE (s)-[:BELONGS_TO]->(a)", title=title, album_name=album_name)
            session.run("MATCH (s:Song {title: $title}), (seg:Segment {id: $segment_id}) MERGE (s)-[:CONTAINS]->(seg)", title=title, segment_id=f"{title}_segment_{row['CHUNK_ID']}")

            # Create Emotion Nodes and Relationships
            for emotion_name in emotions:
                if emotion_name.strip():
                    emotion_name_stripped = emotion_name.strip()
                    session.run("MERGE (e:Emotion {name: $emotion_name})", emotion_name=emotion_name_stripped)
                    session.run("MATCH (seg:Segment {id: $segment_id}), (e:Emotion {name: $emotion_name}) MERGE (seg)-[:EXPRESSES]->(e)", segment_id=f"{title}_segment_{row['CHUNK_ID']}", emotion_name=emotion_name_stripped)

            # Create Theme Nodes and Relationships
            for theme_name in themes:
                if theme_name.strip():
                    theme_name_stripped = theme_name.strip()
                    session.run("MERGE (t:Theme {name: $theme_name})", theme_name=theme_name_stripped)
                    session.run("MATCH (seg:Segment {id: $segment_id}), (t:Theme {name: $theme_name}) MERGE (seg)-[:DEALS_WITH]->(t)", segment_id=f"{title}_segment_{row['CHUNK_ID']}", theme_name=theme_name_stripped)
    
if __name__=="__main__":
    create_populate_ontology()