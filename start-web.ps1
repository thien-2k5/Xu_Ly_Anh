$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

$envFile = Join-Path $root ".env"
if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        $line = $_.Trim()
        if (-not $line -or $line.StartsWith("#")) { return }
        $pair = $line -split "=", 2
        if ($pair.Count -eq 2) {
            $name = $pair[0].Trim()
            $value = $pair[1].Trim().Trim('"').Trim("'")
            Set-Item -Path "Env:$name" -Value $value
        }
    }
}

if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
    Write-Host "Missing .venv. Create it with: py -3.11 -m venv .venv"
    exit 1
}

$env:PYTHONPATH = "$root\src"
$env:FACETRUST_HOST = if ($env:FACETRUST_HOST) { $env:FACETRUST_HOST } else { "127.0.0.1" }
$env:FACETRUST_PORT = if ($env:FACETRUST_PORT) { $env:FACETRUST_PORT } else { "8000" }

.\.venv\Scripts\python.exe -m facetrust_benchmark.web --host $env:FACETRUST_HOST --port $env:FACETRUST_PORT
