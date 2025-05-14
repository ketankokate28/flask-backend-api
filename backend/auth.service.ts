import { Injectable } from '@angular/core';

@Injectable({ providedIn: 'root' })
export class AuthService {
  /* … your existing login/logout/token logic … */

  getUserRole(): string {
    const token = localStorage.getItem('access_token');
    if (!token) { return ''; }
    const payload = JSON.parse(atob(token.split('.')[1]));
    return payload.role;
  }

  isAdmin(): boolean {
    return this.getUserRole() === 'admin';
  }
}