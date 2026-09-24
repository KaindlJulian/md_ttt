import os
import json
import pandas as pd
from tqdm import tqdm

CARD_DIR = "en/" # https://github.com/db-ygoresources-com/yugioh-card-history , card db as per konami 
JSON_PATH = "cardinfo_full.json"  # https://www.ygoprodeck.com/api-guide/ , v7 ygoprodeck api json dump, specifically for findind passcode and border info
PARQUET_PATH = "m.parquet"

# cache card dir
if os.path.exists(PARQUET_PATH):
    df = pd.read_parquet(PARQUET_PATH, engine="pyarrow")
else:
    monsters = []
    files = [
        f for f in os.listdir(CARD_DIR)
        if f.endswith(".json")
    ]
    for file in tqdm(files, desc="parsing cards"):
        path = os.path.join(CARD_DIR, file)
        card = pd.read_json(path, typ="series")
        if card.get("type") != "monster":
            continue
        monsters.append(card)
    df = pd.DataFrame(monsters)
    df.to_parquet(PARQUET_PATH, index=False)

df['type'] = df.apply(lambda r: r.properties[0], axis=1)

# only main deck monsters
df['deck'] = df['properties'].apply(lambda p:
    "ED" if 'Fusion' in p  or 'Synchro' in p or 'Xyz' in p or 'Link' in p else
    "MD")
df = df[df['deck'].isin(['MD'])]

# atk/def ? -> -1
df['atk'] = df['atk'].apply(lambda x: int(x))
df['def'] = df['def'].apply(lambda x: int(x))
df['level'] = df['level'].apply(lambda x: int(x))

df.rename(columns={'localizedAttribute': 'attribute'}, inplace=True)
df = df[['id', 'name', 'attribute', 'level', 'type', 'atk', 'def']]

with open(JSON_PATH, "r", encoding="utf-8") as f:
    json_obj = json.load(f)
jdf = pd.DataFrame(json_obj['data'])

# use konami_id as id
jdf.rename(columns={'id': 'passcode'}, inplace=True)
jdf['id'] = jdf['misc_info'].apply(
    lambda x: x[0].get('konami_id') if x and x[0].get('konami_id') is not None else -1
)

df = df.merge(jdf[['id', 'passcode']], on='id', how='inner')
df = df.merge(jdf[['id', 'frameType']], on='id', how='inner') # ['effect', 'normal', 'ritual', 'effect_pendulum', 'normal_pendulum', 'ritual_pendulum']

# df to csv
csv_path = PARQUET_PATH.replace('.parquet', '.csv')
df.to_csv(csv_path, index=False)
