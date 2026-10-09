import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-login',
  imports: [FormsModule],
  templateUrl: './login.html',
  styleUrl: './login.css'
})
export class Login {

  username = '';

  password = '';

  cargando = false;

  error = '';

  private auth = inject(AuthService);

  private router = inject(Router);

  iniciarSesion(): void {

    this.error = '';

    if (
      !this.username ||
      !this.password
    ) {

      this.error =
        'Capture usuario y contraseña.';

      return;
    }

    this.cargando = true;

    this.auth
      .login(
        this.username,
        this.password
      )
      .subscribe({

        next: () => {

          this.cargando = false;

          this.router.navigate(
            ['/alumnos']
          );

        },

        error: (err) => {

          console.error(err);

          this.cargando = false;

          this.error =
            err.error?.error ??
            'No fue posible iniciar sesión.';

        }

      });

  }

}
