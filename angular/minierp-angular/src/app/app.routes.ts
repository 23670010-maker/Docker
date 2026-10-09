import { Routes } from '@angular/router';

import { Login } from './pages/login/login';

import { Alumnos } from './pages/alumnos/alumnos';

import { authGuard } from './auth-guard';

import { Academico } from './pages/academico/academico';

export const routes: Routes = [

  {
    path: 'login',

    component: Login
  },
  {
    path: 'academico',

    component: Academico,

    canActivate: [
      authGuard
    ]
  },

  {
    path: 'alumnos',

    component: Alumnos,

    canActivate: [

      authGuard

    ]
  },

  {
    path: '',

    redirectTo: 'alumnos',

    pathMatch: 'full'
  }

];
