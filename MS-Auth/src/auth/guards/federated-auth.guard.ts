import { GqlExecutionContext } from "@nestjs/graphql";
import { UnauthorizedException } from "../exception/unauthorized.exception";
import { CanActivate, ExecutionContext, Injectable } from "@nestjs/common";

@Injectable()
export class FederatedAuthGuard implements CanActivate {
  canActivate(context: ExecutionContext): boolean {
    const ctx = GqlExecutionContext.create(context).getContext();
    const userId = ctx.req.headers['x-user-id'];
    console.log("UserId from Gateway headers:", userId);
    // const userEmail = ctx.req.headers['x-user-email'];
    // const userPseudo = ctx.req.headers['x-user-pseudo'];

    if (!userId) {
      throw new UnauthorizedException('Recherche utilisateur impossible sans badge Gateway');
    }

    ctx.req.user = { id: userId, role: ctx.req.headers['x-user-role'] };
    return true;
  }
}