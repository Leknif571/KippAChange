import { Resolver, Query, Args, ResolveField, Parent, ResolveReference, Mutation } from '@nestjs/graphql';
import { WalletService } from './wallet.service';
import { Wallet, User } from './wallet.model';
import { CreateWalletInput } from './dto/create-wallet.input';

@Resolver(() => Wallet)
export class WalletResolver {
  constructor(private readonly walletService: WalletService) {}


  // C'est ultra louche de faire comme ça mais bon j'ai pas encore la solution
  @Query(() => User, { nullable: true, name: '_ignoreMe' })
  _dummy() { return null; }

  @Query(() => [Wallet], { name: 'wallets' })
  getWallets() {
    return this.walletService.findAll();
  }

  @Query(() => Wallet, { name: 'walletByUserId', nullable: true })
  getWallet(@Args('userId') userId: string) {
    return this.walletService.findByUserId(userId);
  }

  @Mutation(() => Wallet)
  async createWallet(
    @Args('createWalletInput') createWalletInput: CreateWalletInput,
  ) {
    return this.walletService.createWallet(createWalletInput.userId);
  }
}

@Resolver(() => User)
export class WalletUserResolver {
  constructor(private readonly walletService: WalletService) {}

  @ResolveReference()
  resolveReference(reference: { __typename: string; googleId: string }) {
    return { googleId: reference.googleId };
  }

  @ResolveField(() => Wallet)
  async wallet(@Parent() user: User): Promise<Wallet | null> {
    return this.walletService.findByUserId(user.googleId);
  }
}