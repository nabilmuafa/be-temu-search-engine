import pandas as pd
import kagglehub
import json
import os

# Buat folder data jika belum ada
os.makedirs("data", exist_ok=True)

# Baca file CSV
input_file = kagglehub.dataset_download(
    "cryptexcode/mpst-movie-plot-synopses-with-tags")
output_file = "data/mpst_docs.jsonl"

df = pd.read_csv(input_file + "/mpst_movie_plots.csv", encoding="utf-8")

with open(output_file, "w", encoding="utf-8") as f:
    for _, row in df.iterrows():
        json.dump({
            "doc_id": row["imdb_id"],
            "title": row["title"],
            "plot": row["plot_synopsis"],
            "tags": [tag.strip() for tag in str(row["tags"]).split(",") if tag.strip()]
        }, f)
        f.write("\n")

print(f"Selesai simpan {output_file}")
