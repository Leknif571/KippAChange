import { Module } from '@nestjs/common';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { GraphQLModule } from '@nestjs/graphql';
import { ConfigModule }  from '@nestjs/config';
import {IntrospectAndCompose, RemoteGraphQLDataSource } from '@apollo/gateway';
import { ApolloGatewayDriver, ApolloGatewayDriverConfig } from '@nestjs/apollo';
import * as jwt from 'jsonwebtoken';

@Module({
  imports: [
    ConfigModule.forRoot({
      isGlobal: true,
    }),
    GraphQLModule.forRoot<ApolloGatewayDriverConfig>({
      driver: ApolloGatewayDriver,
      server: {
        context: ({ req }) => {
          const token = req.headers.authorization?.split(' ')[1];
          if (token) {
            try {
              const secret = process.env.JWT_SECRET;
              if (!secret) {
                console.error("JWT secret is not set");
                return {};
              }
              const decoded = jwt.verify(token, secret) as any;
              return { userId: decoded.sub, userRole: decoded.role, userEmail: decoded.email, userPseudo: decoded.pseudo , userAge: decoded.age };
            } catch (e: any) {
              console.error("Erreur JWT :", e.message);
              return {}; 
            }
          }
          return {};
        },
      },
      gateway: {
        supergraphSdl: new IntrospectAndCompose({
          subgraphs: [
            { name : "auth", url : "http://service-auth:3003/graphql" },
            { name : "user", url : "http://service-user:3002/graphql" },
            // { name : "calendar-match", url : "http://service-calendar-match:8000/graphql" },
            // { name : "bet", url : "http://ms-bet:8001/graphql" },
            // { name : "wallet", url : "http://service-wallet:3005/graphql" }
          ],
        }),
        buildService({ url }) {
          return new RemoteGraphQLDataSource({
            url,
            willSendRequest({ request, context }) {
              if (request.http) {
                request.http.headers.set('x-user-id', context.userId);
                request.http.headers.set('x-user-role', context.userRole);
                request.http.headers.set('x-user-email', context.userEmail);
                request.http.headers.set('x-user-pseudo', context.userPseudo);
                request.http.headers.set('x-user-age', context.userAge);
              }
            },
          });
        },
      },
    }),
    
  ],
  controllers: [AppController],
  providers: [AppService],
})
export class AppModule {}
