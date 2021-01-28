#!/usr/bin/env bash

set -e

printf "\n### Part a\n"
cmd="python ex2-a-refactor.py"
printf "> $cmd\n"
$cmd

printf "\n"
cmd="mpiexec -n 2 ex2-a-refactor.py --mpi"
printf "> $cmd\n"
$cmd

printf "\n### b\n"
cmd="python ex2-b-async.py"
printf "> $cmd\n"
$cmd

printf "\n"
cmd="mpiexec -n 2 python ex2-b-async.py --mpi"
printf "> $cmd\n"
$cmd

printf "\n"
cmd="mpiexec -n 4 python ex2-b-async.py --mpi --async-io"
printf "> $cmd\n"
$cmd

printf "\n### c\n"
cmd="python ex2-c-async-again.py"
printf "> $cmd\n"
$cmd

printf "\n"
cmd="mpiexec -n 2 python ex2-c-async-again.py --mpi"
printf "> $cmd\n"
$cmd

printf "\n"
cmd="mpiexec -n 4 python ex2-c-async-again.py --mpi --async-io"
printf "> $cmd\n"
$cmd

