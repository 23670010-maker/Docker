import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Calificacion {
  id: number;
  alumno_id: number;
  Nctrl: string;
  alumno: string;
  materia_id: number;
  clave: string;
  materia: string;
  periodo: string;
  calificacion: number;
}

export interface CalificacionForm {
  alumno_id: number;
  materia_id: number;
  periodo: string;
  calificacion: number;
}

@Injectable({
  providedIn: 'root'
})
export class CalificacionesService {
  private http = inject(HttpClient);
  private apiUrl = 'http://localhost:8080/api/calificaciones';

  private headers(): { headers: HttpHeaders } {
    const token = sessionStorage.getItem('access_token');
    return {
      headers: new HttpHeaders({
        Authorization: `Bearer ${token}`
      })
    };
  }

  obtenerCalificaciones(): Observable<Calificacion[]> {
    return this.http.get<Calificacion[]>(this.apiUrl, this.headers());
  }

  obtenerPorAlumno(alumnoId: number): Observable<Calificacion[]> {
    return this.http.get<Calificacion[]>(
      `${this.apiUrl}/alumno/${alumnoId}`,
      this.headers()
    );
  }

  crearCalificacion(datos: CalificacionForm) {
    return this.http.post(this.apiUrl, datos, this.headers());
  }

  actualizarCalificacion(id: number, datos: CalificacionForm) {
    return this.http.put(`${this.apiUrl}/${id}`, datos, this.headers());
  }

  eliminarCalificacion(id: number) {
    return this.http.delete(`${this.apiUrl}/${id}`, this.headers());
  }
}
