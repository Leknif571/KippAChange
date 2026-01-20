import { Resolver, Query, Mutation, Args, Context } from '@nestjs/graphql';
import { UseGuards } from '@nestjs/common';
import { JwtAuthGuard } from './guards/jwt-auth.guard';
import { AuthService } from './auth.service';
import { User } from './entities/user.entity';
import { Auth } from './entities/auth.entity';
import { CreateAuthInput } from './dto/create-auth.input';

@Resolver(() => Auth)
export class AuthResolver {
  constructor(private authService: AuthService) {}

  @Query(() => User)
  @UseGuards(JwtAuthGuard)
  getMe(@Context('req') req: Request & { user?: User }) {
    return req.user;
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
