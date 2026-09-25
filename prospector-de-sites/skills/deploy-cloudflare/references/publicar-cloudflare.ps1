# Prospector de Sites — Despliegue Automatizado a Cloudflare (Workers con Static Assets)
param([switch]$Auto)
$ErrorActionPreference = "Stop"
$pasta = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $pasta

function Fim($code){ if(-not $Auto){ pause }; exit $code }
function Log($msg,$cor="Gray"){
  $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
  if($Auto){ Add-Content "publicador-log.txt" "[$ts] $msg" }
  else { Write-Host "[$ts] $msg" -ForegroundColor $cor }
}

Log "Iniciando despliegue hacia Cloudflare..." "Cyan"

# 1. Cargar configuracion
$cfgFile = "prospector-config.json"
if (-not (Test-Path $cfgFile)) {
  Log "AVISO: $cfgFile no encontrado. Usando variables de entorno o defaults." "Yellow"
  $cfg = @{}
} else {
  try { $cfg = Get-Content $cfgFile -Raw -Encoding UTF8 | ConvertFrom-Json }
  catch { Log "ERROR: $cfgFile corrupto." "Red"; Fim 1 }
}

$cf = $cfg.cloudflare
$token = if ($cf.apiToken) { $cf.apiToken } else { $env:CLOUDFLARE_API_TOKEN }
$accountId = if ($cf.accountId) { $cf.accountId } else { $env:CLOUDFLARE_ACCOUNT_ID }
$projName = if ($cf.projectName) { $cf.projectName } else { "prospector-sites" }

if (-not $token) {
  Log "ERROR: Falta el CLOUDFLARE_API_TOKEN en prospector-config.json o entorno." "Red"
  Fim 1
}

# 2. Configurar entorno para wrangler
$env:CLOUDFLARE_API_TOKEN = $token
if ($accountId) { $env:CLOUDFLARE_ACCOUNT_ID = $accountId }
$env:PATH = $env:PATH.Replace('"', '')

# Asegurar carpeta sites
if (-not (Test-Path "sites")) {
  New-Item -ItemType Directory -Path "sites" | Out-Null
  Set-Content "sites/index.html" "<!DOCTYPE html><html><head><title>Prospector Demos</title></head><body><h1>Prospector Landing Pages</h1></body></html>" -Encoding UTF8
}

# 3. Asegurar wrangler.jsonc
if (-not (Test-Path "wrangler.jsonc")) {
  $tpl = Get-Content "prospector-de-sites/skills/deploy-cloudflare/references/wrangler.template.jsonc" -Raw -Encoding UTF8
  $tpl = $tpl -replace '"prospector-sites"', ('"' + $projName + '"')
  Set-Content "wrangler.jsonc" $tpl -Encoding UTF8
}

# 4. Desplegar con Wrangler
Log "Ejecutando wrangler deploy para la carpeta ./sites..." "Green"
try {
  $output = & wrangler deploy 2>&1
  $outputStr = $output -join "`n"
  Log $outputStr "Gray"
  
  if ($LASTEXITCODE -eq 0) {
    Log "Despliegue a Cloudflare completado con éxito." "Green"
    # Extraer URL si existe
    if ($outputStr -match "https://[a-zA-Z0-9.-]+\.workers\.dev") {
      $liveUrl = $matches[0]
      Log "URL Base Activa: $liveUrl" "Cyan"
    }
  } else {
    Log "Fallo en wrangler deploy (codigo $LASTEXITCODE)" "Red"
    Fim 1
  }
} catch {
  Log "Excepción durante wrangler deploy: $_" "Red"
  Fim 1
}

Fim 0
