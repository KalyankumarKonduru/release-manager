import client from './client'
import { User, AuthToken } from '@/types'

export async function login(email: string, password: string): Promise<AuthToken> {
  const response = await client.post('/auth/login', { email, password })
  return response.data
}

export async function register(email: string, password: string, name: string): Promise<AuthToken> {
  const response = await client.post('/auth/register', { email, password, name })
  return response.data
}

export async function getMe(): Promise<User> {
  const response = await client.get('/auth/me')
  return response.data
}

export async function refreshToken(): Promise<AuthToken> {
  const response = await client.post('/auth/refresh')
  return response.data
}

export async function logout(): Promise<void> {
  await client.post('/auth/logout')
}
