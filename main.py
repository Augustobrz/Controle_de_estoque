"""Aplicação desktop para controle de estoque de um mercado."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from tkinter import messagebox, ttk
import customtkinter as ctk


ARQUIVO_ESTOQUE = Path(__file__).with_name("estoque.json")
ARQUIVO_RELATORIO = Path(__file__).with_name("relatorio_estoque.csv")
ARQUIVO_CATEGORIAS = Path(__file__).with_name("categorias.txt")
DADOS_INICIAIS = [
    {"produto": "Aveia", "quantidade": 10, "categoria": "Alimentos", "preco": 8.50},
    {"produto": "Cebola", "quantidade": 15, "categoria": "Hortifruti", "preco": 4.20},
    {"produto": "Sabão em pó", "quantidade": 3, "categoria": "Limpeza", "preco": 22.90},
]


class ControleEstoque(ctk.CTk):
    """Janela principal e operações de estoque."""

    def __init__(self) -> None:
        super().__init__()
        self.produtos = self.carregar_estoque()
        self.categorias = self.carregar_categorias()
        self.indice_em_edicao: int | None = None

        self.title("Controle de Estoque | Mercado")
        self.geometry("1000x630")
        self.minsize(850, 520)
        self.configure(fg_color="#f3f6f8")
        self.protocol("WM_DELETE_WINDOW", self.sair)
        self.criar_interface()
        self.atualizar_tabela()

    def carregar_estoque(self) -> list[dict]:
        """Carrega os dados gravados ou cria o estoque demonstrativo inicial."""
        if not ARQUIVO_ESTOQUE.exists():
            return DADOS_INICIAIS.copy()
        try:
            with ARQUIVO_ESTOQUE.open("r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
            if isinstance(dados, list):
                return dados
        except (OSError, json.JSONDecodeError):
            messagebox.showwarning(
                "Arquivo inválido", "Não foi possível ler o estoque salvo. Os dados iniciais serão usados."
            )
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

        colunas = ("produto", "quantidade", "categoria", "preco")
        self.tabela = ttk.Treeview(tabela_frame, columns=colunas, show="headings", style="Estoque.Treeview", selectmode="browse")
        configuracao_colunas = {
            "produto": ("Produto", 340, "w"), "quantidade": ("Quantidade", 130, "center"),
            "categoria": ("Categoria", 240, "w"), "preco": ("Preço", 150, "e"),
        }
        for coluna, (titulo, largura, alinhamento) in configuracao_colunas.items():
            self.tabela.heading(coluna, text=titulo)
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
        encontrados = 0
        for indice, item in enumerate(self.produtos):
            valores = f"{item['produto']} {item['categoria']} {item['preco']}".lower()
            if termo in valores:
                self.tabela.insert("", "end", iid=str(indice), values=(item["produto"], item["quantidade"], item["categoria"], self.formatar_preco(float(item["preco"]))))
                encontrados += 1
        total_itens = sum(int(item["quantidade"]) for item in self.produtos)
        self.status.configure(text=f"{encontrados} produto(s) exibido(s)  •  {total_itens} item(ns) em estoque")

    def obter_selecao(self) -> int | None:
        selecionados = self.tabela.selection()
        if not selecionados:
            messagebox.showinfo("Seleção necessária", "Selecione um produto na tabela.")
            return None
        return int(selecionados[0])

    def abrir_formulario_adicao(self) -> None:
        self.indice_em_edicao = None
        self.abrir_formulario("Adicionar produto")

    def abrir_formulario_edicao(self) -> None:
        indice = self.obter_selecao()
        if indice is None:
            return
        self.indice_em_edicao = indice
        self.abrir_formulario("Editar produto", self.produtos[indice])

    def abrir_formulario(self, titulo: str, item: dict | None = None) -> None:
        janela = ctk.CTkToplevel(self)
        janela.title(titulo)
        janela.geometry("430x410")
        janela.resizable(False, False)
        janela.transient(self)
        janela.grab_set()
        ctk.CTkLabel(janela, text=titulo, font=("Segoe UI", 21, "bold")).pack(pady=(25, 16))
        campos = {}
        for chave, rotulo in (("produto", "Produto"), ("quantidade", "Quantidade"), ("categoria", "Categoria"), ("preco", "Preço (R$)")):
            ctk.CTkLabel(janela, text=rotulo, anchor="w").pack(fill="x", padx=36)
            if chave == "categoria":
                entrada = ctk.CTkComboBox(
                    janela, values=self.categorias, height=35,
                    dropdown_fg_color="white", dropdown_text_color="#1f2937",
                    button_color="#0f766e", border_color="#9ca3af",
                )
            else:
                entrada = ctk.CTkEntry(janela, height=35)
            entrada.pack(fill="x", padx=36, pady=(2, 10))
            if item:
                valor = item[chave]
                texto = str(valor).replace(".", ",") if chave == "preco" else str(valor)
                if chave == "categoria":
                    entrada.set(texto)
                else:
                    entrada.insert(0, texto)
            campos[chave] = entrada

        def confirmar() -> None:
            try:
                produto = campos["produto"].get().strip()
                categoria = campos["categoria"].get().strip()
                quantidade = int(campos["quantidade"].get().strip())
                preco = float(campos["preco"].get().strip().replace(",", "."))
                if not produto or not categoria:
                    raise ValueError
                if quantidade < 0 or preco < 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Dados inválidos", "Preencha todos os campos. Quantidade e preço devem ser números não negativos.", parent=janela)
                return
            novo_item = {"produto": produto, "quantidade": quantidade, "categoria": categoria, "preco": preco}
            if self.indice_em_edicao is None:
                self.produtos.append(novo_item)
            else:
                self.produtos[self.indice_em_edicao] = novo_item
            self.salvar_estoque(exibir_mensagem=False)
            self.atualizar_tabela()
            janela.destroy()

        ctk.CTkButton(janela, text="Salvar produto", command=confirmar, height=38, fg_color="#0f766e").pack(pady=1)

    def excluir_produto(self) -> None:
        indice = self.obter_selecao()
        if indice is None:
            return
        produto = self.produtos[indice]["produto"]
        if messagebox.askyesno("Excluir produto", f"Deseja excluir '{produto}' do estoque?"):
            self.produtos.pop(indice)
            self.salvar_estoque(exibir_mensagem=False)
            self.atualizar_tabela()

    def salvar_estoque(self, exibir_mensagem: bool = True) -> None:
        try:
            with ARQUIVO_ESTOQUE.open("w", encoding="utf-8") as arquivo:
                json.dump(self.produtos, arquivo, ensure_ascii=False, indent=2)
            if exibir_mensagem:
                messagebox.showinfo("Estoque salvo", f"Dados salvos em:\n{ARQUIVO_ESTOQUE.name}")
        except OSError as erro:
            messagebox.showerror("Erro ao salvar", f"Não foi possível salvar o estoque.\n{erro}")

    def gerar_relatorio(self) -> None:
        try:
            with ARQUIVO_RELATORIO.open("w", encoding="utf-8-sig", newline="") as arquivo:
                escritor = csv.writer(arquivo, delimiter=";")
                escritor.writerow(["Produto", "Quantidade", "Categoria", "Preço unitário (R$)", "Valor em estoque (R$)"])
                for item in self.produtos:
                    escritor.writerow([item["produto"], item["quantidade"], item["categoria"], f"{float(item['preco']):.2f}", f"{int(item['quantidade']) * float(item['preco']):.2f}"])
            messagebox.showinfo("Relatório gerado", f"Arquivo criado com sucesso:\n{ARQUIVO_RELATORIO.name}")
        except OSError as erro:
            messagebox.showerror("Erro no relatório", f"Não foi possível gerar o relatório.\n{erro}")

    def sair(self) -> None:
        self.salvar_estoque(exibir_mensagem=False)
        self.destroy()


if __name__ == "__main__":
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    app = ControleEstoque()
    app.mainloop()
