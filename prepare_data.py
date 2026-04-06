import pandas as pd
import os

df = pd.read_csv('Data/mtsamples.csv')
df = df.dropna(subset=['transcription'])
print(f"Total usable records: {len(df)}")

os.makedirs('data/raw', exist_ok=True)

for i, row in df.head(20).iterrows():
    specialty = str(row['medical_specialty']).strip().replace('/', '-').replace(' ', '_')
    sample_name = str(row['sample_name']).strip().replace('/', '-').replace(' ', '_')
    filename = f"data/raw/{i:04d}_{specialty}_{sample_name}.txt"

    content = f"""MEDICAL SPECIALTY: {row['medical_specialty']}
SAMPLE NAME: {row['sample_name']}
DESCRIPTION: {row['description']}
KEYWORDS: {row['keywords']}

TRANSCRIPTION:
{row['transcription']}
"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)

print("Saved 20 sample files to data/raw/")
for f in sorted(os.listdir('data/raw')):
    print(f"  - {f}")