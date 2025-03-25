import pandas as pd
from owlready2 import *

def create_populate_ontology(onto_file="../../data/taylorswift_ontology.owl", csv_file="../../data/songs_full.csv",output_onto="../../data/ts_onto_full.owl"):
    """Populates the ontology with data from a CSV file."""
    df = pd.read_csv(csv_file)
    
    # Creating TEMPALTE
    onto = get_ontology("temp.owl")
    with onto:
        # Classes
        class Song(Thing): pass
        class Album(Thing): pass
        class Segment(Thing): pass
        class Emotion(Thing): pass
        class Theme(Thing): pass

        # Relations
        class belongsTo(Song >> Album): pass
        class contains(Song >> Segment): pass
        class expresses(Segment >> Emotion): pass
        class dealsWith(Segment >> Theme): pass

        # Attributes
        class title(Song >> str): pass
        class albumName(Album >> str): pass
        class lyrics(Segment >> str): pass
        class emotionName(Emotion >> str): pass 
        class themeName(Theme >> str): pass 
    
    # POPULATING
    
    with onto:
        song_instances = {}
        album_instances = {}
        emotion_instances = {}  
        theme_instances = {}    
        Song = onto.Song
        Album = onto.Album
        Segment = onto.Segment
        Emotion = onto.Emotion
        Theme = onto.Theme
        for idx, row in df.iterrows():
            title = row["SONG"]
            album_name = row["ALBUM"]
            segment_text = row["CHUNK"]
            emotions = row["EMOTIONS"].split(", ") if pd.notna(row["EMOTIONS"]) else []
            themes = row["THEMES"].split(", ") if pd.notna(row["THEMES"]) else []

            # Song
            if title not in song_instances:
                song_instance = Song(title)
                song_instance.title.append(title)
                song_instances[title] = song_instance
            else:
                song_instance = song_instances[title]

            # Album
            if album_name not in album_instances:
                album_instance = Album(album_name)
                album_instance.albumName.append(album_name)
                album_instances[album_name] = album_instance
            else:
                album_instance = album_instances[album_name]

            # Create SegmentParoles instance
            segment_instance = Segment(f"{title}_segment_{row["CHUNK_ID"]}")
            segment_instance.lyrics.append(segment_text)

            # Links
            song_instance.belongsTo.append(album_instance)
            song_instance.contains.append(segment_instance)

            # Create Emotion instances and link to Segment
            for emotion_name in emotions:
                if emotion_name.strip():
                    emotion_name_stripped = emotion_name.strip()
                    if emotion_name_stripped not in emotion_instances:
                        emotion_instance = Emotion(emotion_name_stripped)
                        emotion_instance.emotionName.append(emotion_name_stripped)
                        emotion_instances[emotion_name_stripped] = emotion_instance
                    else:
                        emotion_instance = emotion_instances[emotion_name_stripped]
                    segment_instance.expresses.append(emotion_instance)

            # Create Theme instances and link to Segment
            for theme_name in themes:
                if theme_name.strip():
                    theme_name_stripped = theme_name.strip()
                    if theme_name_stripped not in theme_instances:
                        theme_instance = Theme(theme_name_stripped)
                        theme_instance.themeName.append(theme_name_stripped)
                        theme_instances[theme_name_stripped] = theme_instance
                    else:
                        theme_instance = theme_instances[theme_name_stripped]
                    segment_instance.dealsWith.append(theme_instance)
    onto.save(output_onto)


if __name__=="__main__":
    create_populate_ontology()