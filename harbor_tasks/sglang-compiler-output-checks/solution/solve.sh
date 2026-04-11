#!/bin/bash
# Gold solution: Add user delete endpoint

set -e

cat > /workspace/output/src/api/users.ts << 'EOF'
import { AppError } from '../errors.js';
import { UserRepository } from '../repositories.js';
import logger from '../logger.js';

/**
 * Delete a user by ID
 * @param userId - The unique identifier of the user to delete
 * @return The deleted user record
 * @throws AppError if user not found or deletion fails
 */
export async function deleteUser(userId: string) {
  try {
    const repo = new UserRepository();
    const user = await repo.findById(userId);

    if (!user) {
      throw new AppError('User not found', { userId, operation: 'deleteUser' });
    }

    await repo.delete(userId);
    logger.info(`User deleted: ${userId}`);

    return user;
  } catch (error) {
    if (error instanceof AppError) {
      throw error;
    }
    logger.error(`Failed to delete user ${userId}`, error);
    throw new AppError('Failed to delete user', { userId, operation: 'deleteUser' });
  }
}
EOF
