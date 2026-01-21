import { Test, TestingModule } from '@nestjs/testing';
import { UsersResolver } from '../../src/users/users.resolver';
import { UsersService } from '../../src/users/users.service';

describe('UsersResolver', () => {
  let resolver: UsersResolver;
  let service: UsersService;

  const mockUsersService = {
    findAll: jest.fn().mockResolvedValue([
      { googleId: '1', email: 'adel@email.com', pseudo: 'Adel' }
    ]),
    findOne: jest.fn().mockResolvedValue({ googleId: '1', email: 'adel@email.com' }),
    create: jest.fn().mockResolvedValue({ googleId: '1', email: 'adel@email.com' }),
  };

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [
        UsersResolver,
        {
          provide: UsersService,
          useValue: mockUsersService,
        },
      ],
    }).compile();

    resolver = module.get<UsersResolver>(UsersResolver);
    service = module.get<UsersService>(UsersService);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  test('should be defined', () => {
    expect(resolver).toBeDefined();
  });

  test('should return all users', async () => {
    const result = await resolver.findAll();
    
    expect(result).toBeInstanceOf(Array);
    expect(mockUsersService.findAll).toHaveBeenCalled();
  });

  test('should find one user by id', async () => {
    const id = 'test-id';
    await resolver.findOne(id);
    
    expect(mockUsersService.findOne).toHaveBeenCalledWith(id);
  });
});