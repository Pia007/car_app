SELECT 'CREATE DATABASE car_dealer_db'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'car_dealer_db')\gexec

\c car_dealer_db

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET default_tablespace = '';
SET default_with_oids = false;