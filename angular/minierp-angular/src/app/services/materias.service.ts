import {
  Injectable,
  inject
} from '@angular/core';

import {
  HttpClient
} from '@angular/common/http';

import {
  Observable
} from 'rxjs';

export interface Materia {

  id: number;

  clave: string;

  nombre: string;

  semestre: number;

  creditos: number;

  activo: boolean;

}

export interface MateriaForm {

  clave: string;

  nombre: string;

  semestre: number;

  creditos: number;

}

@Injectable({
  providedIn: 'root'
})
export class MateriasService {

  private http =
    inject(HttpClient);

  private apiUrl =
    'http://localhost:8081/api/materias';

  obtenerMaterias():
    Observable<Materia[]> {

    return this.http.get<Materia[]>(
      this.apiUrl
    );

  }

  crearMateria(
    datos: MateriaForm
  ) {

    return this.http.post(
      this.apiUrl,
      datos
    );

  }

  actualizarMateria(
    id: number,
    datos: MateriaForm
  ) {

    return this.http.put(
      `${this.apiUrl}/${id}`,
      datos
    );

  }

  eliminarMateria(
    id: number
  ) {

    return this.http.delete(
      `${this.apiUrl}/${id}`
    );

  }

}
