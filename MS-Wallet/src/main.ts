import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import { MicroserviceOptions, Transport } from '@nestjs/microservices';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  // --- AJOUT RABBITMQ ---
  app.connectMicroservice<MicroserviceOptions>({
    transport: Transport.RMQ,
    options: {
      // En local : localhost. Dans Docker : message-broker (selon ton docker-compose)
      urls: [process.env.RABBITMQ_URI || 'amqp://user:password@localhost:5672'],
      queue: 'wallet_queue', // Nom de la file d'attente spécifique à ce service
      queueOptions: {
        durable: false, // Met à true si tu veux que la file survive au redémarrage
      },
    },
  });

  // Démarrage des deux moteurs (Microservice + HTTP)
  await app.startAllMicroservices();
  await app.listen(3000);
}
bootstrap();