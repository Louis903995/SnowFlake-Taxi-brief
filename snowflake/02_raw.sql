-- Couche RAW : formats de fichier, stage et tables du contrat.
-- À exécuter avec ROLE_TAXI_TOOLS (et non ACCOUNTADMIN) pour que ce rôle soit propriétaire des objets.
-- Rejouable : chaque instruction utilise IF NOT EXISTS.
USE ROLE ROLE_TAXI_TOOLS;
USE WAREHOUSE WH_TAXI;
USE SCHEMA NYC_TAXI.RAW;

CREATE FILE FORMAT IF NOT EXISTS FF_PARQUET
  TYPE = PARQUET
  USE_LOGICAL_TYPE = TRUE;

CREATE FILE FORMAT IF NOT EXISTS FF_CSV_ZONES
  TYPE = CSV
  SKIP_HEADER = 1
  FIELD_OPTIONALLY_ENCLOSED_BY = '"';

CREATE STAGE IF NOT EXISTS STG_TAXI;

CREATE TABLE IF NOT EXISTS YELLOW_TRIPDATA (
  vendorid NUMBER(18,0),
  tpep_pickup_datetime TIMESTAMP_NTZ,
  tpep_dropoff_datetime TIMESTAMP_NTZ,
  passenger_count NUMBER(18,0),
  trip_distance DOUBLE,
  ratecodeid NUMBER(18,0),
  store_and_fwd_flag VARCHAR,
  pulocationid NUMBER(18,0),
  dolocationid NUMBER(18,0),
  payment_type NUMBER(18,0),
  fare_amount DOUBLE,
  extra DOUBLE,
  mta_tax DOUBLE,
  tip_amount DOUBLE,
  tolls_amount DOUBLE,
  improvement_surcharge DOUBLE,
  total_amount DOUBLE,
  congestion_surcharge DOUBLE,
  airport_fee DOUBLE,
  cbd_congestion_fee DOUBLE,
  _source_file VARCHAR,
  _loaded_at TIMESTAMP_NTZ
);

CREATE TABLE IF NOT EXISTS TAXI_ZONE_LOOKUP (
  locationid NUMBER(18,0),
  borough VARCHAR,
  zone VARCHAR,
  service_zone VARCHAR,
  _source_file VARCHAR,
  _loaded_at TIMESTAMP_NTZ
);
