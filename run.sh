#!/usr/bin/env bash

set -e

printf "\n### Example 1\n"
cmd="python ex1-unsafe.py"
printf "> $cmd\n"
$cmd

printf "\n"
cmd="mpiexec -n 2 python ex1-unsafe.py --mpi"
printf "> $cmd\n"
$cmd

printf "\n"
cmd="python ex1-unsafe.py --trigger-one"
printf "> $cmd\n"
$cmd

printf "\n"
cmd="mpiexec -n 2 python ex1-unsafe.py --trigger-one --mpi"
printf "> $cmd\n" 
$cmd &
PID=$!
sleep 2
printf "^C\n"
kill $PID

printf "\n### Example 2\n"
cmd="mpiexec -n 2 python ex2-safe.py --trigger-one --mpi"
printf "> $cmd\n"
$cmd

printf "\n### Example 3\n"
cmd="mpiexec -n 2 python ex3-mpi4dummies.py --trigger-one --mpi"
printf "> $cmd\n"
$cmd

