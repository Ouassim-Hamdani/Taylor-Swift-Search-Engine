import streamlit as st
from main import SwiftEngineSemantic
from utils import preprocess_text,ALBUM_EMOJI
import re
st.set_page_config(page_title="Taylor Swift Lyrics Search", page_icon="🧣", layout="wide") 


@st.cache_resource
def load_engine():
    """Cached function to load engine search ONCE at startup"""
    engine = SwiftEngineSemantic(".env")
    return engine

engine = load_engine()


col1, col2,col3 = st.columns([1,5, 1])  

with col2: 
    st.title("Taylor Swift Lyrics Search (𝑻𝒂𝒚𝒍𝒐𝒓’𝒔 𝑽𝒆𝒓𝒔𝒊𝒐𝒏) 🧣") 
    with st.container():
        col_input1,col_input2= st.columns([5,1])
        with col_input1:
            query = st.text_input("Type In the Lyrics:", placeholder="e.g., 'red scarf' or 'All Too Well'", key="search_input",label_visibility='hidden')
        with col_input2:
            st.container(height=12,border=0)
            search_button = st.button("🔎")
    search_type = st.radio("Search Type:", ("Ontology", "Ontology LLM","Semantic"), horizontal=True) 
    

if query or search_button :
    with st.spinner("Searching..."):
        if search_type!="Semantic":
            results, query_tokens = engine.search(query,use_llm= search_type=="Ontology LLM")
        else:
            results = engine.semanticSearch(query)
            query_tokens = None
        with col2:
            if query_tokens:
                st.write(f"Searching for: {', '.join(query_tokens)}")
            if results:
                st.write(f"Found {len(results)} results:")
                for idx,result in enumerate(results):
                    st.markdown(f"### {result['song']} - {result['album']} {ALBUM_EMOJI[result["album"]]}")
                    st.markdown(result["lyrics"].replace("\n", "\n\n"))
                    #st.write(f"Relevance: {result['occ']}")
                    if idx!=len(results)-1:
                        st.write("---")
            else:
                    st.info("No results found. Try a different search., if you're using LLM it can be taht model couldn't capture keywords try again")


else:
    with col2:
        st.info("Press Enter or the search button to see results.")
with col2:
    st.markdown("---")
    st.markdown("Made with ❤️ by Ouassim.")


