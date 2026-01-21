import { Controller } from '@nestjs/common';
import { EventPattern, Payload } from '@nestjs/microservices';
import { WalletService } from './wallet.service';

@Controller()
export class WalletController {
  constructor(private readonly walletService: WalletService) {}

  // Écoute l'événement "user_created" (par exemple venant de MS-Notifications ou Auth)
  @EventPattern('user_created')
  async handleUserCreated(@Payload() data: any) {
    console.log('Event received - User Created:', data);
    this.walletService.createWallet(data.userId);
  }

  // Écoute un événement venant de MS-Bet
  @EventPattern('bet_won')
  async handleBetWon(@Payload() data: { userId: string; amount: number }) {
    console.log(`Event prout - Bet Won. Add ${data.amount} to ${data.userId}`);
    this.walletService.creditWallet(data.userId, data.amount);
  }
}