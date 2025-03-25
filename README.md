# Taylor Swift Lyrics Search Engine  (𝑻𝒂𝒚𝒍𝒐𝒓’𝒔 𝑽𝒆𝒓𝒔𝒊𝒐𝒏)  🧣🍂

This project implements a semantic search engine based on ontologies, and using an LLM, for Taylor Swift lyrics. It allows users to search for lyrics and view the matching songs, albums, and lyrics snippets, academic project.
Accessible at https://taylor-swift.streamlit.app/
## Features

* **Lyrics Search:** Swift up the lyrics using keywords.
* **Results Display:** Displays matching songs, albums, and relevant lyrics snippets.
* **Streamlit UI:** Easy-to-use web interface built with Streamlit.
* **Efficient Indexing:** Uses an inverted index for fast search lookups.
* **Data Preprocessing:** Includes data cleaning and preprocessing steps.

## Installation

### 1. Clone the repository:

```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/taylor-swift-lyrics-search.git  # Replace with your repo URL
cd taylor-swift-lyrics-search
```


### 2. Install dependencies:

```bash
pip install -r requirements.txt
```
or if you have `make` installed
```bash
make install
```


## How to run:



```bash
streamlit run src/app.py
```
or if you have `make` insatlled
```bash
make run
```

This will open the app in your web browser.

## STEPS 
- Using Deepseek r1 ollama, we run for 3 hours a process that extract emotions, themes from a chunk of lyrics, to add that to our database


## File Structure

```
taylor-swift-search-engine/
├── src/                  # Source Code files
│   ├── app.py            # Streamlit app
│   ├── main.py           # Search engine logic (SwiftEngine class)
│   └── utils.py          # Utility functions (data preprocessing, chunking, clean_df)
├── data/                 # Data files
│   ├── songs.csv         # Original songs data (input)
│   └── songs_chunked.csv # Processed data (used by the search engine)
├── requirements.txt      # Project dependencies
├── README.md             # This file
└── Makefile              # Makefile for easy commands
```

## Makefile

The included `Makefile` provides convenient commands:

- `make run`: Runs the Streamlit app.
- `make install`: Installs the required Python packages.

## Dependencies

Ensure you have the following Python libraries installed:

- **Streamlit**
- **Pandas**
- **NLTK** (including `punkt` and `stopwords` data)
- **Pydantic**
- **Regular Expression library (re)**

## Example `songs.csv` format:

```csv
Title,Album,Lyrics
"Shake It Off","1989","This sick beat..."
"Blank Space","1989","Darling, I'm a nightmare dressed as a daydream..."
# ... more songs
```

---

Enjoy searching through Taylor Swift's lyrics effortlessly like an Anti-Hero from a fellow Swifite! 🎵✨



15k relations,6k nodes