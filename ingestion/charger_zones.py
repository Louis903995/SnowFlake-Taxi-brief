"""Charge la liste des 265 zones TLC dans NYC_TAXI.RAW.TAXI_ZONE_LOOKUP.

Usage : python ingestion/charger_zones.py

Rejouable : la table est vidée puis rechargée dans une même transaction.
"""
import pathlib

import requests

from charger_mois import get_connection

URL = "https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv"
NOM = "taxi_zone_lookup.csv"
DOSSIER = pathlib.Path("telechargements")


def main():
    chemin = DOSSIER / NOM
    if not chemin.exists():
        DOSSIER.mkdir(exist_ok=True)
        print(f"Téléchargement de {NOM}...")
        r = requests.get(URL, timeout=120)
        r.raise_for_status()
        chemin.write_bytes(r.content)

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            f"PUT file://{chemin.resolve()} @STG_TAXI AUTO_COMPRESS=FALSE OVERWRITE=TRUE"
        )
        cur.execute("BEGIN")
        cur.execute("DELETE FROM TAXI_ZONE_LOOKUP")
        cur.execute(f"""
            COPY INTO TAXI_ZONE_LOOKUP
            FROM (
              SELECT $1::NUMBER(18,0), $2, $3, $4,
                     METADATA$FILENAME,
                     CURRENT_TIMESTAMP()::TIMESTAMP_NTZ
              FROM @STG_TAXI
            )
            FILES = ('{NOM}')
            FILE_FORMAT = (FORMAT_NAME = 'FF_CSV_ZONES')
            FORCE = TRUE
        """)
        cur.execute("COMMIT")
    except Exception:
        cur.execute("ROLLBACK")
        raise

    cur.execute("SELECT COUNT(*), COUNT(DISTINCT locationid) FROM TAXI_ZONE_LOOKUP")
    total, distincts = cur.fetchone()
    print(f"{total} lignes, {distincts} locationid distincts")
    conn.close()


if __name__ == "__main__":
    main()
