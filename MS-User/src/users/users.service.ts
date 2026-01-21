import { Injectable, Inject } from '@nestjs/common';
import { CreateUserInput } from './dto/create-user.input';
import { UpdateUserInput } from './dto/update-user.input';
import { UsersRepository } from './repository/users.repository';
import { User } from './entities/user.entity';
import { ClientProxy } from '@nestjs/microservices/client/client-proxy';
import { lastValueFrom } from 'rxjs';

@Injectable()
export class UsersService {

  constructor(
    private readonly usersRepository: UsersRepository,
    @Inject('NOTIF_SERVICE') private readonly client: ClientProxy) {}


    async sendNotification(payload: any) {
        try {
          await lastValueFrom(
            this.client.emit('user_created', payload)
          );
          console.log("Message envoyé à RabbitMQ");
        } catch (error) {
          console.error("Erreur RabbitMQ:", error);
        }
      }

  async create(createUserInput: CreateUserInput) {

    let userExistent:User|string = await this.findOne(createUserInput.googleId);

    if (typeof userExistent === 'string') {
      await this.usersRepository.create(createUserInput);

      let body_received = {
        "pattern": "user_created",
        "data": {
          "googleId": createUserInput.googleId,
          "email": createUserInput.email,
          "pseudo": createUserInput.pseudo,
          "age": createUserInput.age,
          "role": createUserInput.role
        }
      };

      console.log(body_received); 
      await this.sendNotification(JSON.stringify(body_received)).catch((error) => {
        console.error("Erreur lors de l'envoi de la notification : " + error);
      });

      console.log("ZOZO");

      return createUserInput;
    }

    return userExistent;
  }

  async findAll() {
    return await this.usersRepository.findAll();
  }

  async findOne(googleId: string): Promise<User | string> {
    const user: User | null = await this.usersRepository.findById(googleId);

    if (user) {
      return user;
    }
    return 'Utilisateur non trouvé';
  }

  async update(googleId: string, updateUserInput: UpdateUserInput): Promise<string> {
    const updatedUser = await this.usersRepository.update(googleId, updateUserInput);
    if (updatedUser) {
      return 'Utilisateur mis à jour avec succès';
    }
    return 'Utilisateur non trouvé';
  }

  async remove(googleId: string): Promise<string> {
    await this.usersRepository.delete(googleId);
    return 'Utilisateur supprimé avec succès';
  }
}
