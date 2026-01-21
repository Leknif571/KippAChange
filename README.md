# KippAChange

## Prérequis
- Docker et Docker Compose installés sur votre machine.

## Variables d'environnement
Chaque microservice utilise un fichier `.env` pour gérer ses variables d'environnement. Assurez-vous de configurer correctement ces fichiers avant de démarrer les services.

Ms-Auth/.env :  

Ms-User/.env :  
   - MONGODB_URI=mongodb://mongodb:27017/kippachange
   - RABBITMQ_URI=amqp://rabbitmq:5672

Ms-Notifications/.env :
    - RABBITMQ_URI=amqp://rabbitmq:5672

## Démarrage des services
1. Clonez ce dépôt sur votre machine locale.
2. Ouvrez un terminal et naviguez jusqu'au répertoire du projet.
3. Exécutez la commande suivante pour démarrer tous les services définis dans le fichier `docker-compose.yml` :
   ```bash
   docker-compose up --build
   ```
4. Attendez que tous les services soient démarrés. Vous devriez voir des logs indiquant que chaque service est en cours d'exécution.

## Accées à la gateway
Une fois tous les services démarrés, vous pouvez accéder à la gateway via l'URL suivante :
http://localhost:4001/graphql

Ce lien vous positionnera directement dans le playground GraphQL pour interagir avec les microservices.

## Accès à MongoDB
Vous pouvez accéder à MongoDB via Mongo Express à l'adresse suivante :
http://localhost:8081
Utilisez les identifiants suivants pour vous connecter :
- Utilisateur : admin
- Mot de passe : pass

## Requêtes GraphQL et use-cases
Pour tester les différents use-cases voici quelques requêtes a copier/coller dans le playground GraphQL :

### Création d'un utilisateur
```graphql
mutation {
  createUser(createUserInput: {
    googleId: "sampleGoogleId",
    email: "<EMAIL>",
    name: "Sample User"
    }) {
        accessToken
    }
}
```


## Scénario métier

Création d'un match>Trader dépose une côte>Utilisateur fait un pari sur ce match>Trader mets les résultats du match

Events : 
- Création d'un match:
    - Match créé en bdd
- Trader dépose une côte:
    - Côte modifiée sur le match en question
- Utilisateur fait un pari sur ce match:
    - Pari créé en bdd
    - Soustraction du montant du pari par rapport au montant du wallet
    - Notification envoyée "Pari créé"
- Trader mets les résultats du match:
    - Score modifié sur le match en question
    - Modification du résultat du pari
    - Ajout d'argent dans wallet pari gagné
    - Notification envoyée "Pari gagné/perdu"

