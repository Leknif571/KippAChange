import { Module } from '@nestjs/common';
import { UsersModule } from './users/users.module';
import { ConfigModule } from '@nestjs/config';
import { GraphQLModule } from '@nestjs/graphql';
import { ApolloFederationDriver, ApolloFederationDriverConfig } from '@nestjs/apollo';
import { MongooseModule } from '@nestjs/mongoose';

@Module({
  imports: [
    ConfigModule.forRoot({
      isGlobal: true,
    }),
    GraphQLModule.forRoot<ApolloFederationDriverConfig>({
      driver: ApolloFederationDriver,
      playground: true,
     autoSchemaFile: {
      federation: 2,
    },}),
    MongooseModule.forRoot(
      process.env.MONGO_URL || 'mongodb://mongodb:27017/hubertapp_users',
    ),
    UsersModule,
  ],
  controllers: [],
  providers: [],
})
export class AppModule {}
