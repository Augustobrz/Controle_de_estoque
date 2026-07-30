"""Aplicação desktop para controle de estoque de um mercado."""

from __future__ import annotations

import csv
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from tkinter import messagebox, ttk
import customtkinter as ctk


ARQUIVO_ESTOQUE = Path(__file__).with_name("estoque.json")
BANCO_DADOS = Path(__file__).with_name("estoque.db")
ARQUIVO_RELATORIO = Path(__file__).with_name("relatorio_estoque.csv")
PASTA_RELATORIOS = Path(__file__).with_name("relatorios_por_categoria")
ARQUIVO_CATEGORIAS = Path(__file__).with_name("categorias.txt")
DADOS_INICIAIS = [
    {"codigo": "P0001", "codigo_barras": "", "produto": "Aveia", "categoria": "Alimentos", "fornecedor": "", "unidade": "UN", "preco_compra": 0, "preco_venda": 8.50, "quantidade": 10, "estoque_minimo": 0, "data_cadastro": "", "ultima_alteracao": ""},
    {"codigo": "P0002", "codigo_barras": "", "produto": "Cebola", "categoria": "Hortifruti", "fornecedor": "", "unidade": "UN", "preco_compra": 0, "preco_venda": 4.20, "quantidade": 15, "estoque_minimo": 0, "data_cadastro": "", "ultima_alteracao": ""},
    {"codigo": "P0003", "codigo_barras": "", "produto": "Sabão em pó", "categoria": "Limpeza", "fornecedor": "", "unidade": "UN", "preco_compra": 0, "preco_venda": 22.90, "quantidade": 3, "estoque_minimo": 0, "data_cadastro": "", "ultima_alteracao": ""},
]


class ControleEstoque(ctk.CTk):
    """Janela principal e operações de estoque."""

    def __init__(self) -> None:
        super().__init__()
        self.produtos = self.carregar_estoque()
        self.categorias = self.carregar_categorias()
        self.indice_em_edicao: int | None = None
        self.coluna_ordenacao = "produto"
        self.ordem_reversa = False

        self.title("Controle de Estoque | Mercado")
        self.geometry("1000x630")
        self.minsize(850, 520)
        self.configure(fg_color="#f3f6f8")
        self.protocol("WM_DELETE_WINDOW", self.sair)
        self.criar_interface()
        self.atualizar_tabela()

    def carregar_estoque(self) -> list[dict]:
        """Carrega o estoque do SQLite e migra o arquivo JSON legado, se houver."""
        try:
            with sqlite3.connect(BANCO_DADOS) as conexao:
                conexao.execute("""CREATE TABLE IF NOT EXISTS produtos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, codigo TEXT NOT NULL DEFAULT '', codigo_barras TEXT NOT NULL DEFAULT '',
                    produto TEXT NOT NULL, categoria TEXT NOT NULL, fornecedor TEXT NOT NULL DEFAULT '', unidade TEXT NOT NULL DEFAULT 'UN', preco REAL NOT NULL DEFAULT 0,
                    preco_compra REAL NOT NULL DEFAULT 0, preco_venda REAL NOT NULL DEFAULT 0, quantidade INTEGER NOT NULL,
                    estoque_minimo INTEGER NOT NULL DEFAULT 0, data_cadastro TEXT NOT NULL DEFAULT '', ultima_alteracao TEXT NOT NULL DEFAULT '')""")
                conexao.execute("""CREATE TABLE IF NOT EXISTS movimentos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, tipo TEXT NOT NULL, codigo TEXT NOT NULL,
                    produto TEXT NOT NULL, quantidade REAL NOT NULL, valor REAL NOT NULL DEFAULT 0,
                    data_movimento TEXT NOT NULL, observacao TEXT NOT NULL DEFAULT '')""")
                self.atualizar_estrutura_banco(conexao)
                registros = conexao.execute(
                    "SELECT codigo, codigo_barras, produto, categoria, fornecedor, unidade, preco_compra, preco_venda, quantidade, estoque_minimo, data_cadastro, ultima_alteracao FROM produtos ORDER BY id"
                ).fetchall()
                if registros:
                    return [
                        dict(zip(("codigo", "codigo_barras", "produto", "categoria", "fornecedor", "unidade", "preco_compra", "preco_venda", "quantidade", "estoque_minimo", "data_cadastro", "ultima_alteracao"), registro))
                        for registro in registros
                    ]
                dados = self.carregar_json_legado()
                conexao.executemany(
                    "INSERT INTO produtos (codigo, codigo_barras, produto, categoria, fornecedor, unidade, preco, preco_compra, preco_venda, quantidade, estoque_minimo, data_cadastro, ultima_alteracao) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    [self.valores_banco(item, posicao) for posicao, item in enumerate(dados, 1)],
                )
                return dados
        except sqlite3.Error as erro:
            messagebox.showwarning(
                "Banco indisponível", f"Não foi possível abrir o banco de dados.\n{erro}"
            )
        return DADOS_INICIAIS.copy()

    @staticmethod
    def atualizar_estrutura_banco(conexao: sqlite3.Connection) -> None:
        """Acrescenta os campos do ERP a bancos criados por versões anteriores."""
        colunas = {linha[1] for linha in conexao.execute("PRAGMA table_info(produtos)")}
        novos_campos = {
            "codigo": "TEXT NOT NULL DEFAULT ''", "codigo_barras": "TEXT NOT NULL DEFAULT ''",
            "fornecedor": "TEXT NOT NULL DEFAULT ''", "unidade": "TEXT NOT NULL DEFAULT 'UN'", "preco_compra": "REAL NOT NULL DEFAULT 0",
            "preco_venda": "REAL NOT NULL DEFAULT 0", "estoque_minimo": "INTEGER NOT NULL DEFAULT 0",
            "data_cadastro": "TEXT NOT NULL DEFAULT ''", "ultima_alteracao": "TEXT NOT NULL DEFAULT ''",
        }
        for campo, definicao in novos_campos.items():
            if campo not in colunas:
                conexao.execute(f"ALTER TABLE produtos ADD COLUMN {campo} {definicao}")
        conexao.execute("UPDATE produtos SET preco_venda = preco WHERE preco_venda = 0")
        conexao.execute("UPDATE produtos SET codigo = printf('P%04d', id) WHERE codigo = ''")

    @staticmethod
    def valores_banco(item: dict, posicao: int) -> tuple:
        return (item.get("codigo") or f"P{posicao:04d}", item.get("codigo_barras", ""), item["produto"], item["categoria"], item.get("fornecedor", ""), item.get("unidade", "UN").upper(), item.get("preco_venda", item.get("preco", 0)), item.get("preco_compra", 0), item.get("preco_venda", item.get("preco", 0)), item["quantidade"], item.get("estoque_minimo", 0), item.get("data_cadastro", ""), item.get("ultima_alteracao", ""))

    @staticmethod
    def registrar_movimento(item: dict, tipo: str, quantidade: float, valor: float = 0, observacao: str = "") -> None:
        """Registra entradas e saídas para relatórios históricos."""
        with sqlite3.connect(BANCO_DADOS) as conexao:
            conexao.execute(
                "INSERT INTO movimentos (tipo, codigo, produto, quantidade, valor, data_movimento, observacao) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (tipo, item["codigo"], item["produto"], quantidade, valor, datetime.now().strftime("%d/%m/%Y %H:%M"), observacao),
            )

    @staticmethod
    def carregar_json_legado() -> list[dict]:
        """Importa os dados existentes em JSON apenas na primeira criação do banco."""
        if not ARQUIVO_ESTOQUE.exists():
            return DADOS_INICIAIS.copy()
        try:
            with ARQUIVO_ESTOQUE.open("r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
            if isinstance(dados, list):
                return dados
        except (OSError, json.JSONDecodeError):
            pass
        return DADOS_INICIAIS.copy()

    @staticmethod
    def carregar_categorias() -> list[str]:
        """Lê a lista de categorias disponíveis no formulário."""
        try:
            with ARQUIVO_CATEGORIAS.open("r", encoding="utf-8") as arquivo:
                return sorted({linha.strip() for linha in arquivo if linha.strip()}, key=str.casefold)
        except OSError:
            return ["Alimentos", "Hortifruti", "Limpeza"]

    def criar_interface(self) -> None:
        cabecalho = ctk.CTkFrame(self, fg_color="#155e75", corner_radius=0, height=82)
        cabecalho.pack(fill="x")
        cabecalho.pack_propagate(False)
        ctk.CTkLabel(
            cabecalho, text="🛒  Controle de Estoque", font=("Segoe UI", 27, "bold"), text_color="white"
        ).pack(side="left", padx=28, pady=20)
        ctk.CTkLabel(
            cabecalho, text="MERCADO", font=("Segoe UI", 16, "bold"), text_color="#d9f3f5"
        ).pack(side="right", padx=28)

        conteudo = ctk.CTkFrame(self, fg_color="transparent")
        conteudo.pack(fill="both", expand=True, padx=28, pady=22)

        leitor_frame = ctk.CTkFrame(conteudo, fg_color="#e5f3f5", corner_radius=8)
        leitor_frame.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(leitor_frame, text="Leitor USB", font=("Segoe UI", 13, "bold"), text_color="#155e75").pack(side="left", padx=(14, 8), pady=8)
        self.leitor_codigo = ctk.CTkEntry(
            leitor_frame, height=34, placeholder_text="Leia ou digite o código de barras e pressione Enter",
            fg_color="white", text_color="#1f2937"
        )
        self.leitor_codigo.pack(side="left", fill="x", expand=True, padx=(0, 14), pady=8)
        self.leitor_codigo.bind("<Return>", self.processar_leitura_codigo_barras)
        ctk.CTkLabel(leitor_frame, text="Qtd. entrada", font=("Segoe UI", 12), text_color="#155e75").pack(side="left", padx=(0, 6))
        self.leitor_quantidade = ctk.CTkEntry(leitor_frame, width=74, height=34, justify="center", fg_color="white", text_color="#1f2937")
        self.leitor_quantidade.insert(0, "1")
        self.leitor_quantidade.pack(side="left", padx=(0, 14), pady=8)
        self.leitor_quantidade.bind("<Return>", self.processar_leitura_codigo_barras)
        ctk.CTkLabel(leitor_frame, text="Peso (kg)", font=("Segoe UI", 12), text_color="#155e75").pack(side="left", padx=(0, 6))
        self.leitor_peso = ctk.CTkEntry(leitor_frame, width=82, height=34, justify="center", placeholder_text="0,000", fg_color="white", text_color="#1f2937")
        self.leitor_peso.pack(side="left", padx=(0, 14), pady=8)
        self.leitor_peso.bind("<Return>", self.processar_leitura_codigo_barras)

        self.pesquisa = ctk.CTkEntry(
            conteudo, height=42, placeholder_text="🔍  Pesquisar produto, categoria ou preço...",
            font=("Segoe UI", 14), border_color="#9ca3af", fg_color="white", text_color="#1f2937"
        )
        self.pesquisa.pack(fill="x", pady=(0, 16))
        self.pesquisa.bind("<KeyRelease>", lambda _evento: self.atualizar_tabela())

        tabela_frame = ctk.CTkFrame(conteudo, fg_color="white", corner_radius=10)
        tabela_frame.pack(fill="both", expand=True)
        estilo = ttk.Style(self)
        estilo.theme_use("clam")
        estilo.configure("Estoque.Treeview", font=("Segoe UI", 12), rowheight=34, background="white", fieldbackground="white", foreground="#1f2937")
        estilo.configure("Estoque.Treeview.Heading", font=("Segoe UI", 12, "bold"), background="#e5f3f5", foreground="#155e75", relief="flat")
        estilo.map("Estoque.Treeview", background=[("selected", "#bfe5e9")], foreground=[("selected", "#0f3f4c")])

        colunas = ("codigo", "produto", "categoria", "quantidade", "preco_venda")
        self.tabela = ttk.Treeview(tabela_frame, columns=colunas, show="headings", style="Estoque.Treeview", selectmode="extended")
        configuracao_colunas = {
            "codigo": ("Código", 100, "center"), "produto": ("Produto", 270, "w"),
            "categoria": ("Categoria", 200, "w"), "quantidade": ("Quantidade", 120, "center"),
            "preco_venda": ("Preço de venda", 150, "e"),
        }
        for coluna, (titulo, largura, alinhamento) in configuracao_colunas.items():
            self.tabela.heading(coluna, text=titulo, command=lambda c=coluna: self.ordenar_por(c))
            self.tabela.column(coluna, width=largura, anchor=alinhamento, minwidth=90)
        self.tabela.pack(side="left", fill="both", expand=True, padx=(12, 0), pady=12)
        rolagem = ttk.Scrollbar(tabela_frame, orient="vertical", command=self.tabela.yview)
        rolagem.pack(side="right", fill="y", padx=(0, 12), pady=12)
        self.tabela.configure(yscrollcommand=rolagem.set)
        self.tabela.bind("<Double-1>", lambda _evento: self.abrir_formulario_edicao())

        rodape = ctk.CTkFrame(conteudo, fg_color="transparent")
        rodape.pack(fill="x", pady=(16, 0))
        self.status = ctk.CTkLabel(rodape, text="", font=("Segoe UI", 12), text_color="#4b5563")
        self.status.pack(side="left")
        botoes = ctk.CTkFrame(rodape, fg_color="transparent")
        botoes.pack(side="right")
        self.criar_botao(botoes, "Adicionar", self.abrir_formulario_adicao, "#0f766e").pack(side="left", padx=4)
        self.criar_botao(botoes, "Editar", self.abrir_formulario_edicao, "#2563eb").pack(side="left", padx=4)
        self.criar_botao(botoes, "Excluir", self.excluir_produto, "#dc2626").pack(side="left", padx=4)
        self.criar_botao(botoes, "Salvar", self.salvar_estoque, "#6b7280").pack(side="left", padx=4)
        self.criar_botao(botoes, "Relatório", self.gerar_relatorio, "#7c3aed").pack(side="left", padx=4)
        self.criar_botao(botoes, "Sair", self.sair, "#374151").pack(side="left", padx=4)

    @staticmethod
    def criar_botao(pai, texto: str, comando, cor: str) -> ctk.CTkButton:
        return ctk.CTkButton(pai, text=texto, command=comando, width=95, height=36, fg_color=cor, hover_color=cor, font=("Segoe UI", 12, "bold"))

    @staticmethod
    def formatar_preco(preco: float) -> str:
        return f"R$ {preco:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def atualizar_tabela(self) -> None:
        self.tabela.delete(*self.tabela.get_children())
        termo = self.pesquisa.get().strip().lower()
        itens_filtrados = []
        for indice, item in enumerate(self.produtos):
            valores = f"{item['codigo']} {item['codigo_barras']} {item['produto']} {item['categoria']} {item['fornecedor']} {item['preco_venda']}".lower()
            if termo in valores:
                itens_filtrados.append((indice, item))
        chave = lambda par: par[1][self.coluna_ordenacao].casefold() if self.coluna_ordenacao in {"codigo", "produto", "categoria"} else float(par[1][self.coluna_ordenacao])
        itens_filtrados.sort(key=chave, reverse=self.ordem_reversa)
        for indice, item in itens_filtrados:
            self.tabela.insert("", "end", iid=str(indice), values=(item["codigo"], item["produto"], item["categoria"], item["quantidade"], self.formatar_preco(float(item["preco_venda"]))))
        total_itens = sum(int(item["quantidade"]) for item in self.produtos)
        self.status.configure(text=f"{len(itens_filtrados)} produto(s) exibido(s)  •  {total_itens} item(ns) em estoque")

    def ordenar_por(self, coluna: str) -> None:
        """Ordena a tabela alternando entre ordem crescente e decrescente."""
        self.ordem_reversa = not self.ordem_reversa if coluna == self.coluna_ordenacao else False
        self.coluna_ordenacao = coluna
        self.atualizar_tabela()

    def processar_leitura_codigo_barras(self, _evento=None) -> str:
        """Localiza um produto pelo código lido e registra uma unidade de entrada."""
        codigo_barras = self.leitor_codigo.get().strip()
        if not codigo_barras:
            return "break"
        peso_texto = self.leitor_peso.get().strip()
        try:
            quantidade_entrada = int(self.leitor_quantidade.get().strip())
            if quantidade_entrada <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Quantidade inválida", "Informe uma quantidade de entrada maior que zero.")
            self.leitor_quantidade.focus_set()
            return "break"
        indice = next(
            (posicao for posicao, item in enumerate(self.produtos) if item["codigo_barras"] == codigo_barras),
            None,
        )
        self.leitor_codigo.delete(0, "end")
        if indice is None:
            cadastrar = messagebox.askyesno(
                "Código não encontrado",
                f"O código de barras {codigo_barras} não está cadastrado.\n\nDeseja cadastrar este produto?",
            )
            if cadastrar:
                self.abrir_formulario_adicao(codigo_barras=codigo_barras)
            else:
                self.leitor_codigo.focus_set()
            return "break"

        produto = self.produtos[indice]
        if peso_texto:
            try:
                peso = float(peso_texto.replace(",", "."))
                if peso <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showwarning("Peso inválido", "Informe um peso maior que zero, como 0,750.")
                self.leitor_peso.focus_set()
                return "break"
            if produto.get("unidade", "UN").upper() != "KG":
                messagebox.showwarning("Produto unitário", "Este produto está cadastrado como UN. Cadastre-o como KG para vender por peso.")
                return "break"
            if float(produto["quantidade"]) < peso:
                messagebox.showwarning("Estoque insuficiente", f"Estoque disponível: {float(produto['quantidade']):.3f} kg.")
                return "break"
            produto["quantidade"] = float(produto["quantidade"]) - peso
            mensagem_movimento = f"Venda por peso: {peso:.3f} kg × {self.formatar_preco(float(produto['preco_venda']))}/kg = {self.formatar_preco(peso * float(produto['preco_venda']))}"
        else:
            produto["quantidade"] = int(produto["quantidade"]) + quantidade_entrada
            mensagem_movimento = f"Entrada de {quantidade_entrada} unidade(s): {produto['produto']}"
        produto["ultima_alteracao"] = datetime.now().strftime("%d/%m/%Y %H:%M")
        self.salvar_estoque(exibir_mensagem=False)
        if peso_texto:
            self.registrar_movimento(produto, "Saída", peso, peso * float(produto["preco_venda"]), "Venda por peso")
        else:
            self.registrar_movimento(produto, "Entrada", quantidade_entrada, quantidade_entrada * float(produto["preco_compra"]), "Leitor USB")
        self.atualizar_tabela()
        self.tabela.selection_set(str(indice))
        self.tabela.focus(str(indice))
        self.tabela.see(str(indice))
        self.status.configure(text=f"{mensagem_movimento}  •  estoque atual: {produto['quantidade']}")
        self.leitor_quantidade.delete(0, "end")
        self.leitor_quantidade.insert(0, "1")
        self.leitor_peso.delete(0, "end")
        self.leitor_codigo.focus_set()
        return "break"

    def obter_selecao(self) -> int | None:
        selecionados = self.tabela.selection()
        if not selecionados:
            messagebox.showinfo("Seleção necessária", "Selecione um produto na tabela.")
            return None
        return int(selecionados[0])

    def abrir_formulario_adicao(self, codigo_barras: str = "") -> None:
        self.indice_em_edicao = None
        self.abrir_formulario("Adicionar produto", codigo_barras=codigo_barras)

    def abrir_formulario_edicao(self) -> None:
        indice = self.obter_selecao()
        if indice is None:
            return
        self.indice_em_edicao = indice
        self.abrir_formulario("Editar produto", self.produtos[indice])

    def abrir_formulario(self, titulo: str, item: dict | None = None, codigo_barras: str = "") -> None:
        janela = ctk.CTkToplevel(self)
        janela.title(titulo)
        janela.geometry("500x760")
        janela.resizable(False, False)
        janela.transient(self)
        janela.grab_set()
        ctk.CTkLabel(janela, text=titulo, font=("Segoe UI", 21, "bold")).pack(pady=(25, 16))
        formulario = ctk.CTkScrollableFrame(janela, fg_color="transparent")
        formulario.pack(fill="both", expand=True, padx=24)
        campos = {}
        sugestoes: list[str] = []
        indice_sugestao = -1
        botoes_sugestao = []

        def selecionar_sugestao(indice: int, ocultar: bool = False) -> None:
            """Aplica uma sugestão ao campo de categoria."""
            nonlocal indice_sugestao
            if not sugestoes:
                return
            indice_sugestao = indice % len(sugestoes)
            campos["categoria"].delete(0, "end")
            campos["categoria"].insert(0, sugestoes[indice_sugestao])
            for posicao, botao in enumerate(botoes_sugestao):
                botao.configure(fg_color="#0f766e" if posicao == indice_sugestao else "#e5f3f5")
            if ocultar:
                sugestoes_frame.pack_forget()

        def atualizar_sugestoes(evento=None) -> str | None:
            """Filtra categorias enquanto o usuário digita."""
            nonlocal sugestoes, indice_sugestao, botoes_sugestao
            if evento and evento.keysym in {"Up", "Down", "Return", "Escape"}:
                if evento.keysym == "Up":
                    selecionar_sugestao(indice_sugestao - 1)
                elif evento.keysym == "Down":
                    selecionar_sugestao(indice_sugestao + 1)
                elif evento.keysym == "Return" and indice_sugestao >= 0:
                    selecionar_sugestao(indice_sugestao, ocultar=True)
                elif evento.keysym == "Escape":
                    sugestoes_frame.pack_forget()
                return "break"

            termo = campos["categoria"].get().strip().casefold()
            for widget in sugestoes_frame.winfo_children():
                widget.destroy()
            botoes_sugestao = []
            indice_sugestao = -1
            if not termo:
                sugestoes_frame.pack_forget()
                return None
            sugestoes = [categoria for categoria in self.categorias if termo in categoria.casefold()][:5]
            if not sugestoes:
                sugestoes_frame.pack_forget()
                return None
            for posicao, categoria in enumerate(sugestoes):
                botao = ctk.CTkButton(
                sugestoes_frame, text=categoria, anchor="w", height=27,
                    fg_color="#e5f3f5", text_color="#155e75", hover_color="#bfe5e9",
                    command=lambda i=posicao: selecionar_sugestao(i, ocultar=True),
                )
                botao.pack(fill="x", padx=4, pady=1)
                botoes_sugestao.append(botao)
            sugestoes_frame.pack(fill="x", padx=0, pady=(0, 8))
            return None
        campos_formulario = (
            ("codigo", "Código"), ("codigo_barras", "Código de Barras"), ("produto", "Produto"),
            ("categoria", "Categoria"), ("fornecedor", "Fornecedor"), ("unidade", "Unidade (UN/KG)"), ("preco_compra", "Preço de Compra (R$)"),
            ("preco_venda", "Preço de Venda (R$)"), ("quantidade", "Quantidade"),
            ("estoque_minimo", "Estoque Mínimo"), ("data_cadastro", "Data de Cadastro"),
            ("ultima_alteracao", "Última Alteração"),
        )
        agora = datetime.now().strftime("%d/%m/%Y %H:%M")
        for chave, rotulo in campos_formulario:
            ctk.CTkLabel(formulario, text=rotulo, anchor="w").pack(fill="x", padx=12)
            if chave == "categoria":
                entrada = ctk.CTkEntry(formulario, height=35, placeholder_text="Digite para pesquisar uma categoria")
            elif chave == "unidade":
                entrada = ctk.CTkComboBox(formulario, values=["UN", "KG"], height=35)
            else:
                entrada = ctk.CTkEntry(formulario, height=35)
            entrada.pack(fill="x", padx=12, pady=(2, 10))
            if item:
                valor = item[chave]
                texto = str(valor).replace(".", ",") if chave in {"preco_compra", "preco_venda"} else str(valor)
                if chave == "unidade":
                    entrada.set(texto)
                else:
                    entrada.insert(0, texto)
            elif chave == "codigo":
                entrada.insert(0, f"P{len(self.produtos) + 1:04d}")
            elif chave == "codigo_barras" and codigo_barras:
                entrada.insert(0, codigo_barras)
            elif chave == "unidade":
                entrada.set("UN")
            elif chave in {"data_cadastro", "ultima_alteracao"}:
                entrada.insert(0, agora)
            if chave in {"data_cadastro", "ultima_alteracao"}:
                entrada.configure(state="readonly")
            campos[chave] = entrada
            if chave == "categoria":
                area_sugestoes = ctk.CTkFrame(formulario, fg_color="transparent")
                area_sugestoes.pack(fill="x", padx=12, pady=(0, 8))
                sugestoes_frame = ctk.CTkFrame(
                    area_sugestoes, fg_color="white", border_width=1, border_color="#9ca3af", corner_radius=6
                )
                entrada.bind("<KeyRelease>", atualizar_sugestoes)

        def confirmar() -> None:
            try:
                codigo = campos["codigo"].get().strip()
                codigo_barras = campos["codigo_barras"].get().strip()
                produto = campos["produto"].get().strip().upper()
                categoria = campos["categoria"].get().strip()
                fornecedor = campos["fornecedor"].get().strip()
                unidade = campos["unidade"].get().strip().upper()
                quantidade = float(campos["quantidade"].get().strip().replace(",", "."))
                estoque_minimo = float(campos["estoque_minimo"].get().strip().replace(",", "."))
                preco_compra = float(campos["preco_compra"].get().strip().replace(",", "."))
                preco_venda = float(campos["preco_venda"].get().strip().replace(",", "."))
                if not codigo or not produto or not categoria or unidade not in {"UN", "KG"}:
                    raise ValueError
                if quantidade < 0 or estoque_minimo < 0 or preco_compra < 0 or preco_venda < 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Dados inválidos", "Preencha todos os campos. Quantidade e preço devem ser números não negativos.", parent=janela)
                return
            novo_item = {
                "codigo": codigo, "codigo_barras": codigo_barras, "produto": produto, "categoria": categoria,
                "fornecedor": fornecedor, "unidade": unidade, "preco_compra": preco_compra, "preco_venda": preco_venda,
                "quantidade": quantidade, "estoque_minimo": estoque_minimo,
                "data_cadastro": item["data_cadastro"] if item else agora, "ultima_alteracao": agora,
            }
            quantidade_anterior = float(item["quantidade"]) if item else 0
            if self.indice_em_edicao is None:
                self.produtos.append(novo_item)
            else:
                self.produtos[self.indice_em_edicao] = novo_item
            self.salvar_estoque(exibir_mensagem=False)
            diferenca = quantidade - quantidade_anterior
            if diferenca:
                tipo = "Entrada" if diferenca > 0 else "Saída"
                self.registrar_movimento(novo_item, tipo, abs(diferenca), abs(diferenca) * float(novo_item["preco_compra"]), "Ajuste de cadastro")
            self.atualizar_tabela()
            janela.destroy()

        ctk.CTkButton(janela, text="Salvar produto", command=confirmar, height=38, fg_color="#0f766e").pack(fill="x", padx=36, pady=(10, 18))

    def excluir_produto(self) -> None:
        selecionados = self.tabela.selection()
        if not selecionados:
            messagebox.showinfo("Seleção necessária", "Selecione um ou mais produtos na tabela.")
            return
        indices = sorted((int(indice) for indice in selecionados), reverse=True)
        if messagebox.askyesno("Excluir produtos", f"Deseja excluir {len(indices)} produto(s) selecionado(s) do estoque?"):
            for indice in indices:
                self.produtos.pop(indice)
            self.salvar_estoque(exibir_mensagem=False)
            self.atualizar_tabela()

    def salvar_estoque(self, exibir_mensagem: bool = True) -> None:
        try:
            with sqlite3.connect(BANCO_DADOS) as conexao:
                conexao.execute("DELETE FROM produtos")
                conexao.executemany(
                    "INSERT INTO produtos (codigo, codigo_barras, produto, categoria, fornecedor, unidade, preco, preco_compra, preco_venda, quantidade, estoque_minimo, data_cadastro, ultima_alteracao) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    [self.valores_banco(item, posicao) for posicao, item in enumerate(self.produtos, 1)],
                )
            if exibir_mensagem:
                messagebox.showinfo("Estoque salvo", f"Dados salvos em:\n{BANCO_DADOS.name}")
        except sqlite3.Error as erro:
            messagebox.showerror("Erro ao salvar", f"Não foi possível salvar o estoque.\n{erro}")

    def gerar_relatorio(self) -> None:
        """Abre a seleção dos relatórios que devem ser exportados."""
        janela = ctk.CTkToplevel(self)
        janela.title("Selecionar relatórios")
        janela.geometry("410x410")
        janela.resizable(False, False)
        janela.transient(self)
        janela.grab_set()
        ctk.CTkLabel(janela, text="Relatórios", font=("Segoe UI", 22, "bold")).pack(pady=(24, 4))
        ctk.CTkLabel(janela, text="Marque um ou mais tipos para exportar.").pack(pady=(0, 12))
        opcoes = [
            ("categoria", "Por categoria"), ("preco", "Preços"), ("produto", "Produtos"),
            ("venda", "Vendas (valor atual)"), ("compra", "Compras (custo atual)"),
            ("lucro", "Lucro estimado"), ("saidas", "Saídas"), ("entradas", "Entradas"),
        ]
        selecoes = {chave: ctk.BooleanVar(value=False) for chave, _ in opcoes}
        lista = ctk.CTkFrame(janela, fg_color="transparent")
        lista.pack(fill="x", padx=46)
        for chave, texto in opcoes:
            ctk.CTkCheckBox(lista, text=texto, variable=selecoes[chave]).pack(anchor="w", pady=4)

        def confirmar() -> None:
            tipos = [chave for chave, variavel in selecoes.items() if variavel.get()]
            if not tipos:
                messagebox.showinfo("Seleção necessária", "Escolha pelo menos um tipo de relatório.", parent=janela)
                return
            self.exportar_relatorios(tipos)
            janela.destroy()

        ctk.CTkButton(janela, text="Gerar selecionados", command=confirmar, fg_color="#7c3aed").pack(pady=18)

    def exportar_relatorios(self, tipos: list[str]) -> None:
        """Exporta os tipos selecionados para CSVs independentes."""
        try:
            PASTA_RELATORIOS.mkdir(exist_ok=True)
            cabecalho = ["Código", "Produto", "Categoria", "Fornecedor", "Unidade", "Preço compra", "Preço venda", "Quantidade", "Estoque mínimo", "Valor compra", "Valor venda", "Lucro estimado"]

            def salvar_csv(nome: str, linhas: list[list]) -> None:
                with (PASTA_RELATORIOS / f"{nome}.csv").open("w", encoding="utf-8-sig", newline="") as arquivo:
                    escritor = csv.writer(arquivo, delimiter=";")
                    escritor.writerows(linhas)

            if "categoria" in tipos:
                for categoria in sorted({item["categoria"] for item in self.produtos}):
                    nome = "".join(letra if letra.isalnum() else "_" for letra in categoria) or "sem_categoria"
                    itens = [item for item in self.produtos if item["categoria"] == categoria]
                    salvar_csv(f"categoria_{nome}", [cabecalho] + [self.linha_relatorio(item) for item in itens])
            if "produto" in tipos:
                salvar_csv("produtos", [cabecalho] + [self.linha_relatorio(item) for item in self.produtos])
            if "preco" in tipos:
                salvar_csv("precos", [["Código", "Produto", "Unidade", "Preço de compra", "Preço de venda"]] + [[item["codigo"], item["produto"], item["unidade"], item["preco_compra"], item["preco_venda"]] for item in self.produtos])
            if "venda" in tipos:
                salvar_csv("vendas", [["Código", "Produto", "Quantidade", "Preço venda", "Valor potencial de venda"]] + [[item["codigo"], item["produto"], item["quantidade"], item["preco_venda"], float(item["quantidade"]) * float(item["preco_venda"])] for item in self.produtos])
            if "compra" in tipos:
                salvar_csv("compras", [["Código", "Produto", "Quantidade", "Preço compra", "Custo em estoque"]] + [[item["codigo"], item["produto"], item["quantidade"], item["preco_compra"], float(item["quantidade"]) * float(item["preco_compra"])] for item in self.produtos])
            if "lucro" in tipos:
                salvar_csv("lucro", [["Código", "Produto", "Lucro unitário", "Lucro estimado"]] + [[item["codigo"], item["produto"], float(item["preco_venda"]) - float(item["preco_compra"]), float(item["quantidade"]) * (float(item["preco_venda"]) - float(item["preco_compra"]))] for item in self.produtos])
            if {"entradas", "saidas"} & set(tipos):
                with sqlite3.connect(BANCO_DADOS) as conexao:
                    for tipo, nome in (("Entrada", "entradas"), ("Saída", "saidas")):
                        if nome in tipos:
                            movimentos = conexao.execute("SELECT data_movimento, codigo, produto, quantidade, valor, observacao FROM movimentos WHERE tipo = ? ORDER BY id DESC", (tipo,)).fetchall()
                            salvar_csv(nome, [["Data", "Código", "Produto", "Quantidade", "Valor", "Observação"]] + [list(linha) for linha in movimentos])
            messagebox.showinfo("Relatórios gerados", f"Relatórios exportados em:\n{PASTA_RELATORIOS.name}")
        except (OSError, sqlite3.Error) as erro:
            messagebox.showerror("Erro no relatório", f"Não foi possível gerar os relatórios.\n{erro}")

    @staticmethod
    def linha_relatorio(item: dict) -> list:
        quantidade = float(item["quantidade"])
        compra = float(item["preco_compra"])
        venda = float(item["preco_venda"])
        return [item["codigo"], item["produto"], item["categoria"], item["fornecedor"], item["unidade"], compra, venda, quantidade, item["estoque_minimo"], quantidade * compra, quantidade * venda, quantidade * (venda - compra)]

    def sair(self) -> None:
        self.salvar_estoque(exibir_mensagem=False)
        self.destroy()


if __name__ == "__main__":
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    app = ControleEstoque()
    app.mainloop()
