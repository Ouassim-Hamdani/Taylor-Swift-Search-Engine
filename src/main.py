import pandas as pd
import nltk
nltk.download('punkt_tab')
nltk.download('stopwords')
from utils import preprocess_text,correct_spelling_tokens



            
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
    def search(self,query,correcter=True):
        query_tokens = preprocess_text(query)
        if correcter:
            query_tokens = correct_spelling_tokens(query_tokens)
        results = {}
        for token in query_tokens:
            if token in self.inverse_index:
                for id, positions in self.inverse_index[token].items():
                    if id not in results:
                        results[id] = 0  
                    results[id] += len(positions) 

        print(results)
        ranked_results = sorted(results.items(), key=lambda item: item[1], reverse=True)
        print(ranked_results)
        return ranked_results,query_tokens
    
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
            
    def search_full(self,query,phrase=False,correcter=False):
        if phrase:
            results,query_tokens = self.search_phrase(query,correcter)
            if results is None: # cauuse nto possible, phrase too short
                return None,query_tokens
        else:
            results,query_tokens = self.search(query,correcter)
        results_full = []
        for id,occ in results:
            lyrics,title,album = self.retrieve_lyrics(id)
            results_full.append({"lyrics":lyrics,"song":title,"album":album,"occ":occ})
        return results_full,query_tokens
    
    def search_phrase(self,query,correcter=True):
        query_tokens = preprocess_text(query)
        if correcter:
            query_tokens = correct_spelling_tokens(query_tokens)
        results = {}
        if len(query_tokens) <2:
            return None,query_tokens
        
        if query_tokens[0] not in self.inverse_index:
            return [],query_tokens #if start of phrase ulac, then empty
        
        for idx_1,pos1 in self.inverse_index[query_tokens[0]].items(): #exploring documents of first word dictionary
            if idx_1 not in results:
              results[idx_1] = 0
            for pos1_i in pos1:
                valid_phrase = True
                for i in range(1, len(query_tokens)):
                    next_token = query_tokens[i]
                    if next_token not in self.inverse_index: #next word not present at all.
                        valid_phrase = False
                        break

                    found_next = False # now we know its present, but is it right after first word in doc of idx1, we compare their positions
                    if idx_1 in self.inverse_index[next_token]: #if doc of first word present here too
                        for pos2 in self.inverse_index[next_token][idx_1]: # its opresent we compare positions
                            if pos2 == pos1_i + i:  # Check for consecutive positions
                                found_next = True
                                break
                    if not found_next:
                        valid_phrase = False
                        break

                if valid_phrase:
                    results[idx_1] += 1  
            if results[idx_1]==0: #side bug forget to remove documents that have 0 occ
                del results[idx_1]
        ranked_results = sorted(results.items(), key=lambda item: item[1], reverse=True)
        return ranked_results,query_tokens
    

