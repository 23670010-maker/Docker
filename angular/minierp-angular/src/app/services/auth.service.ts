import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap } from 'rxjs';

export interface LoginResponse {

  access_token: string;

  usuario: string;

  rol: string;
}


@Injectable({
  providedIn: 'root'
})
export class AuthService {

  private http = inject(HttpClient);

  private apiUrl =
    'http://localhost:8080/api/auth';


  login(
    username: string,
    password: string
  ): Observable<LoginResponse> {

    return this.http
      .post<LoginResponse>(
        `${this.apiUrl}/login`,
        {
          username,
          password
        }
      )
      .pipe(

        tap(respuesta => {

          sessionStorage.setItem(
            'access_token',
            respuesta.access_token
          );

          sessionStorage.setItem(
            'usuario',
            respuesta.usuario
          );

          sessionStorage.setItem(
            'rol',
            respuesta.rol
          );

        })

      );

  }


  logout(): void {

    sessionStorage.removeItem(
      'access_token'
    );

    sessionStorage.removeItem(
      'usuario'
    );

    sessionStorage.removeItem(
      'rol'
    );

  }


  estaAutenticado(): boolean {

    return !!sessionStorage.getItem(
      'access_token'
    );

  }


  obtenerToken(): string | null {

    return sessionStorage.getItem(
      'access_token'
    );

  }


  obtenerUsuario(): string {

    return sessionStorage.getItem(
      'usuario'
    ) ?? '';

  }


  obtenerRol(): string {

    return sessionStorage.getItem(
      'rol'
    ) ?? '';

  }


  esAdmin(): boolean {

    return this.obtenerRol() === 'admin';

  }

}
