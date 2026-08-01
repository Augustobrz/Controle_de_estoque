!include "MUI2.nsh"

Name "Controle de Estoque"
OutFile "release\\Controle_de_estoque_installer.exe"
InstallDir "$PROGRAMFILES\\Controle de Estoque"
RequestExecutionLevel admin

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_INSTFILES

Section "Instalar"
    SetOutPath "$INSTDIR"
    ; Inclui todo o conteúdo da pasta release (executável + dados)
    File /r "release\\*.*"

    ; Atalhos
    CreateDirectory "$SMPROGRAMS\\Controle de Estoque"
    CreateShortCut "$SMPROGRAMS\\Controle de Estoque\\Controle de Estoque.lnk" "$INSTDIR\\Controle_de_estoque.exe"
    CreateShortCut "$DESKTOP\\Controle de Estoque.lnk" "$INSTDIR\\Controle_de_estoque.exe"

    ; Uninstaller
    WriteUninstaller "$INSTDIR\\Uninstall.exe"
SectionEnd

Section "Desinstalar"
    ; Remover atalhos e arquivos criados
    Delete "$DESKTOP\\Controle de Estoque.lnk"
    Delete "$SMPROGRAMS\\Controle de Estoque\\Controle de Estoque.lnk"
    RMDir "$SMPROGRAMS\\Controle de Estoque"

    ; Remover arquivos e pasta de instalação
    Delete "$INSTDIR\\Controle_de_estoque.exe"
    Delete "$INSTDIR\\Uninstall.exe"
    ; Remover recursivamente a pasta de instalação
    RMDir /r "$INSTDIR"
SectionEnd
