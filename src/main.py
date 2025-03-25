import pandas as pd
import nltk
import re
from nltk.corpus import stopwords
from neo4j import GraphDatabase
from dotenv import load_dotenv
import ollama,json,os
from utils import get_sentence_embeddings,calculate_similarity,rank_segments
nltk.download('stopwords')



            
class SwiftEngineSemantic:
    def __init__(self,env_file="../.env"):
        load_dotenv(env_file)
        self.driver = GraphDatabase.driver(
            os.environ["NEO4J_URI"],
            auth=(os.environ["NEO4J_USERNAME"], os.environ["NEO4J_PASSWORD"])
        )
    def search(self,query,use_llm=True):
        if not use_llm:
            keywords = self.simpleTokenizer(query)
        else:
            keywords = self.llmKeywordExtractor(query)
        if keywords:
            return self.graphKeywordSearch(keywords),keywords
        return [],[]
    
    def semanticSearch(self,query,top=10):
        query_embedding = get_sentence_embeddings([query])[0]
        segments = self.getAllSegments()
        similarity_scores = calculate_similarity(query_embedding, [seg["embedding"] for seg in segments])
        return rank_segments(segments, similarity_scores,top_n=top)
        
    def simpleTokenizer(self,query):
        words = query.lower().split()
        stop_words = set(stopwords.words('english'))
        return [word for word in words if word not in stop_words]
        
    def llmKeywordExtractor(self,query,model_name="deepseek-r1:1.5b"):
        prompt = f"""
            You are an expert keyword extractor. Your task is to analyze the user's query and extract the most relevant keywords.

            User Query: "{query}"

            Instructions:
            1.  Identify the core concepts and entities mentioned in the query.
            2.  Extract the most significant words or phrases that represent these concepts.
            3.  Exclude common words or stop words that do not contribute to the meaning.
            4.  Return the extracted keywords in a JSON format with the key "keywords" and the value as a list of strings.
            5. Don't add nothing more from query, avoid hallucinations
            Example input :
            "Songs that talke about happy memories of someone gone, and love shared."
            Example Output:
            ```json
            {{"keywords":["love", "sadness", "memories","bereft"]}}
            ```
            """

        try:
            json_prompt = f"{prompt}\n\nRespond with JSON format."
            response = ollama.chat(model=model_name, messages=[
                {
                    'role': 'user',
                    'content': json_prompt,
                    
                },
            ],options={"temperature": 0})
            json_match = re.search(r'```json\s*(.*?})\s*```', response['message']['content'], re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(1))["keywords"]
                except json.JSONDecodeError:
                    return None
            else:
                return None
        except Exception as e:
            return json.dumps({"error": f"An error occurred: {e}"})
        
    
    
    def graphKeywordSearch(self,keywords,limit=30):
        with self.driver.session() as session:
            results = []
            for word in keywords:
                # Search in Segment text
                segment_results = session.run("""
                     MATCH (seg:Segment)<-[:CONTAINS]-(song:Song)-[:BELONGS_TO]->(album:Album)
                    WHERE seg.text CONTAINS $word
                    RETURN seg.text, song.title, album.name
                    LIMIT 5
                """, word=word)
                for record in segment_results:
                    results.append({"lyrics":record['seg.text'],"source":"direct","song":record["song.title"],"album":record["album.name"]})

                # Search in Emotion names
                emotion_results = session.run("""
                    MATCH (e:Emotion)-[:EXPRESSES]-(seg:Segment)<-[:CONTAINS]-(song:Song)-[:BELONGS_TO]->(album:Album)
                    WHERE e.name = $word
                    RETURN seg.text, song.title, album.name
                    LIMIT 5
                """, word=word)
                for record in emotion_results:
                    results.append({"lyrics":record['seg.text'],"source":"emotion","song":record["song.title"],"album":record["album.name"]})

                # Search in Theme names
                theme_results = session.run("""
                    MATCH (t:Theme)-[:DEALS_WITH]-(seg:Segment)<-[:CONTAINS]-(song:Song)-[:BELONGS_TO]->(album:Album)
                    WHERE t.name = $word
                    RETURN seg.text, song.title, album.name
                    LIMIT 5
                """, word=word)
                for record in theme_results:
                    results.append({"lyrics":record['seg.text'],"source":"theme","song":record["song.title"],"album":record["album.name"]})
        return results[:min(len(results),limit)]
    
    def getAllSegments(self):
        """Retrieves all lyric segments from Neo4j."""
        with self.driver.session() as session:
            results = session.run(""" MATCH (seg:Segment)<-[:CONTAINS]-(song:Song)-[:BELONGS_TO]->(album:Album)
                    RETURN seg.text,seg.embedding,song.title, album.name""")
            segments = [{"lyrics":record['seg.text'],"source":"semantic","song":record["song.title"],"album":record["album.name"],"embedding":record["seg.embedding"]} for record in results]
            return segments
    
    def display(self,results):
        for res in results:
            print(res)
            print(f"{res["song"]} - {res["album"]}")
            print(f"\n{res["lyrics"]}")
            print(f"\n Source : {res["source"]}")
            print("----------------------------------")
        print(f"Showing {len(results)} result.")


if __name__=="__main__":
    eng = SwiftEngineSemantic()
    res,keywords = eng.search("My lover left me",use_llm=True)
    eng.display(res)