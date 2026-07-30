# Controle de Estoque para Mercado

Aplicação desktop em Python para cadastrar e acompanhar produtos de um pequeno mercado. A interface foi baseada no layout solicitado: cabeçalho do mercado, pesquisa, tabela de produtos e ações de estoque.

## Funcionalidades

- Pesquisa instantânea por produto, categoria ou preço.
- Cadastro de produto com nome, quantidade, categoria selecionável e preço unitário.
- Edição por botão **Editar** ou duplo clique na linha da tabela.
- Exclusão com confirmação.
- Salvamento automático e manual em `estoque.json`.
- Exportação de relatório em `relatorio_estoque.csv`, compatível com Excel.
- Cálculo do total de unidades exibido no rodapé.

## Categorias

O campo **Categoria** possui uma lista selecionável com 596 categorias de mercado, organizadas no arquivo `categorias.txt`. Também é possível digitar um novo nome diretamente no campo quando uma categoria específica não constar na lista.

## Requisitos

- Python 3.10 ou superior.
- Biblioteca `customtkinter`.

## Instalação e execução

No terminal, dentro da pasta do projeto, instale a dependência:

```powershell
python -m pip install -r requirements.txt
```

Inicie a aplicação:

```powershell
python main.py
```

## Como usar

1. Clique em **Adicionar**, preencha os quatro campos e confirme em **Salvar produto**.
2. Para alterar um registro, selecione a linha e use **Editar** ou dê duplo clique nela.
3. Para remover, selecione o produto, clique em **Excluir** e confirme.
4. Use o campo de busca para filtrar os produtos em tempo real.
5. Clique em **Relatório** para criar uma planilha CSV com preço unitário e valor total por item.
6. Clique em **Salvar** para persistir imediatamente; os dados também são gravados ao adicionar, editar, excluir ou sair.

## Arquivos gerados

| Arquivo | Finalidade |
| --- | --- |
| `estoque.json` | Banco de dados local do estoque. É criado no primeiro salvamento. |
| `relatorio_estoque.csv` | Relatório exportado pelo botão **Relatório**. |

## Estrutura do projeto

```text
Controle_de_estoque/
├── main.py              # Interface e regras de negócio
├── requirements.txt     # Dependência Python
├── categorias.txt       # Categorias selecionáveis no cadastro
├── estoque.json         # Dados locais (gerado pela aplicação)
├── relatorio_estoque.csv# Relatório (gerado pela aplicação)
└── img/logo_estoque.ico # Ícone original do projeto
```

## Dados iniciais

Na primeira execução, a aplicação apresenta Aveia, Cebola e Sabão em pó como exemplo. Os dados passam a ser persistidos após a primeira operação de salvamento.
