@echo off
echo Menjalankan YukResto - Sistem Terdistribusi

start cmd /k "python server_main.py"
start cmd /k "python server_backup.py"
start cmd /k "python client_web.py"
start cmd /k "python worker1_web.py"
start cmd /k "python worker2_web.py"
start cmd /k "python worker3_web.py"

echo Semua komponen telah dijalankan!
pause
