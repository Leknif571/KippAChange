// src/wallet/wallet.resolver.ts
import { Resolver, Query, Args } from '@nestjs/graphql';
import { WalletService } from './wallet.service';
import { Wallet } from './wallet.model';

@Resolver(() => Wallet)
export class WalletResolver {
  constructor(private readonly walletService: WalletService) {}

  // Route: Récupérer tous les wallets
  @Query(() => [Wallet], { name: 'wallets' })
  getWallets() {
    return this.walletService.findAll();
  }

  // Route: Récupérer un wallet par User ID
  @Query(() => Wallet, { name: 'walletByUserId', nullable: true })
  getWallet(@Args('userId') userId: string) {
    return this.walletService.findByUserId(userId);
  }
}