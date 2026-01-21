// src/wallet/wallet.model.ts
import { Field, Float, ID, ObjectType } from '@nestjs/graphql';

@ObjectType()
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