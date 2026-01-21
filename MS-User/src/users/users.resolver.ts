import { Resolver, Query, Mutation, Args, Directive } from '@nestjs/graphql';
import { UsersService } from './users.service';
import { CreateUserInput } from './dto/create-user.input';
import { UpdateUserInput } from './dto/update-user.input';
import { UseGuards } from '@nestjs/common';
import { FederatedAuthGuard } from './guards/federated-auth.guard';
import { CurrentUser } from './decorator/current-user.decorator';
import { User } from './entities/user.entity';

@Resolver(() => User)
export class UsersResolver {
  constructor(private readonly usersService: UsersService) {}


  @Query(() => User)
  @UseGuards(FederatedAuthGuard)
  async getMe(@CurrentUser() user: User) {
    return { googleId: user.googleId, age : user.age, email: user.email, pseudo: user.pseudo, role: user.role }; 
  }


  @Directive('@inaccessible')
  @Mutation(() => User)
  async createUser(@Args('createUserInput') createUserInput: CreateUserInput) {
    return await this.usersService.create(createUserInput);
  }

  @Query(() => [User], { name: 'users' })
  async findAll() {
    const users: User[] = await this.usersService.findAll();
    return users;
  }
  @Query(() => User, { name: 'user' })
  async findOne(@Args('googleId') googleId: string) {
    const user: User | string = await this.usersService.findOne(googleId);
    return user;
  }

  @Directive('@inaccessible')
  @Mutation(() => User)
  async updateUser(@Args('updateUserInput') updateUserInput: UpdateUserInput) {
    const message: string = await this.usersService.update(
      updateUserInput.googleId,
      updateUserInput,
    );
    return message;
  }

  @Directive('@inaccessible')
  @Mutation(() => User)
  async removeUser(@Args('googleId') googleId: string): Promise<string> {
    const message: string = await this.usersService.remove(googleId);
    return message;
  }
}