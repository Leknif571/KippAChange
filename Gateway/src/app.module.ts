import { Module } from '@nestjs/common';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { GraphQLModule } from '@nestjs/graphql';
import { ConfigModule } from '@nestjs/config';
import { IntrospectAndCompose, RemoteGraphQLDataSource } from '@apollo/gateway';
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
          const authHeader = req.headers.authorization;
          const token = authHeader?.split(' ')[1];

          if (!token) {
            return { authState: 'ANONYMOUS' };
          }

          try {
            const secret = process.env.JWT_SECRET;
            if (!secret) {
              return { authState: 'ERROR' };
            }

            const decoded = jwt.verify(token, secret) as any;
            
            return { 
              userId: decoded.sub,
              userRole: decoded.role, 
              userEmail: decoded.email, 
              userPseudo: decoded.pseudo, 
              userAge: decoded.age,
              authState: "VALID" 
            };
          } catch (e: any) {
            return { authState: "INVALID_TOKEN" }; 
          }
        },
      },
      gateway: {
        supergraphSdl: new IntrospectAndCompose({
          subgraphs: [
            { name: "auth", url: "http://service-auth:3003/graphql" },
            { name: "user", url: "http://service-user:3002/graphql" },
            { name: "calendar-match", url: "http://ms-calendar:8000/graphql" },
            { name: "bet", url: "http://ms-bet:80/graphql" },
            { name: "wallet", url: "http://ms-wallet:3010/graphql" },
          ],
        }),
        buildService({ url }) {
          return new RemoteGraphQLDataSource({
            url,
            willSendRequest({ request, context }) {
              if (request.http) {
                request.http.headers.set('x-auth-state', context.authState || 'ANONYMOUS');

                if (context.authState === 'VALID' && context.userId) {
                  request.http.headers.set('x-user-id', String(context.userId));
                  request.http.headers.set('x-user-role', String(context.userRole));
                  request.http.headers.set('x-user-email', String(context.userEmail));
                  request.http.headers.set('x-user-pseudo', String(context.userPseudo));
                  request.http.headers.set('x-user-age', String(context.userAge));
                }
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