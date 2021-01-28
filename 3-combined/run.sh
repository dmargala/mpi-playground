#!/usr/bin/env bash

set -e

printf "\n### Part a\n"
cmd="python ex3-combined.py"
printf "> $cmd\n"
$cmd

printf "\n"
cmd="mpiexec -n 2 python ex3-combined.py --mpi"
printf "> $cmd\n"
$cmd

printf "\n"
cmd="mpiexec -n 2 python ex3-combined.py --mpi --trigger-one"
printf "> $cmd\n"
$cmd

printf "\n"
cmd="mpiexec -n 2 python ex3-combined.py --mpi --trigger-two"
printf "> $cmd\n"
$cmd

printf "\n"
cmd="mpiexec -n 2 python ex3-combined.py --mpi --trigger-three"
printf "> $cmd\n"
$cmd

printf "\n"
cmd="mpiexec -n 4 python ex3-combined.py --mpi --async-io"
printf "> $cmd\n"
$cmd

printf "\n"
cmd="mpiexec -n 4 python ex3-combined.py --mpi --async-io --trigger-one"
printf "> $cmd\n"
$cmd

printf "\n"
cmd="mpiexec -n 4 python ex3-combined.py --mpi --async-io --trigger-two"
printf "> $cmd\n"
$cmd

printf "\n"
cmd="mpiexec -n 4 python ex3-combined.py --mpi --async-io --trigger-three"
printf "> $cmd\n"
$cmd

