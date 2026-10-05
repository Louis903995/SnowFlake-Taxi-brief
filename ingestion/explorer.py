import pathlib
import requests
import pyarrow.parquet as pq
import pandas as pd

URL = "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2025-01.parquet"
path = pathlib.Path("yellow_tripdata_2025-01.parquet")

if not path.exists():
    print("Téléchargement...")
    path.write_bytes(requests.get(URL, timeout=300).content)

pf = pq.ParquetFile(path)
print("Taille (Mo) :", round(path.stat().st_size / 1e6, 1))
print("Lignes      :", pf.metadata.num_rows)
print("\nColonnes et types :")
print(pf.schema_arrow)

df = pd.read_parquet(path)
print("\nAnomalies sur janvier 2025 :")
print("trip_distance = 0        :", (df["trip_distance"] == 0).sum())
print("total_amount < 0         :", (df["total_amount"] < 0).sum())
hors = ~df["tpep_pickup_datetime"].between("2025-03-01", "2025-03-31 23:59:59")
print("pickup hors de janvier   :", hors.sum())
print("\nValeurs de payment_type :")
print(df["payment_type"].value_counts(dropna=False).sort_index())
print("\nValeurs de RatecodeID :")
print(df["RatecodeID"].value_counts(dropna=False).sort_index())
print("\nValeurs de VendorID :")
print(df["VendorID"].value_counts(dropna=False).sort_index())
