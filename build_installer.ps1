# build_installer.ps1
# Executa o makensis para gerar o instalador a partir de installer.nsi
# Requisitos: NSIS (makensis) instalado e disponível no PATH. A pasta 'release' deve conter os arquivos a incluir.

$script = Join-Path $PSScriptRoot 'installer.nsi'
$release = Join-Path $PSScriptRoot 'release'

if (-not (Test-Path $script)) {
    Write-Error "Não encontrei installer.nsi. Execute este script a partir da raiz do repositório."
    exit 1
}
if (-not (Test-Path $release)) {
    Write-Error "Pasta 'release' não existe. Gere o build onefile (PyInstaller) primeiro e confirme que release\\Controle_de_estoque.exe está presente."
    exit 1
}

$makensis = Get-Command makensis -ErrorAction SilentlyContinue
if (-not $makensis) {
    Write-Host "makensis não encontrado. Instale NSIS: https://nsis.sourceforge.io/Download e adicione makensis ao PATH."
    exit 1
}

# Executa o compilador NSIS
& $makensis.Path $script

# Verifica resultado
$installer = Join-Path $PSScriptRoot 'release\\Controle_de_estoque_installer.exe'
if (Test-Path $installer) {
    Write-Host "Instalador gerado: $installer"
} else {
    Write-Error "Falha ao gerar o instalador. Verifique a saída do makensis acima para mensagens de erro."
}
