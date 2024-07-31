import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
from datetime import datetime
import json
from impressao import imprimir_pedido
import tkinter.messagebox as messagebox
from tkinter import filedialog
from tkinter import filedialog, Tk, messagebox

class PedidoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gerenciador de Pedidos")
        self.root.geometry("900x600")

        self.pedidos = []
        self.logo_path = ""

        self.tab_control = ttk.Notebook(root)

        self.lista_pedidos_tab = ttk.Frame(self.tab_control)
        self.adicionar_pedido_tab = ttk.Frame(self.tab_control)
        self.configuracao_tab = ttk.Frame(self.tab_control)

        self.tab_control.add(self.lista_pedidos_tab, text="Lista de Pedidos")
        self.tab_control.add(self.adicionar_pedido_tab, text="Adicionar Pedido")
        self.tab_control.add(self.configuracao_tab, text="Configuração")

        self.tab_control.pack(expand=1, fill="both")

        self.create_lista_pedidos_tab()
        self.create_adicionar_pedido_tab()
        self.create_configuracao_tab()

        self.carregar_pedidos()
        self.atualizar_lista_pedidos()

    def create_configuracao_tab(self):
        for widget in self.configuracao_tab.winfo_children():
            widget.destroy()

        tk.Label(self.configuracao_tab, text="Caminho do Logo").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        self.logo_path_entry = tk.Entry(self.configuracao_tab, width=60, state='readonly')
        self.logo_path_entry.grid(row=0, column=1, padx=10, pady=5, sticky=tk.EW)

        self.selecionar_logo_btn = tk.Button(self.configuracao_tab, text="Selecionar Logo", command=self.selecionar_logo)
        self.selecionar_logo_btn.grid(row=1, column=0, pady=10, padx=10, sticky=tk.W)

        self.remover_logo_btn = tk.Button(self.configuracao_tab, text="Remover Logo", command=self.remover_logo)
        self.remover_logo_btn.grid(row=1, column=1, pady=10, padx=10, sticky=tk.E)

        tk.Label(self.configuracao_tab, text="Cabeçalho do Pedido").grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
        self.cabecalho_pedido_entry = tk.Entry(self.configuracao_tab, width=60)
        self.cabecalho_pedido_entry.grid(row=2, column=1, padx=10, pady=5, sticky=tk.EW)

        tk.Label(self.configuracao_tab, text="Nome do Estabelecimento").grid(row=3, column=0, padx=10, pady=5, sticky=tk.W)
        self.nome_estabelecimento_entry = tk.Entry(self.configuracao_tab, width=60)
        self.nome_estabelecimento_entry.grid(row=3, column=1, padx=10, pady=5, sticky=tk.EW)

        self.salvar_configuracao_btn = tk.Button(self.configuracao_tab, text="Salvar Configuração", command=self.salvar_configuracao)
        self.salvar_configuracao_btn.grid(row=4, column=0, columnspan=2, pady=10, padx=10)

        self.carregar_configuracao()


    def selecionar_logo(self):
        caminho_logo = filedialog.askopenfilename(title="Selecione o Logo", filetypes=[("Imagens", "*.png;*.jpg;*.jpeg")])
        if caminho_logo:
            self.logo_path = caminho_logo
            self.logo_path_entry.config(state='normal')
            self.logo_path_entry.delete(0, tk.END)
            self.logo_path_entry.insert(0, caminho_logo)
            self.logo_path_entry.config(state='readonly')

    def remover_logo(self):
        self.logo_path = ""
        self.logo_path_entry.config(state='normal')
        self.logo_path_entry.delete(0, tk.END)
        self.logo_path_entry.config(state='readonly')

    def salvar_configuracao(self):
        try:
            # Coletar as configurações atuais
            configuracoes = {
                "logo_path": self.logo_path_entry.get(),
                "cabecalho_pedido": self.cabecalho_pedido_entry.get(),
                "nome_estabelecimento": self.nome_estabelecimento_entry.get()
            }

            # Salvar as configurações em um arquivo JSON
            with open("config.json", "w") as arquivo:
                json.dump(configuracoes, arquivo, indent=4)

            # Informar ao usuário que a configuração foi salva com sucesso
            tk.messagebox.showinfo("Configuração", "Configuração salva com sucesso!")
        except Exception as e:
            print(f"Erro ao salvar configuração: {e}")
            tk.messagebox.showerror("Erro", "Não foi possível salvar a configuração.")


    def carregar_configuracao(self):
        try:
            with open("config.json", "r") as arquivo:
                config = json.load(arquivo)
                # Atualizar os campos da interface gráfica com as configurações carregadas
                self.logo_path_entry.config(state='normal')
                self.logo_path_entry.delete(0, tk.END)
                self.logo_path_entry.insert(0, config.get("logo_path", ""))
                self.logo_path_entry.config(state='readonly')
                
                self.cabecalho_pedido_entry.delete(0, tk.END)
                self.cabecalho_pedido_entry.insert(0, config.get("cabecalho_pedido"))

                self.nome_estabelecimento_entry.delete(0, tk.END)
                self.nome_estabelecimento_entry.insert(0, config.get("nome_estabelecimento"))
        except FileNotFoundError:
            # Configurações padrão
            self.logo_path_entry.config(state='normal')
            self.logo_path_entry.delete(0, tk.END)
            self.logo_path_entry.insert(0, "")
            self.logo_path_entry.config(state='readonly')
            
            self.cabecalho_pedido_entry.delete(0, tk.END)
            self.cabecalho_pedido_entry.insert(0, "Recibo de Pedido")

            self.nome_estabelecimento_entry.delete(0, tk.END)
            self.nome_estabelecimento_entry.insert(0, "Adriana Flores")
        except Exception as e:
            print(f"Erro ao carregar configuração: {e}")
            tk.messagebox.showerror("Erro", "Não foi possível carregar a configuração.")



    def create_lista_pedidos_tab(self):
        # Configuração do layout da aba de lista de pedidos
        self.lista_pedidos_tab.grid_rowconfigure(0, weight=1)
        self.lista_pedidos_tab.grid_rowconfigure(1, weight=10)
        self.lista_pedidos_tab.grid_rowconfigure(2, weight=0)
        self.lista_pedidos_tab.grid_columnconfigure(0, weight=1)

        # Barra de Busca
        tk.Label(self.lista_pedidos_tab, text="Buscar:").grid(row=0, column=0, pady=5, padx=10, sticky=tk.W)
        self.busca_entry = tk.Entry(self.lista_pedidos_tab)
        self.busca_entry.grid(row=0, column=1, pady=5, padx=10, sticky=tk.EW)
        self.busca_entry.bind("<KeyRelease>", self.filtrar_pedidos)

        # Configurar a coluna para expandir a barra de busca
        self.lista_pedidos_tab.grid_columnconfigure(1, weight=1)


        # Treeview para exibir os pedidos
        self.tree = ttk.Treeview(self.lista_pedidos_tab, columns=("Nome", "Data do Pedido", "Telefone", "Cartão", "Pedido realizado por", "Nome do Destinatário", "Telefone do Destinatário", "Endereço de Entrega", "Referência", "Data de Entrega", "Hora de Entrega"), show='headings')
        
        # Cabeçalhos das colunas
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor=tk.W)
        
        self.tree.grid(row=1, column=0, columnspan=2, sticky="nsew")

        # Scrollbars
        self.scrollbar_y = tk.Scrollbar(self.lista_pedidos_tab, orient=tk.VERTICAL, command=self.tree.yview)
        self.scrollbar_y.grid(row=1, column=2, sticky="ns")
        self.tree.config(yscrollcommand=self.scrollbar_y.set)
        
        self.scrollbar_x = tk.Scrollbar(self.lista_pedidos_tab, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.scrollbar_x.grid(row=2, column=0, columnspan=2, sticky="ew")
        self.tree.config(xscrollcommand=self.scrollbar_x.set)

        # Botões
        self.imprimir_btn = tk.Button(self.lista_pedidos_tab, text="Imprimir Selecionados", command=self.imprimir_pedidos_selecionados)
        self.imprimir_btn.grid(row=3, column=0, pady=10, padx=10, sticky=tk.W)
        
        self.apagar_btn = tk.Button(self.lista_pedidos_tab, text="Apagar Selecionados", command=self.apagar_pedidos_selecionados)
        self.apagar_btn.grid(row=3, column=1, pady=10, padx=10, sticky=tk.E)
        
        # Atualizar a lista de pedidos
        self.atualizar_lista_pedidos()


    def create_adicionar_pedido_tab(self):
        # Configurar o layout da aba de adicionar pedidos
        self.adicionar_pedido_tab.grid_rowconfigure(0, weight=0)
        self.adicionar_pedido_tab.grid_rowconfigure(1, weight=1)
        self.adicionar_pedido_tab.grid_rowconfigure(2, weight=1)
        self.adicionar_pedido_tab.grid_rowconfigure(3, weight=1)
        self.adicionar_pedido_tab.grid_rowconfigure(4, weight=1)
        self.adicionar_pedido_tab.grid_rowconfigure(5, weight=1)
        self.adicionar_pedido_tab.grid_rowconfigure(6, weight=1)
        self.adicionar_pedido_tab.grid_rowconfigure(7, weight=1)
        self.adicionar_pedido_tab.grid_rowconfigure(8, weight=1)
        self.adicionar_pedido_tab.grid_rowconfigure(9, weight=1)
        self.adicionar_pedido_tab.grid_rowconfigure(10, weight=1)
        self.adicionar_pedido_tab.grid_rowconfigure(11, weight=0)
        self.adicionar_pedido_tab.grid_columnconfigure(0, weight=0)
        self.adicionar_pedido_tab.grid_columnconfigure(1, weight=1)

        # Nome do Comprador
        tk.Label(self.adicionar_pedido_tab, text="Nome do Comprador").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        self.nome_entry = tk.Entry(self.adicionar_pedido_tab, width=50)
        self.nome_entry.grid(row=0, column=1, padx=10, pady=5, sticky=tk.EW)

        # Adicionar Pedidos
        tk.Label(self.adicionar_pedido_tab, text="Pedidos").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        self.pedidos_frame = tk.Frame(self.adicionar_pedido_tab)
        self.pedidos_frame.grid(row=1, column=1, padx=10, pady=5, sticky=tk.EW)
        self.pedido_entries = []
        self.add_pedido_entry()

        self.add_pedido_btn = tk.Button(self.adicionar_pedido_tab, text="Adicionar Outro Pedido", command=self.add_pedido_entry)
        self.add_pedido_btn.grid(row=2, column=1, pady=10, sticky=tk.W)

        # Telefone
        tk.Label(self.adicionar_pedido_tab, text="Telefone").grid(row=3, column=0, padx=10, pady=5, sticky=tk.W)
        self.telefone_entry = tk.Entry(self.adicionar_pedido_tab, width=25)  # Ajustando a largura do campo de telefone
        self.telefone_entry.grid(row=3, column=1, padx=10, pady=5, sticky=tk.W)  # Ajustando a posição do campo de telefone

        # Cartão
        tk.Label(self.adicionar_pedido_tab, text="Cartão").grid(row=4, column=0, padx=10, pady=5, sticky=tk.W)
        cartao_frame = tk.Frame(self.adicionar_pedido_tab)
        cartao_frame.grid(row=4, column=1, padx=10, pady=5, sticky=tk.EW)
        self.cartao_var = tk.StringVar(value="Não")
        tk.Radiobutton(cartao_frame, text="Sim", variable=self.cartao_var, value="Sim").pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(cartao_frame, text="Não", variable=self.cartao_var, value="Não").pack(side=tk.LEFT, padx=5)

        # Contato
        tk.Label(self.adicionar_pedido_tab, text="Pedido realizado por").grid(row=5, column=0, padx=10, pady=5, sticky=tk.W)
        contato_frame = tk.Frame(self.adicionar_pedido_tab)
        contato_frame.grid(row=5, column=1, padx=10, pady=5, sticky=tk.EW)
        self.contato_var = tk.StringVar(value="WhatsApp")
        tk.Radiobutton(contato_frame, text="Telefone", variable=self.contato_var, value="Telefone").pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(contato_frame, text="WhatsApp", variable=self.contato_var, value="WhatsApp").pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(contato_frame, text="Loja", variable=self.contato_var, value="Loja").pack(side=tk.LEFT, padx=5)

        # Nome do Destinatário
        tk.Label(self.adicionar_pedido_tab, text="Nome do Destinatário").grid(row=6, column=0, padx=10, pady=5, sticky=tk.W)
        self.destinatario_entry = tk.Entry(self.adicionar_pedido_tab, width=50)
        self.destinatario_entry.grid(row=6, column=1, padx=10, pady=5, sticky=tk.EW)

        # Telefone do Destinatário
        tk.Label(self.adicionar_pedido_tab, text="Telefone do Destinatário").grid(row=7, column=0, padx=10, pady=5, sticky=tk.W)
        self.telefone_destinatario_entry = tk.Entry(self.adicionar_pedido_tab, width=25)
        self.telefone_destinatario_entry.grid(row=7, column=1, padx=10, pady=5, sticky=tk.W)

        # Endereço de Entrega
        tk.Label(self.adicionar_pedido_tab, text="Endereço de Entrega").grid(row=8, column=0, padx=10, pady=5, sticky=tk.W)
        self.endereco_entry = tk.Entry(self.adicionar_pedido_tab, width=50)
        self.endereco_entry.grid(row=8, column=1, padx=10, pady=5, sticky=tk.EW)

        # Referência
        tk.Label(self.adicionar_pedido_tab, text="Referência").grid(row=9, column=0, padx=10, pady=5, sticky=tk.W)
        self.referencia_entry = tk.Entry(self.adicionar_pedido_tab, width=50)
        self.referencia_entry.grid(row=9, column=1, padx=10, pady=5, sticky=tk.EW)

        # Data de Entrega
        tk.Label(self.adicionar_pedido_tab, text="Data de Entrega").grid(row=10, column=0, padx=10, pady=5, sticky=tk.W)
        self.data_entrega_entry = DateEntry(self.adicionar_pedido_tab, date_pattern='dd/MM/yyyy', width=12)  # Define a largura do campo de data
        self.data_entrega_entry.grid(row=10, column=1, padx=10, pady=5, sticky=tk.W)

        tk.Label(self.adicionar_pedido_tab, text="Hora de Entrega").grid(row=11, column=0, padx=10, pady=5, sticky=tk.W)
        self.hora_entrega_entry = tk.Frame(self.adicionar_pedido_tab)
        self.hora_entrega_entry.grid(row=11, column=1, padx=10, pady=5, sticky=tk.W)

        self.hora_var = tk.StringVar(value="00")
        self.minuto_var = tk.StringVar(value="00")
        tk.Spinbox(self.hora_entrega_entry, from_=0, to=23, textvariable=self.hora_var, width=3, format="%02.0f").grid(row=0, column=0)
        tk.Label(self.hora_entrega_entry, text=":").grid(row=0, column=1)
        tk.Spinbox(self.hora_entrega_entry, from_=0, to=59, textvariable=self.minuto_var, width=3, format="%02.0f").grid(row=0, column=2)



        # Botão Adicionar Pedido
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
        resposta = messagebox.askyesno("Confirmar", "Deseja realmente adicionar este pedido?")
        if not resposta:
            return

        pedidos = [entry.get() for entry in self.pedido_entries]
        hora = self.hora_var.get()
        minuto = self.minuto_var.get()
        
        pedido = {
            "Nome do Comprador": self.nome_entry.get(),
            "Pedidos": pedidos,
            "Telefone": self.telefone_entry.get(),
            "Cartão": self.cartao_var.get(),
            "Pedido realizado por": self.contato_var.get(),
            "Nome do Destinatário": self.destinatario_entry.get(),
            "Telefone do Destinatário": self.telefone_destinatario_entry.get(),
            "Endereço de Entrega": self.endereco_entry.get(),
            "Referência": self.referencia_entry.get(),
            "Data de Entrega": self.data_entrega_entry.get_date().strftime("%d/%m/%Y"),
            "Hora de Entrega": f"{hora.zfill(2)}:{minuto.zfill(2)}",
            "Data do Pedido": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        }
        self.pedidos.append(pedido)
        self.atualizar_lista_pedidos()
        self.salvar_pedidos()

        # Imprimir o pedido
        imprimir_pedido(pedido)

        messagebox.showinfo("Sucesso", "Pedido adicionado com sucesso!")

        # Limpar os campos após adicionar
        self.nome_entry.delete(0, tk.END)
        self.pedido_entries.clear()
        for widget in self.pedidos_frame.winfo_children():
            widget.destroy()
        self.add_pedido_entry()
        self.telefone_entry.delete(0, tk.END)
        self.cartao_var.set("Não")
        self.contato_var.set("WhatsApp")
        self.destinatario_entry.delete(0, tk.END)
        self.telefone_destinatario_entry.delete(0, tk.END)
        self.endereco_entry.delete(0, tk.END)
        self.referencia_entry.delete(0, tk.END)
        self.data_entrega_entry.set_date(datetime.now())
        self.hora_var.set("00")
        self.minuto_var.set("00")


    def salvar_pedidos(self):
        with open("pedidos.json", "w") as arquivo:
            json.dump(self.pedidos, arquivo, indent=4)


    def carregar_pedidos(self):
        try:
            with open("pedidos.json", "r") as arquivo:
                self.pedidos = json.load(arquivo)
        except FileNotFoundError:
            self.pedidos = []


    def atualizar_lista_pedidos(self):
        # Ordenar pedidos por data, mais recente primeiro
        self.pedidos.sort(key=lambda x: datetime.strptime(x['Data do Pedido'], "%d/%m/%Y %H:%M:%S"), reverse=True)
        
        self.tree.delete(*self.tree.get_children())
        for pedido in self.pedidos:
            self.tree.insert('', 'end', values=(
                pedido["Nome do Comprador"],
                pedido["Data do Pedido"],
                pedido["Telefone"],
                pedido["Cartão"],
                pedido["Pedido realizado por"],
                pedido["Nome do Destinatário"],
                pedido["Telefone do Destinatário"],
                pedido["Endereço de Entrega"],
                pedido["Referência"],
                pedido["Data de Entrega"],
                pedido["Hora de Entrega"]
            ))


    def filtrar_pedidos(self, event):
        query = self.busca_entry.get().lower()
        filtered_pedidos = [
            pedido for pedido in self.pedidos
            if query in pedido["Nome do Comprador"].lower() or query in pedido["Data do Pedido"].lower()
        ]
        self.tree.delete(*self.tree.get_children())
        for pedido in filtered_pedidos:
            self.tree.insert('', 'end', values=(
                pedido["Nome do Comprador"],
                pedido["Data do Pedido"],
                pedido["Telefone"],
                pedido["Cartão"],
                pedido["Pedido realizado por"],
                pedido["Nome do Destinatário"],
                pedido["Telefone do Destinatário"],
                pedido["Endereço de Entrega"],
                pedido["Referência"],
                pedido["Data de Entrega"],
                pedido["Hora de Entrega"]
            ))


    def imprimir_pedidos_selecionados(self):
        selecionados = self.tree.selection()
        if not selecionados:
            messagebox.showwarning("Aviso", "Nenhum pedido selecionado para imprimir.")
            return
        
        resposta = messagebox.askyesno("Confirmar Impressão", "Deseja realmente imprimir os pedidos selecionados?")
        if not resposta:
            return
        
        for item in selecionados:
            valores = self.tree.item(item, "values")
            pedido = next((p for p in self.pedidos if p["Nome do Comprador"] == valores[0] and p["Data do Pedido"] == valores[1]), None)
            if pedido:
                imprimir_pedido(pedido)
        messagebox.showinfo("Sucesso", "Pedidos impressos com sucesso!")



    def apagar_pedidos_selecionados(self):
        selecionados = self.tree.selection()
        if not selecionados:
            messagebox.showwarning("Aviso", "Nenhum pedido selecionado para apagar.")
            return
        
        resposta = messagebox.askyesno("Confirmar Exclusão", "Deseja realmente apagar os pedidos selecionados?")
        if not resposta:
            return
        
        for item in reversed(selecionados):
            index = self.tree.index(item)
            del self.pedidos[index]
            self.tree.delete(item)
        self.salvar_pedidos()
        messagebox.showinfo("Sucesso", "Pedidos apagados com sucesso!")



if __name__ == "__main__":
    root = tk.Tk()
    app = PedidoApp(root)
    app.carregar_configuracao()  # Carregar configurações ao iniciar o app
    root.mainloop()
