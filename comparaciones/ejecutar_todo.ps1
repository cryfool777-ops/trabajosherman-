# Compila y ejecuta los 5 benchmarks y, al final, genera el reporte con gestor.py.
# Uso: powershell -ExecutionPolicy Bypass -File .\ejecutar_todo.ps1

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location $root

function Assert-LastExitCode {
    param([string]$Step)
    if ($LASTEXITCODE -ne 0) {
        throw "Fallo en: $Step (codigo de salida $LASTEXITCODE)"
    }
}

$total = [System.Diagnostics.Stopwatch]::StartNew()

try {
    Write-Host "=== 1/6 Compilando C# (Release) ==="
    dotnet build "csharp\sorting.csproj" -c Release --nologo
    Assert-LastExitCode "dotnet build"

    Write-Host "=== 2/6 Ejecutando C# ==="
    dotnet "csharp\bin\Release\net10.0\Sorting.dll"
    Assert-LastExitCode "C#"

    Write-Host "=== 3/6 Compilando y ejecutando C++ (-O2) ==="
    g++ -O2 -std=c++17 -o sorting_cpp.exe sorting.cpp
    Assert-LastExitCode "g++"
    .\sorting_cpp.exe
    Assert-LastExitCode "C++"

    Write-Host "=== 4/6 Compilando y ejecutando Java ==="
    javac -encoding UTF-8 Sorting.java
    Assert-LastExitCode "javac"
    java Sorting
    Assert-LastExitCode "Java"

    Write-Host "=== 5/6 Ejecutando Python y JavaScript ==="
    python sorting.py
    Assert-LastExitCode "Python"
    node sorting.js
    Assert-LastExitCode "JavaScript"

    Write-Host "=== 6/6 Generando reporte con gestor.py ==="
    python gestor.py
    Assert-LastExitCode "gestor.py"

    $total.Stop()
    Write-Host ("Tiempo total: {0:N1} s" -f $total.Elapsed.TotalSeconds)
}
finally {
    Pop-Location
}
