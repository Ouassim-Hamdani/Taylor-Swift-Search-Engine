import pandas as pd
import ollama,re
import json
from tqdm import tqdm
def llm_call(lyrics,prompt=None,model_name="deepseek-r1:1.5b"):
    if prompt is None:
        prompt = f"""
            Analyze the following lyrics and provide the emotions and themes as JSON:
            Emotion text should be simple liek "happy" "sad" "bereft" "Nostalgia" not complciated phrase
            Themes text should be simple word/phrase, not too long
            Lyrics: 
            {lyrics}
            JSON format:
            {{
            "emotions": ["Emotion1", "Emotion2"],
            "themes": ["Theme1", "Theme2"]
            }}
        """
    try:
        json_prompt = f"{prompt}\n\nRespond with JSON format."
        response = ollama.chat(model=model_name, messages=[
            {
                'role': 'user',
                'content': json_prompt,
                
            },
        ],options={"temperature": 0})
        return response['message']['content']
    except ollama.exceptions.ModelNotFoundError:
        return json.dumps({"error": f"Model '{model_name}' not found. Please pull the model using 'ollama pull {model_name}'."})
    except Exception as e:
        return json.dumps({"error": f"An error occurred: {e}"})


def extract_json_from_text(text):
    """Extracts JSON code from a text, used to get JSON from llm output, as it is unstructured"""
    json_match = re.search(r'```json\s*({.*?})\s*```', text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            return None
    else:
        return None

def extract_emotion_theme(text):
    try:
        resp = llm_call(text)
        json_resp = extract_json_from_text(resp)
        if json_resp:
            return json_resp["emotions"],json_resp["themes"]
        return [],[]    
    except:
        return [],[]

def generate_emotions_themes_from_df(input_file="../../data/songs_chunked.csv",output_file="../../data/songs_full.csv"):
    df = pd.read_csv(input_file)
    df["EMOTIONS"] = None
    df["THEMES"] = None
    idxs = []
    
    for idx,row in tqdm(df.iterrows(),total=df.shape[0]):
        
        emotions, themes = extract_emotion_theme(row["CHUNK"])
        
        try:
            if emotions:
                df.loc[idx, "EMOTIONS"] = ", ".join(emotions)
            else:
                df.loc[idx, "EMOTIONS"] = pd.NA
            if themes:
                df.loc[idx, "THEMES"] = ", ".join(themes)
            else:
                df.loc[idx, "THEMES"] = pd.NA
        except:
            df.loc[idx, "THEMES"] = pd.NA
            df.loc[idx, "EMOTIONS"] = pd.NA
            
        try:
            if pd.isna(df.loc[idx, "EMOTIONS"]) or pd.isna(df.loc[idx, "THEMES"]==pd.NA):
                idxs.append(idx)
        except Exception as e:
            print("I nknow this should be impossible, but hey i'm running a 3000 llM INERERENCE IT TAKES 3 HOURS SO IM SORRY IF IM BEING CAUTIOUS SPECIALLY AFTER IT RAN FOR 2 HOURS AND CRAHSED")
            print(e)
    df.to_csv(output_file, index=False)
    print(idxs)
if __name__=="__main__":
    generate_emotions_themes_from_df()
