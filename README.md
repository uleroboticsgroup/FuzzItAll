# FuzzItAll

A service to ease the process of fuzzing and instrumenting binaries using the capabilities of a High-Performance Computing Enviroment (HPCE).

## Overview

### Organization

The project is organized as follows:

    .
    ├── core/                    # Core tool
    │   ├── slurm/                  # Slurm scripts to run jobs related to the fuzzing process
    │   ├── utils/                  # Utilities scripts
    │   ├── FIA.config/             # Main configuration file
    │   └── fuzzitall/              # Main executable script
    ├── external/                # External fuzzing tools
    │   └── AFL++/                  # [AFL++](https://aflplus.plus/)
    ├── web_service/             # Web server for end users to run FuzzItAll
    ├── setup.sh                 # Deployment script
    └── README.md

There are two main components: core tool and web service

#### Core tool

The core tool consists in a set of bash and Slurm scripts that runs a general fuzzing pipeline: 1) prepare the source code for binary instrumentation; and 2) fuzz the output binary using parallel jobs.

The tool relies on a configuration file named `FIA.config` that contains a list of general purpose variables and paths.

#### Web service

> Under construction :-)

The web service is written in Python using [Flask](https://flask.palletsprojects.com/en/2.0.x/) and [JWT](https://pyjwt.readthedocs.io/en/stable/). This service allow end users:

* Provide a database of authenticated users.
* Run fuzzing jobs in an HPCE.
* Check their status and download the results.

### Installation

#### Core tool

An installation script (`setup.sh`) is provided to deploy FuzzItAll core tool. Its usage is:

```bash
bash setup.sh <installationDir>
```

This process will copy the core tool to a target directory (`installationDir`), initialize the main configuration file (`FIA.config`) and build all available fuzzers.

#### Web service

> Under construction :-)

## Usage

### Core tool

Running the tool is as simple as typing the command:

```bash
./fuzzitall <source_code_directory>
```

This will automatically create a copy of the repository stored in `source_code_directory`, prepare the source code for binary instrumentation and finally run the fuzzing process in a distributed way over the output binary.

To successfully run the tool, `source_code_directory` must include a configuration file named `conf.conf`. This file defines three variables:

1. *compilation_file*: script file to build the project
2. *run*: command to run the output binary
3. *corpus_path*: directory containing the corpus to test the output binary

An example repository for testing purposes can be fount at https://niebla.unileon.es/DavidFerng/test-fuzz

### Web service

> Under construction :-)

## Credits

FuzzItAll is licensed under [MIT license](https://choosealicense.com/licenses/mit/). It has been funded by the Addendum no. 4 to the Universidad de León-Instituto Nacional de Ciberseguridad (INCIBE) Convention Framework on the "Detection of new threats and unknown patterns" and was originally designed and developed by the following people:

* David Fernández
* Gonzalo Esteban
* Francisco Borja Garnelo