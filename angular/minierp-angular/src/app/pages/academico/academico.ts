import {
  Component,
  OnInit,
  inject
} from '@angular/core';

import {
  FormsModule
} from '@angular/forms';

import {
  MateriasService,
  Materia,
  MateriaForm
} from '../../services/materias.service';

import {
  CalificacionesService,
  Calificacion
} from '../../services/calificaciones.service';

import {
  AuthService
} from '../../services/auth.service';


@Component({
  selector: 'app-academico',
  imports: [FormsModule],
  templateUrl: './academico.html',
  styleUrl: './academico.css'
})
export class Academico
  implements OnInit {


  materias: Materia[] = [];

  calificaciones:
    Calificacion[] = [];


  alumnoSeleccionado:
    number | null = null;


  cargando = false;

  error = '';

  mensaje = '';


  private materiasService =
    inject(MateriasService);


  private calificacionesService =
    inject(
      CalificacionesService
    );


  auth =
    inject(AuthService);


  ngOnInit(): void {

    this.cargarMaterias();

    this.cargarCalificaciones();

  }


  cargarMaterias(): void {

    this.materiasService
      .obtenerMaterias()
      .subscribe({

        next: datos => {

          this.materias = datos;

        },

        error: error => {

          console.error(error);

          this.error =
            'No fue posible cargar materias.';

        }

      });

  }


  cargarCalificaciones(): void {

    this.cargando = true;

    this.calificacionesService
      .obtenerCalificaciones()
      .subscribe({

        next: datos => {

          this.calificaciones =
            datos;

          this.cargando = false;

        },

        error: error => {

          console.error(error);

          this.error =
            'No fue posible cargar calificaciones.';

          this.cargando = false;

        }

      });

  }


  filtrarAlumno(): void {

    console.log('FILTRAR EJECUTADO');

    if (
      this.alumnoSeleccionado ===
      null
    ) {

      this.cargarCalificaciones();

      return;

    }

console.log(
  'Alumno seleccionado:',
  this.alumnoSeleccionado
);


    this.cargando = true;

    this.calificacionesService
      .obtenerPorAlumno(
        this.alumnoSeleccionado
      )
      .subscribe({

        next: datos => {

          this.calificaciones =
            datos;

          this.cargando = false;

        },

        error: error => {

          console.error(error);

          this.error =
            'No fue posible obtener las calificaciones.';

          this.cargando = false;

        }

      });

  }


  eliminar(
    calificacion: Calificacion
  ): void {

    if (
      !this.auth.esAdmin()
    ) {

      this.error =
        'No tiene permisos.';

      return;

    }


    const confirmar =
      window.confirm(
        `¿Eliminar la calificación de ${calificacion.alumno}?`
      );


    if (!confirmar) {

      return;

    }


    this.calificacionesService
      .eliminarCalificacion(
        calificacion.id
      )
      .subscribe({

        next: () => {

          this.mensaje =
            'Calificación eliminada.';

          this.cargarCalificaciones();

        },

        error: error => {

          console.error(error);

          this.error =
            error.error?.error ??
            'No fue posible eliminar.';

        }

      });

  }

}
