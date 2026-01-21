-- Créer les bases de données pour chaque microservice
CREATE DATABASE calendar_db;
CREATE DATABASE auth_db;
CREATE DATABASE user_db;

-- Créer les utilisateurs
CREATE USER calendar_user WITH PASSWORD 'calendar_password';
CREATE USER auth_user WITH PASSWORD 'auth_password';
CREATE USER user_user WITH PASSWORD 'user_password';

-- Accorder les privilèges
GRANT ALL PRIVILEGES ON DATABASE calendar_db TO calendar_user;
GRANT ALL PRIVILEGES ON DATABASE auth_db TO auth_user;
GRANT ALL PRIVILEGES ON DATABASE user_db TO user_user;
