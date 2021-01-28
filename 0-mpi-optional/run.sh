#!/usr/bin/env bash

set -e

printf "\n### Part a\n"
cmd="python ex0-a-nompi.py"
printf "> $cmd\n"
$cmd

printf "\n### Part b\n"
cmd="mpiexec -n 2 python ex0-b-mpi.py"
printf "> $cmd\n"
$cmd

printf "\n### Part c\n"
cmd="python ex0-c-mpioptional.py"
printf "> $cmd\n"
$cmd

printf "\n"
cmd="mpiexec -n 2 python ex0-c-mpioptional.py --mpi"
printf "> $cmd\n"
$cmd

