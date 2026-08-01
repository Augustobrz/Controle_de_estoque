INSTALLER_README - Como gerar o instalador NSIS

O repositório já contém um script NSIS (installer.nsi) e um helper PowerShell (build_installer.ps1) para gerar um instalador Windows (.exe).

Pré-requisitos:
- NSIS (makensis) instalado: https://nsis.sourceforge.io/Download
- A pasta 'release' deve existir e conter pelo menos 'Controle_de_estoque.exe' (gerado pelo PyInstaller) e, opcionalmente, arquivos de dados (estoque.db, categorias.txt etc.).

Passos:
1. Gere o executável com PyInstaller (se ainda não gerou):
   python -m PyInstaller --onefile --noconsole --name Controle_de_estoque main.py
   copie o dist\Controle_de_estoque.exe para a pasta 'release' do repositório.

2. Abra PowerShell na raiz do repositório e execute (com privilégios de usuário):
   .\build_installer.ps1

3. Se makensis estiver no PATH, o script chamará makensis installer.nsi e criará:
   release\Controle_de_estoque_installer.exe

4. Teste o instalador em máquina de teste antes de distribuir.

Notas:
- O instalador instala no diretório padrão do Programa (Program Files) e cria atalhos no menu Iniciar e no desktop.
- Para personalizar o que é instalado (por exemplo excluir relatorio_estoque.csv), edite installer.nsi.
- Se houver problemas com permissões, execute o PowerShell como Administrador.

Desenvolvedor: Augusto da Costa Pires
