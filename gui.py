import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
from datetime import datetime
import json
from impressao import imprimir_pedido

class PedidoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gerenciador de Pedidos")
        self.root.geometry("800x600")

        self.pedidos = []

        self.tab_control = ttk.Notebook(root)

        self.lista_pedidos_tab = ttk.Frame(self.tab_control)
        self.adicionar_pedido_tab = ttk.Frame(self.tab_control)

        self.tab_control.add(self.lista_pedidos_tab, text="Lista de Pedidos")
        self.tab_control.add(self.adicionar_pedido_tab, text="Adicionar Pedido")

        self.tab_control.pack(expand=1, fill="both")

        self.create_lista_pedidos_tab()
        self.create_adicionar_pedido_tab()

        self.carregar_pedidos()  # Carregar pedidos ao iniciar

    def create_lista_pedidos_tab(self):
        self.lista_pedidos_listbox = tk.Listbox(self.lista_pedidos_tab, selectmode=tk.MULTIPLE, height=20)
        self.lista_pedidos_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar = tk.Scrollbar(self.lista_pedidos_tab)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.lista_pedidos_listbox.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.lista_pedidos_listbox.yview)

        self.imprimir_btn = tk.Button(self.lista_pedidos_tab, text="Imprimir Selecionados", command=self.imprimir_pedidos_selecionados)
        self.imprimir_btn.pack(pady=10)

        self.apagar_btn = tk.Button(self.lista_pedidos_tab, text="Apagar Selecionados", command=self.apagar_pedidos_selecionados)
        self.apagar_btn.pack(pady=10)

        self.atualizar_lista_pedidos()

    def create_adicionar_pedido_tab(self):
        tk.Label(self.adicionar_pedido_tab, text="Nome do Comprador").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        self.nome_entry = tk.Entry(self.adicionar_pedido_tab)
        self.nome_entry.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)

        self.pedidos_frame = tk.Frame(self.adicionar_pedido_tab)
        self.pedidos_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky=tk.W)

        self.pedido_entries = []
        self.add_pedido_entry()

        self.add_pedido_btn = tk.Button(self.adicionar_pedido_tab, text="Adicionar Outro Pedido", command=self.add_pedido_entry)
        self.add_pedido_btn.grid(row=2, column=0, columnspan=2, pady=10)

        tk.Label(self.adicionar_pedido_tab, text="Telefone").grid(row=3, column=0, padx=10, pady=5, sticky=tk.W)
        self.telefone_entry = tk.Entry(self.adicionar_pedido_tab)
        self.telefone_entry.grid(row=3, column=1, padx=10, pady=5, sticky=tk.W)

        tk.Label(self.adicionar_pedido_tab, text="Cartão").grid(row=4, column=0, padx=10, pady=5, sticky=tk.W)
        self.cartao_var = tk.StringVar(value="Não")
        tk.Radiobutton(self.adicionar_pedido_tab, text="Sim", variable=self.cartao_var, value="Sim").grid(row=4, column=1, padx=10, pady=5, sticky=tk.W)
        tk.Radiobutton(self.adicionar_pedido_tab, text="Não", variable=self.cartao_var, value="Não").grid(row=4, column=1, padx=10, pady=5, sticky=tk.E)

        tk.Label(self.adicionar_pedido_tab, text="Contato").grid(row=5, column=0, padx=10, pady=5, sticky=tk.W)
        self.contato_var = tk.StringVar(value="WhatsApp")
        tk.Radiobutton(self.adicionar_pedido_tab, text="Telefone", variable=self.contato_var, value="Telefone").grid(row=5, column=1, padx=10, pady=5, sticky=tk.W)
        tk.Radiobutton(self.adicionar_pedido_tab, text="WhatsApp", variable=self.contato_var, value="WhatsApp").grid(row=5, column=2, padx=10, pady=5, sticky=tk.W)
        tk.Radiobutton(self.adicionar_pedido_tab, text="Loja", variable=self.contato_var, value="Loja").grid(row=5, column=3, padx=10, pady=5, sticky=tk.W)

        tk.Label(self.adicionar_pedido_tab, text="Nome do Destinatário").grid(row=6, column=0, padx=10, pady=5, sticky=tk.W)
        self.destinatario_entry = tk.Entry(self.adicionar_pedido_tab)
        self.destinatario_entry.grid(row=6, column=1, padx=10, pady=5, sticky=tk.W)

        tk.Label(self.adicionar_pedido_tab, text="Telefone do Destinatário").grid(row=7, column=0, padx=10, pady=5, sticky=tk.W)
        self.telefone_destinatario_entry = tk.Entry(self.adicionar_pedido_tab)
        self.telefone_destinatario_entry.grid(row=7, column=1, padx=10, pady=5, sticky=tk.W)

        tk.Label(self.adicionar_pedido_tab, text="Endereço de Entrega").grid(row=8, column=0, padx=10, pady=5, sticky=tk.W)
        self.endereco_entry = tk.Entry(self.adicionar_pedido_tab)
        self.endereco_entry.grid(row=8, column=1, padx=10, pady=5, sticky=tk.W)

        tk.Label(self.adicionar_pedido_tab, text="Referência").grid(row=9, column=0, padx=10, pady=5, sticky=tk.W)
        self.referencia_entry = tk.Entry(self.adicionar_pedido_tab)
        self.referencia_entry.grid(row=9, column=1, padx=10, pady=5, sticky=tk.W)

        tk.Label(self.adicionar_pedido_tab, text="Data de Entrega").grid(row=10, column=0, padx=10, pady=5, sticky=tk.W)
        self.data_entrega_entry = DateEntry(self.adicionar_pedido_tab, date_pattern='dd/MM/yyyy')
        self.data_entrega_entry.grid(row=10, column=1, padx=10, pady=5, sticky=tk.W)

        tk.Label(self.adicionar_pedido_tab, text="Hora de Entrega").grid(row=11, column=0, padx=10, pady=5, sticky=tk.W)
        self.hora_entrega_entry = tk.Entry(self.adicionar_pedido_tab)
        self.hora_entrega_entry.grid(row=11, column=1, padx=10, pady=5, sticky=tk.W)

        self.adicionar_pedido_btn = tk.Button(self.adicionar_pedido_tab, text="Adicionar Pedido", command=self.adicionar_pedido)
        self.adicionar_pedido_btn.grid(row=12, column=0, columnspan=2, pady=10)

    def add_pedido_entry(self):
        row = len(self.pedido_entries)
        pedido_label = tk.Label(self.pedidos_frame, text=f"Pedido {row + 1}")
        pedido_label.grid(row=row, column=0, padx=10, pady=5, sticky=tk.W)
        pedido_entry = tk.Entry(self.pedidos_frame)
        pedido_entry.grid(row=row, column=1, padx=10, pady=5, sticky=tk.W)
        self.pedido_entries.append(pedido_entry)

    def adicionar_pedido(self):
        pedidos = [entry.get() for entry in self.pedido_entries]
        pedido = {
            "Nome do Comprador": self.nome_entry.get(),
            "Pedidos": pedidos,  # Lista de pedidos
            "Telefone": self.telefone_entry.get(),
            "Cartão": self.cartao_var.get(),
            "Contato": self.contato_var.get(),
            "Nome do Destinatário": self.destinatario_entry.get(),
            "Telefone do Destinatário": self.telefone_destinatario_entry.get(),
            "Endereço de Entrega": self.endereco_entry.get(),
            "Referência": self.referencia_entry.get(),
            "Data de Entrega": self.data_entrega_entry.get_date().strftime("%d/%m/%Y") if self.data_entrega_entry.get_date() else "",
            "Hora de Entrega": self.hora_entrega_entry.get(),
            "Data do Pedido": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        }

        self.pedidos.append(pedido)
        self.atualizar_lista_pedidos()
        self.salvar_pedidos()  # Salva os pedidos no arquivo JSON

        # Limpar campos
        self.nome_entry.delete(0, tk.END)
        for entry in self.pedido_entries:
            entry.delete(0, tk.END)
        self.telefone_entry.delete(0, tk.END)
        self.destinatario_entry.delete(0, tk.END)
        self.telefone_destinatario_entry.delete(0, tk.END)
        self.endereco_entry.delete(0, tk.END)
        self.referencia_entry.delete(0, tk.END)
        self.hora_entrega_entry.delete(0, tk.END)
        self.contato_var.set("")  # Limpar a seleção dos radiobuttons

    def atualizar_lista_pedidos(self):
        self.lista_pedidos_listbox.delete(0, tk.END)
        for pedido in self.pedidos:
            exibir_pedido = f"Nome: {pedido['Nome do Comprador']}, Data do Pedido: {pedido['Data do Pedido']}"
            self.lista_pedidos_listbox.insert(tk.END, exibir_pedido)

    def apagar_pedidos_selecionados(self):
        selecionados = self.lista_pedidos_listbox.curselection()
        for indice in reversed(selecionados):
            self.pedidos.pop(indice)
        self.atualizar_lista_pedidos()
        self.salvar_pedidos()  # Salva os pedidos no arquivo JSON

    def imprimir_pedidos_selecionados(self):
        selecionados = self.lista_pedidos_listbox.curselection()
        for indice in selecionados:
            pedido = self.pedidos[indice]
            imprimir_pedido(pedido)  # Chama a função de impressão

    def salvar_pedidos(self):
        with open("pedidos.json", "w") as arquivo:
            json.dump(self.pedidos, arquivo, indent=4)

    def carregar_pedidos(self):
        try:
            with open("pedidos.json", "r") as arquivo:
                self.pedidos = json.load(arquivo)
        except FileNotFoundError:
            self.pedidos = []

if __name__ == "__main__":
    root = tk.Tk()
    app = PedidoApp(root)
    root.mainloop()
