import re
import pandas as pd
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import string
from spellchecker import SpellChecker

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
    
    
def correct_spelling_tokens(tokens): 
    corrected_tokens = []
    spell = SpellChecker()
    for token in tokens:
        if token in spell:
            corrected_tokens.append(token)
        else:
            suggestion = spell.correction(token)
            if suggestion:
                corrected_tokens.append(suggestion)
            else:
                corrected_tokens.append(token)
    return corrected_tokens

ALBUM_EMOJI = {"The Tortured Poets Department":"🪶","1989 (Taylor's Version)":"🌊","Taylor Swift":"📗","Fearless (Taylor's Version)":"💛","Speak Now (Taylor's Version)":"📔","Red (Taylor's Version)":"🧣","reputation":"🐍","Lover":"💕","folklore":"🪩","evermore":"🍂","Midnights":'🌌','The Taylor Swift Holiday Collection':'🎎','The Hunger Games':'🏹',"How Long Do You Think It's Gonna Last":'🪕',
               "Cats":"🐈","Where The Crawdads Sing":"⛵","Christmas Tree Farm":"🎄","Fifty Shades Darker":"🖤","Miss Americana":"👑","Love Drunk":"💌","Women in Music Part III":"👩","Two Lanes of Freedom":"🛣️","Bad Blood (Remix) (Taylor's Version)":"🩸","The Hannah Montana Movie":"🎸"
               ,"Beautiful Eyes":"👀"}

#SEMANTIC
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

def get_sentence_embeddings(sentences, model_name='all-mpnet-base-v2'):
    """Generates sentence embeddings using sentence transformers."""
    model = SentenceTransformer(model_name)
    embeddings = model.encode(sentences)
    return embeddings

def calculate_similarity(query_embedding, segment_embeddings):
    """Calculates cosine similarity between the query and segment embeddings."""
    similarity_scores = cosine_similarity([query_embedding], segment_embeddings)[0]
    return similarity_scores

def rank_segments(segments, similarity_scores, top_n=10):
    """Ranks segments based on similarity scores and returns the top results."""
    ranked_segments = list(zip(segments, similarity_scores))
    ranked_segments.sort(key=lambda item: item[1], reverse=True)
    return [x[0] for x in ranked_segments[:top_n]]