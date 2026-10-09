import { Component, OnInit, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { MateriasService, Materia } from '../../services/materias.service';
import { CalificacionesService, Calificacion } from '../../services/calificaciones.service';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-academico',
  standalone: true,
  imports: [FormsModule, RouterLink],
  templateUrl: './academico.html',
  styleUrl: './academico.css'
})
export class Academico implements OnInit {
  materias: Materia[] = [];
  calificaciones: Calificacion[] = [];
  todasLasCalificaciones: Calificacion[] = [];

  alumnoSeleccionado: number | null = null;
  cargando = false;
  error = '';
  mensaje = '';

  private materiasService = inject(MateriasService);
  private calificacionesService = inject(CalificacionesService);
  auth = inject(AuthService);

  ngOnInit(): void {
    this.cargarMaterias();
    this.cargarCalificaciones();
  }

  cargarMaterias(): void {
    this.materiasService.obtenerMaterias().subscribe({
      next: (datos) => {
        this.materias = datos;
      },
      error: (err) => {
        console.error(err);
        this.error = 'No fue posible cargar materias.';
      }
    });
  }

  cargarCalificaciones(): void {
    this.cargando = true;
    this.error = '';
    this.mensaje = '';
    this.calificacionesService.obtenerCalificaciones().subscribe({
      next: (datos) => {
        this.todasLasCalificaciones = Array.isArray(datos) ? datos : [];
        this.calificaciones = [...this.todasLasCalificaciones];
        this.cargando = false;
      },
      error: (err) => {
        console.error(err);
        this.cargando = false;
        this.error = 'Sesión expirada o no autorizada. Inicia sesión nuevamente.';
      }
    });
  }

  filtrarAlumno(): void {
    this.error = '';
    this.mensaje = '';
    this.cargando = false;

    if (!this.alumnoSeleccionado) {
      this.calificaciones = [...this.todasLasCalificaciones];
      return;
    }

    const id = Number(this.alumnoSeleccionado);
    this.calificaciones = this.todasLasCalificaciones.filter(
      (c) => c.alumno_id === id
    );

    if (this.calificaciones.length === 0) {
      this.mensaje = `El alumno con ID ${id} no tiene calificaciones registradas.`;
    }
  }

  eliminar(calificacion: Calificacion): void {
    if (!this.auth.esAdmin()) {
      this.error = 'No tiene permisos.';
      return;
    }

    const confirmar = window.confirm(`¿Eliminar la calificación de ${calificacion.alumno}?`);
    if (!confirmar) return;

    this.calificacionesService.eliminarCalificacion(calificacion.id).subscribe({
      next: () => {
        this.mensaje = 'Calificación eliminada correctamente.';
        this.cargarCalificaciones();
      },
      error: (err) => {
        console.error(err);
        this.error = 'No fue posible eliminar la calificación.';
      }
    });
  }
}
