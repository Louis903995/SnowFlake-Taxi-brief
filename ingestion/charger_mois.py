"""Charge un mois de trajets TLC dans NYC_TAXI.RAW.YELLOW_TRIPDATA.

Usage : python ingestion/charger_mois.py 2025-01

Rejouable : les lignes déjà chargées pour ce fichier sont supprimées puis
rechargées dans une même transaction, donc relancer ne crée aucun doublon.
"""
import os
import re
import sys
import pathlib

import requests
import snowflake.connector
from cryptography.hazmat.primitives import serialization
from dotenv import load_dotenv

BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data"
DOSSIER = pathlib.Path("telechargements")  # ignoré par Git (*.parquet)


def get_connection():
    """Connexion par paire de clés, lue depuis le .env (aucun secret dans le code)."""
    load_dotenv()
    with open(os.environ["SNOWFLAKE_PRIVATE_KEY_PATH"], "rb") as f:
        key = serialization.load_pem_private_key(f.read(), password=None)
    pkb = key.private_bytes(
        serialization.Encoding.DER,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    return snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        private_key=pkb,
        role=os.environ["SNOWFLAKE_ROLE"],
        warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
        database="NYC_TAXI",
        schema="RAW",
    )


def telecharger(mois):
    nom = f"yellow_tripdata_{mois}.parquet"
    chemin = DOSSIER / nom
    if not chemin.exists():
        DOSSIER.mkdir(exist_ok=True)
        print(f"Téléchargement de {nom}...")
        r = requests.get(f"{BASE_URL}/{nom}", timeout=300)
        r.raise_for_status()
        chemin.write_bytes(r.content)
    return nom, chemin


def sql_copy(nom):
    return f"""
COPY INTO YELLOW_TRIPDATA
FROM (
  SELECT
    $1:"VendorID"::NUMBER(18,0),
    $1:"tpep_pickup_datetime"::TIMESTAMP_NTZ,
    $1:"tpep_dropoff_datetime"::TIMESTAMP_NTZ,
    $1:"passenger_count"::NUMBER(18,0),
    $1:"trip_distance"::DOUBLE,
    $1:"RatecodeID"::NUMBER(18,0),
    $1:"store_and_fwd_flag"::VARCHAR,
    $1:"PULocationID"::NUMBER(18,0),
    $1:"DOLocationID"::NUMBER(18,0),
    $1:"payment_type"::NUMBER(18,0),
    $1:"fare_amount"::DOUBLE,
    $1:"extra"::DOUBLE,
    $1:"mta_tax"::DOUBLE,
    $1:"tip_amount"::DOUBLE,
    $1:"tolls_amount"::DOUBLE,
    $1:"improvement_surcharge"::DOUBLE,
    $1:"total_amount"::DOUBLE,
    $1:"congestion_surcharge"::DOUBLE,
    COALESCE($1:"Airport_fee", $1:"airport_fee")::DOUBLE,
    $1:"cbd_congestion_fee"::DOUBLE,
    METADATA$FILENAME,
    CURRENT_TIMESTAMP()::TIMESTAMP_NTZ
  FROM @STG_TAXI
)
FILES = ('{nom}')
FILE_FORMAT = (FORMAT_NAME = 'FF_PARQUET')
FORCE = TRUE
"""


def main():
    if len(sys.argv) != 2 or not re.fullmatch(r"\d{4}-\d{2}", sys.argv[1]):
        sys.exit("Usage : python ingestion/charger_mois.py AAAA-MM")
    mois = sys.argv[1]
    nom, chemin = telecharger(mois)

    conn = get_connection()
    cur = conn.cursor()
    try:
        # 1. Dépôt à la racine du stage, sans compression pour garder le nom exact
        cur.execute(
            f"PUT file://{chemin.resolve()} @STG_TAXI AUTO_COMPRESS=FALSE OVERWRITE=TRUE"
        )
        print("Fichier déposé dans le stage.")

        # 2. Suppression + rechargement dans une même transaction
        cur.execute("BEGIN")
        cur.execute("DELETE FROM YELLOW_TRIPDATA WHERE _source_file = %s", (nom,))
        cur.execute(sql_copy(nom))
        cur.execute("COMMIT")
    except Exception:
        cur.execute("ROLLBACK")
        raise

    cur.execute(
        "SELECT COUNT(*) FROM YELLOW_TRIPDATA WHERE _source_file = %s", (nom,)
    )
    print(f"{nom} : {cur.fetchone()[0]} lignes dans YELLOW_TRIPDATA")
    conn.close()


if __name__ == "__main__":
    main()
