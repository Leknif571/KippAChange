import { GraphQLError } from 'graphql';

export class UnauthorizedException extends GraphQLError {
  constructor(message: string = 'Unauthorized') {
    super(message, {
      extensions: {
        code: 'UNAUTHENTICATED', // Code standard Apollo
        http: { status: 401 },    // Pour que la Gateway comprenne le code HTTP
      },
    });
    
    this.name = 'UnauthorizedException';
  }
}