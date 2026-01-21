import { Injectable, NotFoundException } from '@nestjs/common';
import { Wallet } from './wallet.model';

@Injectable()
export class WalletService {
  // Simulation de BDD
  private wallets: Wallet[] = [
    { id: '1', userId: 'user123', balance: 150.50, currency: 'EUR' },
    { id: '2', userId: 'user456', balance: 2000.00, currency: 'USD' },
  ];

  findAll(): Wallet[] {
    return this.wallets;
  }

  findByUserId(userId: string): Wallet {
    const wallet = this.wallets.find((w) => w.userId === userId);
    if (!wallet) {
      throw new NotFoundException(`Wallet not found for user ${userId}`);
    }
    return wallet;
  }


  createWallet(userId: string): Wallet {
    const existingWallet = this.wallets.find((w) => w.userId === userId);
    if (existingWallet) {
      return existingWallet;
    }

    const newWallet: Wallet = {
      id: Math.random().toString(36).substring(7),
      userId: userId,
      balance: 0, // Un nouveau wallet commence à 0
      currency: 'EUR',
    };

    this.wallets.push(newWallet);
    console.log(`Wallet créé pour l'user ${userId}`);
    return newWallet;
  }

  creditWallet(userId: string, amount: number): Wallet {
    // On réutilise findByUserId pour récupérer le wallet (et ça lance une erreur 404 s'il n'existe pas)
    const wallet = this.findByUserId(userId);
    console.log("Wallet:", wallet);
    if(!wallet || wallet == null){
        this.createWallet(userId);
        console.log(`Wallet créé pour l'user ${userId} lors du crédit`);
    }
    wallet.balance += amount;
    console.log(`Wallet de ${userId} crédité de ${amount}. Nouveau solde : ${wallet.balance}`);
    
    return wallet;
  }
}