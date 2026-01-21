import { Module } from '@nestjs/common';
import { WalletService } from './wallet.service';
import { WalletResolver, WalletUserResolver } from './wallet.resolver';
import { WalletController } from './wallet.controller';

@Module({
  providers: [WalletService, WalletResolver, WalletUserResolver],
  controllers: [WalletController],
})
export class WalletModule {}