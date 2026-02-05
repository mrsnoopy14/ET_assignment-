# Runs an end-to-end demo locally:
# - Starts the Python Flask solver (port 5000)
# - Starts the Node forwarding service (port 3000)
# - Calls Node endpoints and writes JSON outputs to out/
# - Stops both processes

$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $repoRoot

$outDir = Join-Path $repoRoot 'out'
New-Item -ItemType Directory -Force $outDir | Out-Null

function Wait-HttpOk {
  param(
    [Parameter(Mandatory=$true)][string]$Url,
    [int]$TimeoutSeconds = 30
  )

  $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
  while ((Get-Date) -lt $deadline) {
    try {
      $null = Invoke-RestMethod -Uri $Url -Method Get -TimeoutSec 2
      return
    } catch {
      Start-Sleep -Milliseconds 300
    }
  }
  throw "Timed out waiting for: $Url"
}

# Find Python interpreter (prefer local venv)
$pythonExe = Join-Path $repoRoot '.venv\Scripts\python.exe'
if (-not (Test-Path $pythonExe)) {
  $pythonExe = 'python'
}

$flaskLogOut = Join-Path $outDir 'flask_stdout.log'
$flaskLogErr = Join-Path $outDir 'flask_stderr.log'
$nodeLogOut  = Join-Path $outDir 'node_stdout.log'
$nodeLogErr  = Join-Path $outDir 'node_stderr.log'

$flask = $null
$node = $null

try {
  # Start Flask
  $env:HOST = '127.0.0.1'
  $env:PORT = '5000'
  $env:FLASK_DEBUG = '0'

  $flask = Start-Process -FilePath $pythonExe -ArgumentList @('-u', 'src/app.py') -WorkingDirectory $repoRoot -PassThru -RedirectStandardOutput $flaskLogOut -RedirectStandardError $flaskLogErr
  Wait-HttpOk -Url 'http://127.0.0.1:5000/' -TimeoutSeconds 30

  # Start Node
  $env:SOLVER_URL = 'http://127.0.0.1:5000/thermal'
  $env:HOST = '127.0.0.1'
  $env:PORT = '3000'

  $node = Start-Process -FilePath 'node' -ArgumentList @('server.js') -WorkingDirectory $repoRoot -PassThru -RedirectStandardOutput $nodeLogOut -RedirectStandardError $nodeLogErr
  Wait-HttpOk -Url 'http://127.0.0.1:3000/' -TimeoutSeconds 30

  # Call Node endpoints and write outputs
  $default = Invoke-RestMethod -Uri 'http://127.0.0.1:3000/solve/default' -Method Get
  $default | ConvertTo-Json -Depth 20 | Set-Content -Path (Join-Path $outDir 'node_demo_default.json') -Encoding utf8

  $body = Get-Content (Join-Path $repoRoot 'node-service\sample_request.json') -Raw
  $post = Invoke-RestMethod -Uri 'http://127.0.0.1:3000/solve' -Method Post -ContentType 'application/json' -Body $body
  $post | ConvertTo-Json -Depth 20 | Set-Content -Path (Join-Path $outDir 'node_demo_post.json') -Encoding utf8

  Write-Host 'OK. Wrote:'
  Write-Host ' - out\node_demo_default.json'
  Write-Host ' - out\node_demo_post.json'
  Write-Host 'Logs:'
  Write-Host ' - out\flask_stdout.log / out\flask_stderr.log'
  Write-Host ' - out\node_stdout.log / out\node_stderr.log'
}
finally {
  if ($node -and -not $node.HasExited) {
    Stop-Process -Id $node.Id -Force -ErrorAction SilentlyContinue
  }
  if ($flask -and -not $flask.HasExited) {
    Stop-Process -Id $flask.Id -Force -ErrorAction SilentlyContinue
  }
}
