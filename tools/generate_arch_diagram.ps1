param(
    [string]$InputFile = "docs/project_architecture.mmd",
    [string]$OutputFile = "docs/project_architecture.png"
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$inputPath = Join-Path $repoRoot $InputFile
$outputPath = Join-Path $repoRoot $OutputFile

if (!(Test-Path $inputPath)) {
    throw "Input Mermaid file not found: $inputPath"
}

$outDir = Split-Path -Parent $outputPath
if (!(Test-Path $outDir)) {
    New-Item -ItemType Directory -Path $outDir | Out-Null
}

Write-Host "[INFO] Rendering Mermaid diagram..."
Write-Host "[INFO] Input : $inputPath"
Write-Host "[INFO] Output: $outputPath"

$configPath = Join-Path $repoRoot "docs/mermaid_theme.json"
if (!(Test-Path $configPath)) {
@'
{
  "theme": "base",
  "themeVariables": {
    "background": "#020817",
    "primaryColor": "#1F2020",
    "primaryTextColor": "#E5E7EB",
    "primaryBorderColor": "#A7A7A7",
    "lineColor": "#A7A7A7",
    "secondaryColor": "#1F2020",
    "tertiaryColor": "#1F2020"
  }
}
'@ | Set-Content -Path $configPath -Encoding ASCII
}

npx -y @mermaid-js/mermaid-cli -i $inputPath -o $outputPath -t dark -b "#020817" -c $configPath
if ($LASTEXITCODE -ne 0) {
    throw "Mermaid render failed with exit code $LASTEXITCODE"
}

Write-Host "[DONE] Diagram generated: $outputPath"
