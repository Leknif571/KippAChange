# Étape 1 : On part d'une image Node.js légère (Alpine Linux)
FROM node:20-alpine

# Étape 2 : Définir le répertoire de travail dans le conteneur
WORKDIR /usr/src/app

# Étape 3 : Copier les fichiers de dépendances (package.json et lock file)
# On fait ça AVANT de copier tout le code pour profiter du cache Docker
COPY package*.json ./

# Étape 4 : Installer les dépendances
RUN npm install

# Étape 5 : Copier tout le reste du code source
COPY . .

# Étape 6 : Construire l'application (Compilation TypeScript -> JavaScript)
RUN npm run build

# Étape 7 : Exposer le port (Purement informatif, mais bonne pratique)
EXPOSE 3000

# Étape 8 : Commande de démarrage
# On lance directement le fichier compilé (plus rapide et stable que npm run start)
CMD ["node", "dist/main"]