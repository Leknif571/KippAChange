import { Resolver, Query, Mutation, Args, Context } from '@nestjs/graphql';
import { UseGuards } from '@nestjs/common';
import { JwtAuthGuard } from './guards/jwt-auth.guard';
import { AuthService } from './auth.service';
import { User } from './entities/user.entity';
import { Auth } from './entities/auth.entity';
import { CreateAuthInput } from './dto/create-auth.input';
import { FederatedAuthGuard } from './guards/federated-auth.guard';
import { CurrentUser } from './decorator/current-user.decorator';

@Resolver(() => Auth)
export class AuthResolver {
  constructor(private authService: AuthService) {}

  @Query(() => User)
  @UseGuards(FederatedAuthGuard)
  async getMe(@CurrentUser() userId: string) { 
    return { googleId: userId, age : null, email: null, pseudo: null, role: null }; 
  }

  @Mutation(() => Auth)
  async googleLogin(
    @Args('googleId') googleId: string,
    @Args('email') email: string,
    @Args('pseudo') pseudo: string,
    @Args('age') age: number,
    @Args('role') role: string,
  ) {
    const user: CreateAuthInput = await this.authService.findOrCreateUser({
      googleId,
      email,
      pseudo,
      age,
      role,
    });

    const accessToken = this.authService.getJwtToken(user);

    return {
      user: user,
      accessToken: accessToken,
    };
  }
}
