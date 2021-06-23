# The fuzzer

## Estructura del fuzzer

El fuzzer consta de un único script: `fuzzitall.sh`. Este es el encargado de lanzar todos los trabajos asociados a un proyecto. Recibe dos variables: el nombre del proyecto y enlace al repositorio.

El fuzzer requiere que el repositorio contenga 1 fichero:

* `conf.conf`:
    * compilation_file: script para compilar el proyecto
    * run: linea para ejecutar el proyecto
    * corpus_path: el directorio donde se encuentra el corpus

Para que el fuzzer pueda descargarse el proyecto es necesario añadir el usuario del Fuzzer al proyecto en gitlab.

Hay un fichero que contiene la configuración general denominado  `HS.conf`. Este contiene las rutas del AFL, numero de slaves para los trabajos, etc.

Hay un repositorio de ejemplo para probar la ejecucion: 
https://niebla.unileon.es/DavidFerng/test-fuzz

Para ejecutar este seria:

`./fuzzitall.sh TestJob1 ssh://git@niebla.unileon.es:5022/DavidFerng/test-fuzz.git`

## Web server

La carpeta `servr` contiene el codigo del servidor web desde el que poder lanzar jobs, ver el estado y descargarse resultados.

Es un servidor Flask (Python) con un index.html sencillo como front. Utiliza JWT para la autenticación de usuarios.

Está en fase beta y es extremadamente esquemático.

## Slurm

Actualmente hay un Slurm activo en Yogui, desplegado en dockers. Accediendo al interior de `slurmctld` está el repositorio del fuzzer, el AFL y todo. 

Desde ahi podeis hacer pruebas.



