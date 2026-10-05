# Fiche source — Trajets des taxis jaunes de New York (TLC)

Tous les chiffres ont été mesurés avec `ingestion/explorer.py` sur les fichiers téléchargés (janvier, février, mars 2025).

## Identité

| Rubrique | Réponse |
|---|---|
| Nom de la source | Yellow Taxi Trip Records |
| Producteur des données | NYC Taxi and Limousine Commission (TLC) |
| Adresse (URL) | `https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_AAAA-MM.parquet` (ex. `2025-01`) |
| Accès (public, authentifié) | Public, sans authentification |
| Format du fichier | Parquet, un fichier par mois |
| Fréquence de publication | Mensuelle |
| Délai entre la période couverte et la publication | À renseigner d'après votre observation (comparer la date de la dernière période publiée sur la page de la TLC avec la date du jour) |

**Dictionnaire de données** : `Data Dictionary – Yellow Taxi Trip Records`, version du 18 mars 2025 (PDF publié par la TLC). Les codes et les significations ci-dessous en sont extraits.

## Volume mesuré

| Fichier | Taille | Nombre de lignes | Nombre de colonnes | Outil et commande utilisés |
|---|---|---|---|---|
| `yellow_tripdata_2025-01.parquet` | 59,2 Mo | 3 475 226 | 20 | Python, pyarrow : `python ingestion/explorer.py 2025-01` |
| `yellow_tripdata_2025-02.parquet` | 60,3 Mo | 3 577 543 | 20 | `python ingestion/explorer.py 2025-02` |
| `yellow_tripdata_2025-03.parquet` | 70,0 Mo | 4 145 257 | 20 | `python ingestion/explorer.py 2025-03` |

Total des trois mois : 11 198 026 lignes brutes.

## Colonnes

Types lus dans le schéma Parquet. Exemples : première ligne de janvier 2025 (sauf `cbd_congestion_fee`, première ligne de février).

| Colonne | Type dans le fichier | Signification (dictionnaire TLC) | Exemple de valeur |
|---|---|---|---|
| `VendorID` | int32 | Code du fournisseur de compteur (TPEP) qui a transmis l'enregistrement | 1 |
| `tpep_pickup_datetime` | timestamp[us] | Date et heure d'enclenchement du compteur | 2025-01-01 00:18:38 |
| `tpep_dropoff_datetime` | timestamp[us] | Date et heure de coupure du compteur | 2025-01-01 00:26:59 |
| `passenger_count` | int64 | Nombre de passagers dans le véhicule | 1 |
| `trip_distance` | double | Distance parcourue en miles, selon le taximètre | 1.6 |
| `RatecodeID` | int64 | Code du tarif en vigueur à la fin du trajet | 1 |
| `store_and_fwd_flag` | large_string | Indique si l'enregistrement a été conservé dans le véhicule avant envoi (pas de connexion au serveur) | N |
| `PULocationID` | int32 | Zone TLC où le compteur a été enclenché | 229 |
| `DOLocationID` | int32 | Zone TLC où le compteur a été coupé | 237 |
| `payment_type` | int64 | Code du mode de paiement | 1 |
| `fare_amount` | double | Tarif temps-distance calculé par le compteur | 10.0 |
| `extra` | double | Suppléments divers | 3.5 |
| `mta_tax` | double | Taxe déclenchée automatiquement selon le tarif | 0.5 |
| `tip_amount` | double | Pourboire (renseigné automatiquement pour la carte, **pourboires en espèces exclus**) | 3.0 |
| `tolls_amount` | double | Total des péages du trajet | 0.0 |
| `improvement_surcharge` | double | Surcharge d'amélioration appliquée à la prise en charge | 1.0 |
| `total_amount` | double | Montant total facturé au passager, **pourboires en espèces exclus** | 18.0 |
| `congestion_surcharge` | double | Surcharge de congestion de l'État de New York | 2.5 |
| `Airport_fee` | double | Frais de prise en charge aux aéroports LaGuardia et JFK uniquement | 0.0 |
| `cbd_congestion_fee` | double | Frais par trajet pour la zone de réduction de congestion de la MTA, à partir du 5 janvier 2025 | 0.75 |

Remarque : le nom de la colonne est `Airport_fee` dans les fichiers et `airport_fee` dans le dictionnaire.

## Codes

Source : dictionnaire de données TLC du 18 mars 2025 (libellés d'origine).

| Colonne | Valeur | Signification |
|---|---|---|
| `VendorID` | 1 | Creative Mobile Technologies, LLC |
| `VendorID` | 2 | Curb Mobility, LLC |
| `VendorID` | 6 | Myle Technologies Inc |
| `VendorID` | 7 | Helix |
| `RatecodeID` | 1 | Standard rate |
| `RatecodeID` | 2 | JFK |
| `RatecodeID` | 3 | Newark |
| `RatecodeID` | 4 | Nassau or Westchester |
| `RatecodeID` | 5 | Negotiated fare |
| `RatecodeID` | 6 | Group ride |
| `RatecodeID` | 99 | Null/unknown |
| `payment_type` | 0 | Flex Fare trip |
| `payment_type` | 1 | Credit card |
| `payment_type` | 2 | Cash |
| `payment_type` | 3 | No charge |
| `payment_type` | 4 | Dispute |
| `payment_type` | 5 | Unknown |
| `payment_type` | 6 | Voided trip |
| `store_and_fwd_flag` | Y | Store and forward trip |
| `store_and_fwd_flag` | N | Not a store and forward trip |

## Ce qui a surpris

**Anomalies mesurées** (les catégories peuvent se chevaucher, ne pas les additionner) :

| Mois | `trip_distance` = 0 | `total_amount` < 0 | Départ hors du mois |
|---|---|---|---|
| Janvier 2025 | 90 893 | 63 037 | 22 |
| Février 2025 | 99 771 | 55 179 | 31 |
| Mars 2025 | 103 722 | 68 686 | 33 |

- **Dates d'un autre mois** : chaque fichier mensuel contient quelques dizaines de trajets dont le départ tombe hors du mois.
- **Colonne `cbd_congestion_fee`** : elle apparaît en 2025 (frais en vigueur depuis le 5 janvier 2025). Elle vaut 0.0 sur la première ligne de janvier et 0.75 sur celle de février. Les colonnes varient donc d'une année à l'autre : la couche RAW doit les accepter.
- **`payment_type` = 0 (Flex Fare)** : 540 149 lignes en janvier. Le même nombre de lignes a un `RatecodeID` nul, ce qui laisse penser qu'il s'agit des mêmes trajets (à confirmer par une requête).
- **Entiers lus en décimaux** : `passenger_count` et `RatecodeID` sont `int64` dans le fichier, mais pandas les lit en décimal (`1.0`) à cause des valeurs nulles. Une même colonne peut être entière un mois et décimale le suivant : d'où des types larges en RAW.
- **`VendorID` 6 et 7** : très peu de lignes en janvier (489 et 1 206), mais ils figurent bien dans le dictionnaire.
- **Pourboires en espèces absents** : `tip_amount` et `total_amount` ne les incluent pas, donc les trajets payés en espèces paraissent moins rentables qu'ils ne le sont. À signaler pour la question « combien rapporte un trajet ».
- **Volumes inégaux** : mars (70,0 Mo, 4,1 millions de lignes) est nettement plus gros que janvier et février.
