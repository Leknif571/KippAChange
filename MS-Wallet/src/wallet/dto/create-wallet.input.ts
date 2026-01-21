import { InputType, Field, Float } from '@nestjs/graphql';

@InputType()
export class CreateWalletInput {
  @Field()
  userId: string;

  @Field(() => Float, { defaultValue: 0 })
  balance: number;

  @Field({ defaultValue: 'EUR' })
  currency: string;
}