import sys, calendar, pathlib
import requests
import pyarrow.parquet as pq
import pandas as pd

mois = sys.argv[1]                      # ex. 2025-01
annee, m = map(int, mois.split("-"))
debut = f"{mois}-01"
fin = f"{mois}-{calendar.monthrange(annee, m)[1]} 23:59:59"

url = f"https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{mois}.parquet"
path = pathlib.Path(f"yellow_tripdata_{mois}.parquet")

if not path.exists():
    print("Téléchargement...")
    path.write_bytes(requests.get(url, timeout=300).content)

pf = pq.ParquetFile(path)
print("Fichier     :", path.name)
print("Taille (Mo) :", round(path.stat().st_size / 1e6, 1))
print("Lignes      :", pf.metadata.num_rows)
print("Colonnes    :", len(pf.schema_arrow.names))
print(pf.schema_arrow)

df = pd.read_parquet(path)
print("\nAnomalies :")
print("trip_distance = 0      :", (df["trip_distance"] == 0).sum())
print("total_amount < 0       :", (df["total_amount"] < 0).sum())
hors = ~df["tpep_pickup_datetime"].between(debut, fin)
print(f"pickup hors de {mois}  :", hors.sum())
print("\nPremière ligne :")
print(df.iloc[0].to_string())
