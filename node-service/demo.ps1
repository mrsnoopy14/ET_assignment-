# Demo script for screenshots:
# - Assumes Flask is running at http://127.0.0.1:5000
# - Assumes Node service is running at http://127.0.0.1:3000

New-Item -ItemType Directory -Force ..\out | Out-Null

$default = Invoke-RestMethod -Uri 'http://127.0.0.1:3000/solve/default' -Method Get
$defaultJson = $default | ConvertTo-Json -Depth 10
Set-Content -Path '..\out\node_demo_default.json' -Value $defaultJson -Encoding utf8

$body = Get-Content '.\sample_request.json' -Raw
$post = Invoke-RestMethod -Uri 'http://127.0.0.1:3000/solve' -Method Post -ContentType 'application/json' -Body $body
$postJson = $post | ConvertTo-Json -Depth 10
Set-Content -Path '..\out\node_demo_post.json' -Value $postJson -Encoding utf8

Write-Host 'Wrote:'
Write-Host ' - out\node_demo_default.json'
Write-Host ' - out\node_demo_post.json'
