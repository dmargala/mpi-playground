#!/usr/bin/env bash

set -e

printf "\n### Part a\n"
cmd="python ex1-a-unsafe.py"
printf "> $cmd\n"
$cmd

printf "\n"
cmd="mpiexec -n 2 python ex1-a-unsafe.py --mpi"
printf "> $cmd\n"
$cmd

printf "\n"
cmd="python ex1-a-unsafe.py --trigger-one"
printf "> $cmd\n"
$cmd

printf "\n"
cmd="mpiexec -n 2 python ex1-a-unsafe.py --trigger-one --mpi"
printf "> $cmd\n" 
$cmd &
PID=$!
sleep 2
printf "^C\n"
kill $PID

printf "\n### Part b\n"
cmd="mpiexec -n 2 python ex1-b-safe.py --trigger-one --mpi"
printf "> $cmd\n"
$cmd

printf "\n### Part c\n"
cmd="mpiexec -n 2 python ex1-c-safe-again.py --trigger-one --mpi"
printf "> $cmd\n"
$cmd

