# FuzzItAll (command line tool)

Command line tool to run grey-box fuzzing engines on an HPC system. This tool acts as a backend to the FuzzItAll service.

## Getting Started

These instructions will get you a copy of the project up and running on your target HPC system for execution or testing purposes.

### Prerequisites

The project requires a Linux HPC system with the following software installed:

* Bash
* Slurm Workload Manager
* LLVM 12.1.0+ and/or gcc 9.2.0+

Additionally, the system must have a **scratch space** available for the tool to perform fuzzing tasks and dump their results.

### Deployment

The project includes a script file (see [deploy](deploy)) to facilitate the deployment of the tool. That being said, once the project has been transferred to the target frontend of the HPC system, first you must access it and assign execution permissions to the script file:

```
cd /path/to/cli_tool && chmod +x deploy
```

After that, you must configure the job descriptor file (see [slurm.conf](slurm.conf)) to suit your needs (e.g. whether or not you wish to receive e-mail notifications of submitted jobs) and those of the HPC system (e.g. indicate the minimum and maximum number of nodes to use, the partition within the cluster and the modules to be loaded corresponding to LLVM and/or gcc):

```
vi slurm.conf
```

Finally, simply run the script indicating both the path to the deployment directory (with the `-d` option) and the path to the user's scratch directory (with the `-s` option):

```
./deploy -d /path/to/target_directory -s /path/to/scratch_directory
```

The script will guide you through the entire deployment process. Among other tasks, this process will compile the fuzzing engines (fuzzers) available within the [external](external) directory. Furthermore, the script will create two environment variables: `FIA_ROOT` (path to the directory where the tool is deployed) and `FIA_WORKSPACE` (path to the directory where fuzzing projects are stored and processed).

## Running

The tool is launched via the [fuzzitall](fuzzitall) script file. For its execution, it is necessary to specify two options: *1)* a path to the project containing the fuzz target (with the `-p` option) and *2)* the name of the fuzzing engine to be used (with the `-f` option). Optionally, it is possible to indicate the number of parallel fuzzing tasks to be launched (using the `-n` option). Please note that these tasks are executed using Slurm's feature of array jobs and its maximum value depends on the variable `FIA_MAX_PARALLEL_TASKS` (which is stored in the `FIA.config` file). Having said that, the command to launch the tool is:

```
./fuzzitall -p /path/to/project_directory -f name_of_fuzzing_engine [-n number_of_parallel_fuzzing_tasks]
```

The output of the tool consists of an identifier corresponding to the Slurm job assigned to perform fuzzing tasks. For instance, when executing the command:

```
./fuzzitall -p $FIA_WORKSPACE/example-project -f AFL++ -n 2
```

Its output will be:

```
0000001
```

You can check the status of the job and its related tasks using the Slurm `squeue` command:

```
squeue -j 0000001
```

Which output should look like this:

```
JOBID       PARTITION   NAME    USER        ST  TIME    NODES   NODELIST(REASON)
0000001_0   part_name   FuzzItA hpc_user    R   0:01    1       node_no
0000001_1   part_name   FuzzItA hpc_user    R   0:01    1       node_no
0000001_2   part_name   FuzzItA hpc_user    R   0:01    1       node_no
```

In addition, log files associated with the Slurm job are stored in the `log` directory and follow the "`FuzzItAll-<project_name>-<fuzzing_step>_<slurm_job_id>.<extension>`" convention, where:

* `<project_name>`. Name of the project.
* `<fuzzing_step>`. Step executed within the fuzzing pipeline. This could be *Instrumentation* or *Fuzzing*.
* `<slurm_job_id>`. Slurm job identifier responsible for running the *fuzzing step*.
* `<extension>`. Whether the content of the log corresponds to the standard output (`.out`) or to the error output (`.err`).

## Displaying results

The fuzzer output is stored within the project itself in a directory called `fuzz-out`; although it should be noted that its content depends on the type of fuzzing engine used. The tool has a utility to display the fuzzing results through the [monitor-fuzzing](core/utils/monitor-fuzzing) script file. This script needs to specify two parameters for its execution: *1)* a path to the project on which fuzzing has been applied (with the `-p` option) and *2)* the name of the fuzzing engine used (with the `-f` option):

```
./utils/monitor-fuzzing -p $FIA_WORKSPACE/example-project -f AFL++
```

The output of this utility will depend on the fuzzing engine used but it shall contain all data related to crashes or hangs detected during the execution of the fuzzing tasks.

## FuzzItAll project convention

To perform fuzzing tasks on a project, a specific convention must be complied with. Any FuzzItAll project has the following structure:

    .
    ├── src/                    # Source code of the project
    │   └── fia_project.conf    # FuzzItAll project configuration
    └── fuzz_out/               # Fuzzers output

Inside the `src` directory, besides the source code it is mandatory to include a configuration file (named `fia_project.conf`) that defines three variables:

1. *FIA_BUILD_CMD* - Command or list of commands (separated by semicolons) used to build the project source code to generate the fuzz target. Whenever possible, you should always configure the project to build the target statically and not dynamically (e.g. using the *--disable-shared* flag).
2. *FIA_FUZZ_TARGET* - Output binary on which fuzzing is to be applied.
3. *FIA_TESTCASE_DIR* - Directory containing the seed corpus to test the fuzz target.

In addition, the `FIA_TESTCASE_DIR` directory must be contained within `src` and must include all input files to be used as test cases. On the other hand, the `fuzz_out` directory stores the output of the fuzzers during and after their execution. The output contains data about the crashes and hangs found and its format will depend on the selected fuzzer.

Finally, a list of sample projects adapted to FuzzItAll can be found at https://niebla.unileon.es/securecoding/misc/fuzzitall-examples.

## Built With

* [Slurm](https://slurm.schedmd.com/) - Resource manager and job scheduling system.
* [Bash](https://www.gnu.org/software/bash/) - Command-line interpreter.
* [AFL++](https://aflplus.plus/) - Fuzzing engine.

## Credits

See parent [README.md](../README.md) file.
