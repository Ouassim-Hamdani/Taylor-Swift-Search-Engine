import streamlit as st
from main import SwiftEngine
from utils import preprocess_text
import re
def highlight_query_in_lyrics(lyrics, query):
    """Highlights the query terms in the lyrics snippet."""
    query_tokens = preprocess_text(query)  
    snippet = ""
    for token in query_tokens:
        lyrics = re.sub(r"\b" + re.escape(token) + r"\b", r"**\g**", lyrics, flags=re.IGNORECASE)
    return lyrics

@st.cache_resource
def load_engine():
    """Cached function to load engine search ONCE at startup"""
    engine = SwiftEngine()
    return engine

engine = load_engine()

st.title("Taylor Swift Lyrics Search")

query = st.text_input("Enter your search query:")

if query:
    with st.spinner("Searching..."):
        results = engine.search_full(query)
        if results:
            st.write(f"Found {len(results)} results:")
            for result in results:

               
                #highlighted_snippet = highlight_query_in_lyrics(result["lyrics"], query)

                st.markdown(f"### {result["song"]} - {result["album"]} 🧣") 
                st.markdown(result["lyrics"].replace("\n","\n\n")) 
                st.write(f"Relevance: {result["occ"]}")
                st.write("---")  

        else:
            st.write("No results found.")


