import pandas as pd
import nltk
nltk.download('punkt_tab')
nltk.download('stopwords')
from utils import preprocess_text



            
class SwiftEngine:
    def __init__(self,data_file="data/songs_chunked.csv"):
        self.df = pd.read_csv(data_file)
        self.inverse_index = {}
        self.create_index()
    def create_index(self):
        for idx,row in self.df.iterrows():
            lyrics = row["CHUNK"]
            id = str(row["ID"])
            tokens = preprocess_text(lyrics)
            for pos,token in enumerate(tokens):
                if token not in self.inverse_index:
                    self.inverse_index[token] = {}
                if id not in self.inverse_index[token]:
                    self.inverse_index[token][id] = []
                self.inverse_index[token][id].append(pos)
    def search(self,query):
        query_tokens = preprocess_text(query)
        results = {} 
        for token in query_tokens:
            if token in self.inverse_index:
                for id, positions in self.inverse_index[token].items():
                    if id not in results:
                        results[id] = 0  
                    results[id] += len(positions) 

        
        ranked_results = sorted(results.items(), key=lambda item: item[1], reverse=True)

        return ranked_results
    
    def retrieve_lyrics(self,id):
        id = int(id)
        row = self.df.iloc[id]
        
        return row["CHUNK"],row['SONG'],row['ALBUM']

    
    def search_show(self,query):
        results = self.search(query)
        print(f"\n\n\n\nShowcasing results for '{query}'\nFound {len(results)} results.\n")
        for id,occ in results:
            lyrics,title,album = self.retrieve_lyrics(id)
            print(f"{title} - {album}\n---------------------\n{lyrics}\n\n\n")
            
    def search_full(self,query):
        results = self.search(query)
        results_full = []
        for id,occ in results:
            lyrics,title,album = self.retrieve_lyrics(id)
            results_full.append({"lyrics":lyrics,"song":title,"album":album,"occ":occ})
        return results_full
 

