import tkinter as tk
from tkinter import simpledialog, messagebox

produtos = ['aveia', 'sabao em po', 'manteiga', 'cebola']
quantidades = [1, 1, 1, 1]

def atualizar_lista():
    lista.delete(0, tk.END)

    texto = pesquisa.get().lower()

    for i in range(len(produtos)):
        if texto in produtos[i].lower():
            lista.insert(tk.END, f"{produtos[i]} - {quantidades[i]} unidades")

def alterar_produto(event):
    if not lista.curselection():
        return

    item = lista.get(lista.curselection()[0])
    nome = item.split(" - ")[0]

    pos = produtos.index(nome)

    nova = simpledialog.askinteger(
        "Quantidade",
        f"{nome} possui {quantidades[pos]} unidades.\nNova quantidade:"
    )

    if nova is None:
        return

    if nova == 0:
        produtos.pop(pos)
        quantidades.pop(pos)
        messagebox.showinfo("Sucesso", "Produto removido!")
    else:
        quantidades[pos] = nova
        messagebox.showinfo("Sucesso", "Quantidade atualizada!")

    atualizar_lista()

janela = tk.Tk()
janela.configure(bg="#636b2f")
janela.title("Super Mercado - Controle de Estoque")
janela.geometry("450x350")
janela.iconbitmap("img/logo_estoque.ico")

tk.Label(janela, text="Pesquisar produto").pack(pady=5)

pesquisa = tk.Entry(janela, font=("Arial", 12))
pesquisa.pack(fill="x", padx=10)
pesquisa.bind("<KeyRelease>", lambda e: atualizar_lista())

lista = tk.Listbox(janela, font=("Arial", 12))
lista.pack(fill="both", expand=True, padx=10, pady=10)
lista.bind("<Double-Button-1>", alterar_produto)

atualizar_lista()

janela.mainloop()