import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Alumno {
  id: number;
  Nctrl: string;
  nombre: string;
  promedio: number;
  carrera: string;
  semestre: number;
  sexo: string;
}

export interface AlumnoForm {
  Nctrl: string;
  nombre: string;
  promedio: number;
  carrera: string;
  semestre: number;
  sexo: string;
}

@Injectable({
  providedIn: 'root'
})
export class AlumnosService {

  private http = inject(HttpClient);

  private apiUrl = 'http://localhost:8080/api/alumnos';

  obtenerAlumnos(): Observable<Alumno[]> {
    return this.http.get<Alumno[]>(this.apiUrl);
  }

  crearAlumno(
    datos: AlumnoForm
  ): Observable<{mensaje: string, id: number}> {

    return this.http.post<{mensaje: string, id: number}>(
      this.apiUrl,
      datos
    );

  }

  actualizarAlumno(
    id: number,
    datos: AlumnoForm
  ): Observable<{mensaje: string}> {

    return this.http.put<{mensaje: string}>(
      `${this.apiUrl}/${id}`,
      datos
    );

  }

  eliminarAlumno(
    id: number
  ): Observable<{mensaje: string}> {

    return this.http.delete<{mensaje: string}>(
      `${this.apiUrl}/${id}`
    );

  }

}
