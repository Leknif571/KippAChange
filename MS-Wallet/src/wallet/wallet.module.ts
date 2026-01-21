import { Module } from '@nestjs/common';
import { WalletService } from './wallet.service';
import { WalletResolver } from './wallet.resolver';
import { WalletController } from './wallet.controller';

@Module({
  providers: [WalletService, WalletResolver],
  controllers: [WalletController],
})
export class WalletModule {}