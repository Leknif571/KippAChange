import { ExecutionContext, Injectable } from '@nestjs/common';
import { GqlExecutionContext } from '@nestjs/graphql';
import { AuthGuard } from '@nestjs/passport';
import { User } from '../entities/user.entity';
import { CreateAuthInput } from '../dto/create-auth.input';

@Injectable()
export class JwtAuthGuard extends AuthGuard('jwt') {
  getRequest(context: ExecutionContext): Request & { user?: CreateAuthInput } {
    const ctx: GqlExecutionContext = GqlExecutionContext.create(context);
    const ctxContext: { req: Request & { user?: CreateAuthInput } } = ctx.getContext();
    return ctxContext.req;
  }
}
