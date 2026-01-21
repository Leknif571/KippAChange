import { Module } from '@nestjs/common';
import { GraphQLModule } from '@nestjs/graphql';
import { ApolloFederationDriver, ApolloFederationDriverConfig } from '@nestjs/apollo';
import { join } from 'path';
import { WalletModule } from './wallet/wallet.module';

@Module({
  imports: [
    GraphQLModule.forRoot<ApolloFederationDriverConfig>({
      driver: ApolloFederationDriver,
      playground: true,
      // typePaths: ['./**/*.graphql'],
      autoSchemaFile: {
        federation: 2,
      },
    }),

    WalletModule,
  ],
})
export class AppModule {}