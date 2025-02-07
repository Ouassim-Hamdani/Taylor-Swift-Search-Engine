import re
import pandas as pd
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import string

def clean_lyrics(lyrics):
    cleaned_lyrics = re.sub(r"\[.*?\]", "", lyrics)
    return cleaned_lyrics.strip()   

def clean_df(filename="data/songs.csv"):   
    df = pd.read_csv("data/songs.csv")
    df["cleaned_lyrics"] = df["Lyrics"].apply(clean_lyrics)
    df.to_csv(filename,index=False)

def preprocess_text(text):
        text = text.lower() # Lowering 
        text = text.translate(str.maketrans('', '', string.punctuation)) # removing penctuation
        tokens = word_tokenize(text) # tokenizein text, returniing list of words, can do it classically with split

        stop_words = set(stopwords.words('english'))  # instance of stop words (useless words in english), to ignore
        tokens = [w for w in tokens if w not in stop_words]  #doing what i said above

        stemmer = PorterStemmer() #stemmer from nltk tool used to turn words from running to run, (getting root), i beilive its optional but why not
        tokens = [stemmer.stem(w) for w in tokens] # apllying what i just said
        return tokens
    
def chunk_lyrics(lyrics, chunk_size=4):
    lines = lyrics.splitlines()
    chunks = []
    current_chunk = []

    for line in lines:
        cleaned_line = line.strip()  
        if cleaned_line:  
            current_chunk.append(line)  
            if len(current_chunk) >= chunk_size:
                chunks.append("\n".join(current_chunk))
                current_chunk = []

    if current_chunk: 
        chunks.append("\n".join(current_chunk))

    return chunks
    
def create_pd_chunked(filename='data/songs.csv',output="data/songs_chunked.csv"):
    df = pd.read_csv(filename)
    new_rows = []
    row_id = 0
    for  idx,row in df.iterrows():
        chunks = chunk_lyrics(row["cleaned_lyrics"])
        title = row['Title']
        album = row['Album']
        for idx_c,chunk in enumerate(chunks):
            new_row = {"ID":row_id,"SONG":title,"ALBUM":album,"CHUNK_ID":idx_c,"CHUNK":chunk}
            new_rows.append(new_row)
            row_id+=1
    
    df_out = pd.DataFrame(new_rows)
    
    df_out.to_csv(output,index=False)
    
    
def create_df():
    clean_df()
    create_pd_chunked()