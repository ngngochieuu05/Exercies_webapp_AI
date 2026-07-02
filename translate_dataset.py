import json
import time
import os
import sys
import subprocess
import requests

dataset_path = "D:/Python/project/App_The_Thao/model/exercises.json"
backend_json_path = "D:/Python/project/App_The_Thao/backend/data/exercises.json"
db_path = "D:/Python/project/App_The_Thao/backend/exercises.db"

def load_dataset():
    with open(dataset_path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_dataset(data):
    # Save to model/exercises.json
    with open(dataset_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    # Copy to backend/data/exercises.json
    os.makedirs(os.path.dirname(backend_json_path), exist_ok=True)
    with open(backend_json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def translate_texts_fast(texts):
    if not texts:
        return []
    
    chunks = []
    current_chunk = []
    current_length = 0
    
    for text in texts:
        clean_text = text.replace("\n", " ").strip()
        text_len = len(clean_text)
        if current_length + text_len + 5 > 3000:
            chunks.append(current_chunk)
            current_chunk = [clean_text]
            current_length = text_len
        else:
            current_chunk.append(clean_text)
            current_length += text_len + 5
            
    if current_chunk:
        chunks.append(current_chunk)
        
    translated_texts = []
    url = "https://translate.googleapis.com/translate_a/single"
    
    for chunk in chunks:
        joined_text = "\n***\n".join(chunk)
        success = False
        delay = 2
        
        for attempt in range(5):
            try:
                params = {
                    "client": "gtx",
                    "sl": "en",
                    "tl": "vi",
                    "dt": "t",
                    "q": joined_text
                }
                res = requests.get(url, params=params, timeout=4.0)
                if res.status_code == 200:
                    parts = res.json()[0]
                    translated_joined = "".join([part[0] for part in parts if part and part[0]])
                    
                    parts_split = [p.strip() for p in translated_joined.split("***")]
                    if len(parts_split) == len(chunk):
                        translated_texts.extend(parts_split)
                        success = True
                        break
                    else:
                        print(f"Warning: split count mismatch ({len(parts_split)} vs {len(chunk)}). Attempting translation fallback...", flush=True)
                else:
                    print(f"Error status code {res.status_code}. Retrying...", flush=True)
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...", flush=True)
                
            time.sleep(delay)
            delay *= 2
                
        if not success:
            # Individual fallback for this chunk if batching fails completely
            print("Batch translation failed completely. Translating chunk items individually...", flush=True)
            for item in chunk:
                item_success = False
                item_delay = 1
                for item_attempt in range(3):
                    try:
                        res = requests.get(url, params={"client": "gtx", "sl": "en", "tl": "vi", "dt": "t", "q": item}, timeout=3.0)
                        if res.status_code == 200:
                            translated = res.json()[0][0][0]
                            translated_texts.append(translated.strip())
                            item_success = True
                            break
                    except Exception:
                        pass
                    time.sleep(item_delay)
                    item_delay *= 2
                if not item_success:
                    translated_texts.append("") # Keep placeholder if translation fails
            time.sleep(0.5)
        else:
            time.sleep(0.5)
        
    return translated_texts

def main():
    print("Loading dataset...", flush=True)
    data = load_dataset()
    total = len(data)
    print(f"Total exercises: {total}", flush=True)

    # 1. Identify missing translations
    missing_exercises = []
    for idx, ex in enumerate(data):
        has_instructions_vi = "vi" in ex.get("instructions", {})
        has_steps_vi = "vi" in ex.get("instruction_steps", {})
        
        # Check if vi instructions exists and is not empty
        if has_instructions_vi and ex["instructions"]["vi"]:
            if has_steps_vi and ex["instruction_steps"]["vi"] and all(ex["instruction_steps"]["vi"]):
                continue
                
        missing_exercises.append((idx, ex))

    print(f"Exercises needing translation: {len(missing_exercises)}", flush=True)
    if not missing_exercises:
        print("All exercises are already translated to Vietnamese!", flush=True)
    else:
        # We will process in batches of 40 exercises to make it fast
        BATCH_SIZE = 40
        
        for i in range(0, len(missing_exercises), BATCH_SIZE):
            batch = missing_exercises[i : i + BATCH_SIZE]
            print(f"\nProcessing batch {i // BATCH_SIZE + 1} ({i} to {i + len(batch)} of {len(missing_exercises)})...", flush=True)
            
            texts_to_translate = []
            mapping = []
            
            for idx, ex in batch:
                if "vi" not in ex.get("instructions", {}) or not ex["instructions"]["vi"]:
                    en_text = ex["instructions"].get("en", "")
                    if en_text:
                        texts_to_translate.append(en_text)
                        mapping.append((idx, "instruction", None))
                
                if "vi" not in ex.get("instruction_steps", {}) or not ex["instruction_steps"]["vi"] or not all(ex["instruction_steps"]["vi"]):
                    en_steps = ex["instruction_steps"].get("en", [])
                    for s_idx, step in enumerate(en_steps):
                        if step:
                            texts_to_translate.append(step)
                            mapping.append((idx, "step", s_idx))

            if not texts_to_translate:
                continue

            print(f"Translating {len(texts_to_translate)} items...", flush=True)
            
            try:
                translated_texts = translate_texts_fast(texts_to_translate)
            except Exception as e:
                print(f"Fatal translation error: {e}. Exiting to save progress.", flush=True)
                break

            # Merge translations back into data
            for translated, (idx, field_type, s_idx) in zip(translated_texts, mapping):
                ex = data[idx]
                if field_type == "instruction":
                    if "instructions" not in ex:
                        ex["instructions"] = {}
                    ex["instructions"]["vi"] = translated
                elif field_type == "step":
                    if "instruction_steps" not in ex:
                        ex["instruction_steps"] = {}
                    if "vi" not in ex["instruction_steps"] or not ex["instruction_steps"]["vi"]:
                        en_len = len(ex["instruction_steps"].get("en", []))
                        ex["instruction_steps"]["vi"] = [""] * en_len
                    
                    if s_idx < len(ex["instruction_steps"]["vi"]):
                        ex["instruction_steps"]["vi"][s_idx] = translated

            # Save progress checkpoint
            save_dataset(data)
            print(f"Checkpoint saved. Progress: {i + len(batch)}/{len(missing_exercises)} exercises processed.", flush=True)
            time.sleep(1)

    print("\nTranslation session finished!", flush=True)
    
    # 2. Database Rebuild Step
    print("\nRebuilding SQLite database with new translations...", flush=True)
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print(f"Deleted old database at {db_path}", flush=True)
        except Exception as e:
            print(f"Error deleting database: {e}. If the backend is running, it might lock it.", flush=True)
    
    try:
        res = subprocess.run([sys.executable, "D:/Python/project/App_The_Thao/backend/database.py"], capture_output=True, text=True)
        print(res.stdout, flush=True)
        print(res.stderr, flush=True)
        print("Database rebuild complete!", flush=True)
    except Exception as e:
        print(f"Error running database rebuild script: {e}", flush=True)

if __name__ == "__main__":
    main()
