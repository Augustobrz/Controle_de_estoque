# Controle de Estoque para Mercado

Aplicação desktop em Python para cadastrar e acompanhar produtos de um pequeno mercado. A interface foi baseada no layout solicitado: cabeçalho do mercado, pesquisa, tabela de produtos e ações de estoque.

## Funcionalidades

- Pesquisa instantânea por produto, categoria ou preço.
- Cadastro em formato ERP: código, código de barras, produto, categoria, fornecedor, preços de compra e venda, quantidade, estoque mínimo e datas de auditoria.
- Edição por botão **Editar** ou duplo clique na linha da tabela.
- Exclusão com confirmação.
- Salvamento automático e manual em banco de dados SQLite (`estoque.db`).
- Ordenação por produto, quantidade ou preço ao clicar no título da coluna.
- Seleção múltipla de produtos para exclusão em lote.
- Seleção múltipla de relatórios: categoria, preços, produtos, vendas, compras, lucro, entradas e saídas.
- Integração com leitor USB de código de barras para entrada rápida de estoque.
- Venda por peso: produtos `KG` calculam automaticamente o valor a partir do peso informado.
- Exportação de relatório em `relatorio_estoque.csv`, compatível com Excel.
- Cálculo do total de unidades exibido no rodapé.

## Categorias

O campo **Categoria** possui uma lista de 596 categorias de mercado, organizadas no arquivo `categorias.txt`. Basta começar a digitar: até cinco correspondências são exibidas imediatamente. Use as setas ↑/↓ e **Enter** para escolher sem usar o mouse, ou continue digitando uma categoria nova.

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
7. Para entrada pelo leitor USB, informe antes a **Qtd. entrada** (por exemplo, `12` para uma caixa fechada), deixe o cursor no campo **Leitor USB** e leia o código de barras. O produto é selecionado, recebe a quantidade informada e é salvo automaticamente. O campo volta para `1` após cada leitura.
8. Para carne e outros itens por peso, cadastre a **Unidade** como `KG` e use o preço de venda como valor por quilo. Informe o **Peso (kg)** medido (ex.: `0,750`), leia o código de barras e o sistema calcula o total da venda, baixa o peso do estoque e salva a operação.
9. Se uma leitura não for encontrada, escolha **Sim** na pergunta de cadastro. A tela de produto será aberta com o código de barras já preenchido.
10. Em **Relatório**, marque um ou mais tipos e clique em **Gerar selecionados**. Os arquivos são criados na pasta `relatorios_por_categoria`. Entradas e saídas passam a ser registradas a partir desta versão.

## Arquivos gerados

| Arquivo | Finalidade |
| --- | --- |
| `estoque.db` | Banco de dados SQLite local do estoque. |
| `estoque.json` | Arquivo legado, importado automaticamente apenas na primeira criação do banco. |
| `relatorio_estoque.csv` | Relatório exportado pelo botão **Relatório**. |

## Estrutura do projeto

```text
Controle_de_estoque/
├── main.py              # Interface e regras de negócio
├── requirements.txt     # Dependência Python
├── categorias.txt       # Categorias selecionáveis no cadastro
├── estoque.db           # Banco de dados SQLite (gerado pela aplicação)
├── relatorio_estoque.csv# Relatório (gerado pela aplicação)
└── img/logo_estoque.ico # Ícone original do projeto
```

## Dados iniciais

Na primeira execução, a aplicação apresenta Aveia, Cebola e Sabão em pó como exemplo. Os dados passam a ser persistidos após a primeira operação de salvamento.
