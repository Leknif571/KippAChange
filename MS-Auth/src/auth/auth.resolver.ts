import { Resolver, Query, Mutation, Args, Context } from '@nestjs/graphql';
import { UseGuards } from '@nestjs/common';
import { JwtAuthGuard } from './guards/jwt-auth.guard';
import { AuthService } from './auth.service';
import { User } from './entities/user.entity';

@Resolver()
export class AuthResolver {
  constructor(private authService: AuthService) {}

  @Query('me')
  @UseGuards(JwtAuthGuard)
  getMe(@Context('req') req: Request & { user?: User }) {
    return req.user;
  }


  @Mutation('googleLogin')
  async googleLogin(
    @Args('googleId') googleId: string,
    @Args('email') email: string,
    @Args('pseudo') pseudo: string,
    @Args('age') age: number,
    @Args('role') role: string,
  ) {
    const user: User = await this.authService.findOrCreateUser({
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
