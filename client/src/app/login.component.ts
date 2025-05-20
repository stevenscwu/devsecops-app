import { Component } from '@angular/core';

@Component({
  selector: 'app-login',
  template: `
    <input [(ngModel)]="username" placeholder="Username">
    <input [(ngModel)]="password" type="password" placeholder="Password">
    <button (click)="login()">Login</button>
  `
})
export class LoginComponent {
  username = '';
  password = '';

  login() {
    console.log('Logging in with', this.username, this.password); // 🔴 should be avoided in prod

    eval("console.log('This is dangerous')"); // 🔴 security risk

    fetch('http://insecure-api.local/login', {
      method: 'POST',
      body: JSON.stringify({ username: this.username, password: this.password })
    }).then(res => res.text()).then(console.log);
  }
}
