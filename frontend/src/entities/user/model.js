export class User {
  constructor(data) {
    this.id = data.id;
    this.email = data.email;
    this.name = data.name;
    this.createdAt = data.created_at;
  }

  static fromApiResponse(data) {
    return new User(data);
  }

  get displayName() {
    return this.name || this.email;
  }
}

export const createUser = (data) => new User(data); 