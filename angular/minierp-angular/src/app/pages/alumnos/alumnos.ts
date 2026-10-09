import { Component, OnInit, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { HttpClient } from '@angular/common/http';

import {
  AlumnosService,
  Alumno,
  AlumnoForm
} from '../../services/alumnos';

@Component({
  selector: 'app-alumnos',
  imports: [FormsModule, RouterLink],
  templateUrl: './alumnos.html',
  styleUrl: './alumnos.css'
})
export class Alumnos implements OnInit {

  titulo = 'MiniERP Escolar';

  estadoSistema: any = {};

  alumnos: Alumno[] = [];

  formulario: AlumnoForm = this.formularioVacio();

  editandoId: number | null = null;

  cargando = false;
  guardando = false;

  mensaje = '';
  error = '';

  private alumnosService = inject(AlumnosService);

  private auth = inject(AuthService);

  private router = inject(Router);

  private http = inject(HttpClient);


  ngOnInit(): void {
    this.cargarAlumnos();
    this.cargarEstado();
  }

  formularioVacio(): AlumnoForm {
    return {
      Nctrl: '',
      nombre: '',
      promedio: 0,
      carrera: '',
      semestre: 1,
      sexo: ''
    };
  }

  cargarAlumnos(): void {

    this.cargando = true;
    this.error = '';

    this.alumnosService.obtenerAlumnos().subscribe({
      next: (datos) => {
        this.alumnos = datos;
        this.cargando = false;
      },
      error: (err) => {
        console.error(err);
        this.error = 'No fue posible obtener los alumnos.';
        this.cargando = false;
      }
    });

  }

  nuevoAlumno(): void {

    this.editandoId = null;
    this.formulario = this.formularioVacio();

    this.mensaje = '';
    this.error = '';

  }

  editarAlumno(alumno: Alumno): void {

    this.editandoId = alumno.id;

    this.formulario = {
      Nctrl: alumno.Nctrl,
      nombre: alumno.nombre,
      promedio: alumno.promedio,
      carrera: alumno.carrera,
      semestre: alumno.semestre,
      sexo: alumno.sexo
    };

    this.mensaje = '';
    this.error = '';

  }

  guardarAlumno(): void {

    this.mensaje = '';
    this.error = '';

    if (!this.formularioValido()) {
      this.error =
        'Complete correctamente todos los campos.';
      return;
    }

    this.guardando = true;

    if (this.editandoId === null) {

      this.alumnosService
        .crearAlumno(this.formulario)
        .subscribe({

          next: (respuesta) => {

            this.mensaje =
              `Alumno creado. ID: ${respuesta.id}`;

            this.guardando = false;

            this.nuevoAlumno();
            this.cargarAlumnos();

          },

          error: (err) => {

            console.error(err);

            this.error =
              'No fue posible crear el alumno.';

            this.guardando = false;

          }

        });

    } else {

      const id = this.editandoId;

      this.alumnosService
        .actualizarAlumno(id, this.formulario)
        .subscribe({

          next: () => {

            this.mensaje =
              'Alumno actualizado correctamente.';

            this.guardando = false;

            this.nuevoAlumno();
            this.cargarAlumnos();

          },

          error: (err) => {

            console.error(err);

            this.error =
              'No fue posible actualizar el alumno.';

            this.guardando = false;

          }

        });

    }

  }

  eliminarAlumno(alumno: Alumno): void {

    const confirmar = window.confirm(
      `¿Eliminar al alumno ${alumno.nombre}?`
    );

    if (!confirmar) {
      return;
    }

    this.mensaje = '';
    this.error = '';

    this.alumnosService
      .eliminarAlumno(alumno.id)
      .subscribe({

        next: () => {

          this.mensaje =
            'Alumno eliminado correctamente.';

          this.cargarAlumnos();

        },

        error: (err) => {

          console.error(err);

          this.error =
            'No fue posible eliminar el alumno.';

        }

      });

  }

  formularioValido(): boolean {

    return (
      this.formulario.Nctrl.trim().length > 0 &&
      this.formulario.nombre.trim().length > 0 &&
      this.formulario.promedio >= 0 &&
      this.formulario.promedio <= 10 &&
      this.formulario.carrera.trim().length > 0 &&
      this.formulario.semestre >= 1 &&
      this.formulario.semestre <= 20 &&
      this.formulario.sexo.trim().length > 0
    );

  }


cargarEstado(): void {

  this.http
    .get(
      'http://localhost:8081/api/health'
    )
    .subscribe({

      next: datos => {

        this.estadoSistema = datos;

      },

      error: error => {

        console.error(error);

      }

    });

}



cerrarSesion(): void {

  this.auth.logout();

  this.router.navigate(['/login']);

}

}
