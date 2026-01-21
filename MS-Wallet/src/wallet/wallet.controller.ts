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
    this.walletService.createWallet(data.user_id);
  }

  // Écoute un événement venant de MS-Bet
  @EventPattern('bet_created')
  async handleBetCreated(@Payload() data: { user_id: string; amount: number}) {
    console.log(`Event received - Bet Created for ${data.user_id}, Substract ${data.amount}`);
    this.walletService.debitWallet(data.user_id, data.amount);
  }

  // Écoute un événement venant de MS-Bet
  @EventPattern('bet_won')
  async handleBetWon(@Payload() data: { user_id: string; amount: number }) {
    console.log(`Event received - Bet Won. Add ${data.amount} to ${data.user_id}`);
    this.walletService.creditWallet(data.user_id, data.amount);
  }

  @EventPattern('bet_lost')
  async handleBetLoose(@Payload() data: { user_id: string; amount: number }) {
    console.log(`Event received - Bet Lost. Substract ${data.amount} to ${data.user_id}`);
    this.walletService.debitWallet(data.user_id, data.amount);
  }

}