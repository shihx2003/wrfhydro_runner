#!/bin/bash

NUM_PROCS=4
WRF_HYDRO_EXE="./wrf_hydro.exe"
LOGFILE="wrf_hydro.log"

if [[ ! -f "$WRF_HYDRO_EXE" ]]; then
    echo "Error: Can Not Find $WRF_HYDRO_EXE！Please Check The EXE Path" | tee -a "$LOGFILE"
    exit 1
fi
echo "Run WRF-Hydro，Use $NUM_PROCS Core..." | tee -a "$LOGFILE"
nohup mpirun -np "$NUM_PROCS" "$WRF_HYDRO_EXE" >> "$LOGFILE" 2>&1 &
echo $! > wrf_hydro.pid
