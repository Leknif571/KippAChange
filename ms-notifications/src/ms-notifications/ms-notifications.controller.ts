import { Controller } from '@nestjs/common';
import { EventPattern, Payload, Ctx, RmqContext } from '@nestjs/microservices';
import { NotificationsService } from './ms-notifications.service';

@Controller()
export class NotificationsController {
  constructor(private readonly notificationsService: NotificationsService) {}

  // Dès qu'un message avec le motif "user_created" arrive, cette fonction se lance
  @EventPattern('user_created')
  handleUserCreated(@Payload() data: any, @Ctx() context: RmqContext) {
    console.log(`⚡️ Event [UserCreated] Reçu via RabbitMQ :`, data);

    if (data.userId && data.email) {
      this.notificationsService.create(data.userId, `Bienvenue ${data.email} !`);
    }
  }

  @EventPattern('bet_created')
  handleBetCreated(@Payload() data: any, @Ctx() context: RmqContext) {
    console.log(`⚡️ Event [BetCreated] Reçu via RabbitMQ :`, data);

    if (data.userId && data.matchId) {
      this.notificationsService.create(data.userId, `Bet ${data.matchId} du joueur ${data.userId} avec la probabilité ${data.odds} à payer ${data.amount} !`);
    }
  }
}