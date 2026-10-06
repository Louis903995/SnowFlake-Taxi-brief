-- Vérifications de la couche RAW (requêtes du contrat CONTRAT_RAW.md).
-- À exécuter avec ROLE_TAXI_TOOLS.
USE ROLE ROLE_TAXI_TOOLS;
USE WAREHOUSE WH_TAXI;

-- 1. Les deux tables existent et appartiennent au rôle des outils (colonne owner)
SHOW TABLES IN SCHEMA NYC_TAXI.RAW;

-- 2. Un mois chargé : lignes par fichier, colonnes techniques remplies
--    (3 475 226 lignes attendues pour janvier 2025)
SELECT _source_file, COUNT(*) AS nb_lignes, MIN(_loaded_at) AS premier_chargement
FROM NYC_TAXI.RAW.YELLOW_TRIPDATA
GROUP BY 1
ORDER BY 1;

-- 3. Les montants ont gardé leurs décimales
SELECT fare_amount, total_amount
FROM NYC_TAXI.RAW.YELLOW_TRIPDATA
LIMIT 5;

-- 4. Les zones : 265 lignes attendues
SELECT COUNT(*) AS nb_zones FROM NYC_TAXI.RAW.TAXI_ZONE_LOOKUP;

-- 5. locationid unique : aucune ligne ne doit être renvoyée
SELECT locationid, COUNT(*)
FROM NYC_TAXI.RAW.TAXI_ZONE_LOOKUP
GROUP BY 1
HAVING COUNT(*) > 1;
