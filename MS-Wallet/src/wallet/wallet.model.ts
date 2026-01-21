import { Directive, Field, Float, ID, ObjectType } from '@nestjs/graphql';

@ObjectType()
@Directive('@key(fields: "id")')
export class Wallet {
  @Field(() => ID)
  id: string;

  @Field()
  userId: string;

  @Field(() => Float)
  balance: number;

  @Field()
  currency: string;
}

@ObjectType()
@Directive('@extends')
@Directive('@key(fields: "googleId")')
export class User {
  @Field(() => ID)
  @Directive('@external')
  googleId: string;

  @Field(() => Wallet, { nullable: true })
  wallet?: Wallet;
}