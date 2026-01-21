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

    if (data.user_id && data.email) {
      this.notificationsService.create(data.user_id, `Bienvenue ${data.email} !`);
    }
  }

  @EventPattern('bet_created')
  handleBetCreated(@Payload() data: any, @Ctx() context: RmqContext) {
    console.log(`⚡️ Event [BetCreated] Reçu via RabbitMQ :`, data);

    if (data.user_id && data.match_id) {
      this.notificationsService.create(data.user_id, `Bet ${data.match_id} du joueur ${data.user_id} avec la probabilité ${data.odds} à payer ${data.amount} !`);
    }
  }

  @EventPattern('bet_won')
  handleBetWon(@Payload() data: any, @Ctx() context: RmqContext) {
    console.log(`⚡️ Event [BetCreated] Reçu via RabbitMQ :`, data);

    if (data.user_id && data.match_id) {
      this.notificationsService.create(data.user_id, `Bet ${data.match_id} du joueur ${data.user_id} est gagné !`);
    }
  }

  @EventPattern('bet_loose')
  handleBetLoose(@Payload() data: any, @Ctx() context: RmqContext) {
    console.log(`⚡️ Event [BetCreated] Reçu via RabbitMQ :`, data);

    if (data.user_id && data.match_id) {
      this.notificationsService.create(data.user_id, `Bet ${data.match_id} du joueur ${data.user_id} est perdue !`);
    }
  }
}