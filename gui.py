import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
from datetime import datetime
import json
from impressao import imprimir_pedido
import tkinter.messagebox as messagebox
from tkinter import filedialog, Tk, messagebox, LabelFrame, StringVar, Radiobutton
import usb.core
import usb.util

class PedidoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gerenciador de Pedidos")
        self.root.geometry("780x680")

        self.root.iconbitmap("icons/icogerenciamento.ico")

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

        # Frame para a rolagem
        self.scrollable_config_frame = tk.Frame(self.configuracao_tab)
        self.scrollable_config_frame.grid(row=0, column=0, sticky="nsew")
        self.configuracao_tab.grid_rowconfigure(0, weight=1)
        self.configuracao_tab.grid_columnconfigure(0, weight=1)

        # Canvas para a rolagem
        self.config_canvas = tk.Canvas(self.scrollable_config_frame, borderwidth=0, highlightthickness=0)
        self.config_canvas.grid(row=0, column=0, sticky="nsew")

        # Scrollbar para a rolagem
        self.config_scrollbar = tk.Scrollbar(self.scrollable_config_frame, orient="vertical", command=self.config_canvas.yview)
        self.config_scrollbar.grid(row=0, column=1, sticky="ns")
        self.config_canvas.configure(yscrollcommand=self.config_scrollbar.set)

        # Frame que será colocado dentro do Canvas
        self.scrollable_config_content = tk.Frame(self.config_canvas)
        self.config_canvas.create_window((0, 0), window=self.scrollable_config_content, anchor="nw")

        # Atualiza o scrollregion do canvas quando o conteúdo é modificado
        self.scrollable_config_content.bind("<Configure>", lambda e: self.config_canvas.configure(scrollregion=self.config_canvas.bbox("all")))

        # Configurar o Canvas para ajustar o tamanho da janela
        self.config_canvas.bind("<Configure>", lambda e: self.config_canvas.config(width=self.scrollable_config_frame.winfo_width()))

        # Frame para configuração do logo
        logo_frame = tk.LabelFrame(self.scrollable_config_content, text="Configuração do Logo", padx=10, pady=10)
        logo_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        logo_frame.columnconfigure(1, weight=1)

        tk.Label(logo_frame, text="Caminho do Logo").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        self.logo_path_entry = tk.Entry(logo_frame, width=60, state='readonly')
        self.logo_path_entry.grid(row=0, column=1, padx=10, pady=5, sticky=tk.EW)

        self.selecionar_logo_btn = tk.Button(logo_frame, text="Selecionar Logo", command=self.selecionar_logo)
        self.selecionar_logo_btn.grid(row=1, column=0, pady=10, padx=10, sticky=tk.W)

        self.remover_logo_btn = tk.Button(logo_frame, text="Remover Logo", command=self.remover_logo)
        self.remover_logo_btn.grid(row=1, column=1, pady=10, padx=10, sticky=tk.E)

        # Frame para configuração do cabeçalho e nome do estabelecimento
        cabecalho_frame = tk.LabelFrame(self.scrollable_config_content, text="Configuração do Pedido", padx=10, pady=10)
        cabecalho_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        cabecalho_frame.columnconfigure(1, weight=1)

        tk.Label(cabecalho_frame, text="Cabeçalho do Pedido").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        self.cabecalho_pedido_entry = tk.Entry(cabecalho_frame, width=88)
        self.cabecalho_pedido_entry.grid(row=0, column=1, padx=10, pady=5, sticky=tk.EW)

        tk.Label(cabecalho_frame, text="Nome do Estabelecimento").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        self.nome_estabelecimento_entry = tk.Entry(cabecalho_frame, width=60)
        self.nome_estabelecimento_entry.grid(row=1, column=1, padx=10, pady=5, sticky=tk.EW)

        # Frame para configuração da impressora
        impressora_frame = tk.LabelFrame(self.scrollable_config_content, text="Configuração da Impressora", padx=10, pady=10)
        impressora_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        impressora_frame.columnconfigure(1, weight=1)

        tk.Label(impressora_frame, text="Selecionar Impressora").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        self.printer_var = tk.StringVar()
        self.printer_combobox = ttk.Combobox(impressora_frame, textvariable=self.printer_var)
        self.printer_combobox.grid(row=0, column=1, padx=10, pady=5, sticky=tk.EW)
        self.printer_combobox.bind("<<ComboboxSelected>>", self.atualizar_impressora_selecionada)

        # Botão para atualizar a lista de impressoras
        self.atualizar_lista_btn = tk.Button(impressora_frame, text="Atualizar Lista", command=self.atualizar_lista_impressoras)
        self.atualizar_lista_btn.grid(row=0, column=2, padx=10, pady=5)

        tk.Label(impressora_frame, text="Vendor ID").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        self.vendor_id_entry = tk.Entry(impressora_frame, width=30)
        self.vendor_id_entry.grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)

        tk.Label(impressora_frame, text="Product ID").grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
        self.product_id_entry = tk.Entry(impressora_frame, width=30)
        self.product_id_entry.grid(row=2, column=1, padx=10, pady=5, sticky=tk.W)

        # Checkbutton para entrada manual dos IDs
        self.entrada_manual_var = tk.BooleanVar()
        self.entrada_manual_check = tk.Checkbutton(impressora_frame, text="Inserir manualmente", variable=self.entrada_manual_var, command=self.atualizar_estado_ids)
        self.entrada_manual_check.grid(row=3, column=0, columnspan=2, pady=10, padx=10, sticky=tk.W)

        # Label para mostrar a impressora selecionada
        self.impressora_selecionada_label = tk.Label(impressora_frame, text="Impressora Selecionada: Nenhuma")
        self.impressora_selecionada_label.grid(row=4, column=0, columnspan=3, pady=10, padx=10, sticky=tk.W)

        # Garanta que o Frame de rolagem se ajuste ao Canvas
        self.scrollable_config_frame.grid_rowconfigure(0, weight=1)
        self.scrollable_config_frame.grid_columnconfigure(0, weight=1)

        # Botão para salvar as configurações
        self.salvar_configuracao_btn = tk.Button(self.configuracao_tab, text="Salvar Configuração", command=self.salvar_configuracao)
        self.salvar_configuracao_btn.grid(row=3, column=0, columnspan=2, pady=10)


        # Botão Adicionar Pedido
        self.adicionar_pedido_btn = tk.Button(self.adicionar_pedido_tab, text="Adicionar Pedido", command=self.adicionar_pedido)
        self.adicionar_pedido_btn.grid(row=12, column=0, columnspan=2, pady=10)

        self.carregar_configuracao()
        self.atualizar_lista_impressoras()
        self.atualizar_estado_ids()

    def atualizar_lista_impressoras(self):
        self.usb_printers = self.listar_impressoras_usb()
        self.printer_combobox.config(values=self.usb_printers)
        if not self.usb_printers:
            self.printer_var.set("")
        else:
            self.printer_var.set(self.usb_printers[0] if self.usb_printers else "")

    def atualizar_impressora_selecionada(self, event):
        selecionado = self.printer_var.get()
        self.impressora_selecionada_label.config(text=f"Impressora Selecionada: {selecionado}")
        # Atualiza o estado dos campos conforme a seleção
        self.atualizar_estado_ids()

    def atualizar_estado_ids(self):
        if self.entrada_manual_var.get():
            self.vendor_id_entry.config(state='normal')
            self.product_id_entry.config(state='normal')
        else:
            self.vendor_id_entry.config(state='disabled')
            self.product_id_entry.config(state='disabled')

    def listar_impressoras_usb(self):
        dispositivos = usb.core.find(find_all=True)
        impressoras = []
        for dispositivo in dispositivos:
            try:
                if dispositivo.bDeviceClass == 7:
                    nome = usb.util.get_string(dispositivo, dispositivo.iProduct) if dispositivo.iProduct else "Desconhecido"
                    impressoras.append(f"{nome} (Vendor ID: {hex(dispositivo.idVendor)}, Product ID: {hex(dispositivo.idProduct)})")
                elif dispositivo.bDeviceClass == 0:
                    for config in dispositivo:
                        for interface in config:
                            if interface.bInterfaceClass == 7:
                                nome = usb.util.get_string(dispositivo, dispositivo.iProduct) if dispositivo.iProduct else "Desconhecido"
                                impressoras.append(f"{nome} (Vendor ID: {hex(dispositivo.idVendor)}, Product ID: {hex(dispositivo.idProduct)})")
                                break
                print(f"Dispositivo encontrado: Vendor ID = {hex(dispositivo.idVendor)}, Product ID = {hex(dispositivo.idProduct)}, Classe = {dispositivo.bDeviceClass}")
            except usb.core.USBError as e:
                print(f"Erro ao acessar dispositivo USB: {e}")
            except ValueError:
                print(f"Não foi possível acessar o nome do dispositivo: Vendor ID = {hex(dispositivo.idVendor)}, Product ID = {hex(dispositivo.idProduct)}")
        if not impressoras:
            print("Nenhuma impressora USB encontrada.")
        return impressoras



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
                "nome_estabelecimento": self.nome_estabelecimento_entry.get(),
                "printer_vendor_id": int(self.vendor_id_entry.get(), 16) if self.vendor_id_entry.get() else 0x04b8,
                "printer_product_id": int(self.product_id_entry.get(), 16) if self.product_id_entry.get() else 0x0e03,
                "impressora_selecionada": self.printer_var.get()  # Adiciona a impressora selecionada
            }

            # Salvar as configurações em um arquivo JSON
            with open("config.json", "w") as arquivo:
                json.dump(configuracoes, arquivo, indent=4)

            # Atualizar o label com a impressora selecionada
            impressora_selecionada = self.printer_var.get() or "Nenhuma"
            self.impressora_selecionada_label.config(text=f"Impressora Selecionada: {impressora_selecionada}")

            # Informar ao usuário que a configuração foi salva com sucesso
            tk.messagebox.showinfo("Configuração", "Configuração salva com sucesso!")
        except Exception as e:
            print(f"Erro ao salvar configuração: {e}")
            tk.messagebox.showerror("Erro", "Não foi possível salvar a configuração.")





    def carregar_configuracao(self):
        try:
            with open("config.json", "r") as arquivo:
                config = json.load(arquivo)
                self.logo_path_entry.config(state='normal')  # Permitir edição para carregar o caminho
                self.logo_path_entry.delete(0, tk.END)
                self.logo_path_entry.insert(0, config.get("logo_path", ""))
                self.logo_path_entry.config(state='readonly')  # Voltar para somente leitura

                self.cabecalho_pedido_entry.delete(0, tk.END)
                self.cabecalho_pedido_entry.insert(0, config.get("cabecalho_pedido", ""))

                self.nome_estabelecimento_entry.delete(0, tk.END)
                self.nome_estabelecimento_entry.insert(0, config.get("nome_estabelecimento", ""))

                self.vendor_id_entry.delete(0, tk.END)
                self.vendor_id_entry.insert(0, format(config.get("printer_vendor_id", 0x04b8), '04x').upper())

                self.product_id_entry.delete(0, tk.END)
                self.product_id_entry.insert(0, format(config.get("printer_product_id", 0x0e03), '04x').upper())

                # Atualizar a combobox com a impressora selecionada
                impressora_selecionada = config.get("impressora_selecionada", "Nenhuma")
                self.printer_var.set(impressora_selecionada)
                self.impressora_selecionada_label.config(text=f"Impressora Selecionada: {impressora_selecionada}")

        except FileNotFoundError:
            # Configurações padrão em caso de arquivo não encontrado
            self.logo_path_entry.config(state='normal')
            self.logo_path_entry.delete(0, tk.END)
            self.logo_path_entry.insert(0, "")

            self.cabecalho_pedido_entry.delete(0, tk.END)
            self.cabecalho_pedido_entry.insert(0, "Cabeçalho não configurado")

            self.nome_estabelecimento_entry.delete(0, tk.END)
            self.nome_estabelecimento_entry.insert(0, "Estabelecimento não configurado")

            self.vendor_id_entry.delete(0, tk.END)
            self.vendor_id_entry.insert(0, "04B8")

            self.product_id_entry.delete(0, tk.END)
            self.product_id_entry.insert(0, "0E03")

            self.printer_var.set("Nenhuma")
            self.impressora_selecionada_label.config(text="Impressora Selecionada: Nenhuma")




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
        self.adicionar_pedido_tab.grid_columnconfigure(0, weight=1)

        # Frame para a rolagem
        self.scrollable_frame = tk.Frame(self.adicionar_pedido_tab)
        self.scrollable_frame.grid(row=1, column=0, sticky="nsew")

        # Canvas para a rolagem
        self.canvas = tk.Canvas(self.scrollable_frame, borderwidth=0, highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        # Scrollbar para a rolagem
        self.scrollbar = tk.Scrollbar(self.scrollable_frame, orient="vertical", command=self.canvas.yview)
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Frame que será colocado dentro do Canvas
        self.scrollable_frame_content = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.scrollable_frame_content, anchor="nw")

        # Atualiza o scrollregion do canvas quando o conteúdo é modificado
        self.scrollable_frame_content.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # Garanta que o Frame de rolagem se ajuste ao Canvas
        self.scrollable_frame.grid_rowconfigure(0, weight=1)
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        # Configurar o Canvas para ajustar o tamanho da janela
        self.canvas.bind("<Configure>", lambda e: self.canvas.config(width=self.scrollable_frame.winfo_width()))

        # Adicione widgets ao self.scrollable_frame_content
        self.comprador_frame = tk.LabelFrame(self.scrollable_frame_content, text="Comprador", padx=10, pady=10)
        self.comprador_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.comprador_frame.columnconfigure(1, weight=1)

        tk.Label(self.comprador_frame, text="Nome").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        self.nome_entry = tk.Entry(self.comprador_frame, width=50)
        self.nome_entry.grid(row=0, column=1, padx=10, pady=5, sticky=tk.EW)

        # Garanta que o frame e os widgets se ajustem ao tamanho da janela
        self.scrollable_frame_content.grid_rowconfigure(0, weight=1)
        self.scrollable_frame_content.grid_columnconfigure(0, weight=1)




    
        # Telefone
        tk.Label(self.comprador_frame, text="Telefone").grid(row=3, column=0, padx=10, pady=5, sticky=tk.W)
        self.telefone_entry = tk.Entry(self.comprador_frame, width=25)  # Ajustando a largura do campo de telefone
        self.telefone_entry.grid(row=3, column=1, padx=10, pady=5, sticky=tk.W)

        # Configurar os pesos das linhas e colunas do `scrollable_frame`
        self.scrollable_frame.grid_rowconfigure(0, weight=1)
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
       
        # Pedidos frame
        self.pedidos_frame = tk.LabelFrame(self.scrollable_frame_content, text="Pedidos", padx=10, pady=10)
        self.pedidos_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew", columnspan=2)
        self.pedidos_frame.columnconfigure(1, weight=1)

        # Frame interno para pedidos
        self.pedidos_inner_frame = tk.Frame(self.pedidos_frame)
        self.pedidos_inner_frame.grid(row=0, column=0, padx=10, pady=5, sticky=tk.EW, columnspan=2)

        # Frame para os botões
        self.botoes_frame = tk.Frame(self.pedidos_frame)
        self.botoes_frame.grid(row=1, column=0, columnspan=2, pady=10, padx=5, sticky=tk.EW)

        # Inicializa a lista de entradas de pedido
        self.pedido_entries = []

        # Botão Adicionar Pedido
        self.add_pedido_btn = tk.Button(self.botoes_frame, text="Adicionar Outro Pedido", command=self.add_pedido_entry)
        self.add_pedido_btn.grid(row=0, column=0, pady=10, padx=5, sticky=tk.W)
        
        # Botão Excluir Pedido
        self.del_pedido_btn = tk.Button(self.botoes_frame, text="Excluir Último Pedido", command=self.del_pedido_entry)
        self.del_pedido_btn.grid(row=0, column=1, pady=10, padx=5, sticky=tk.W)
        self.del_pedido_btn.grid_remove()  # Esconda o botão inicialmente

        # Adiciona o primeiro pedido
        self.add_pedido_entry()

        # Cartao
        tk.Label(self.pedidos_frame, text= "Cartão").grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
        pedidos_frame = tk.Frame(self.pedidos_frame)
        pedidos_frame.grid(row=2, column=1, padx=10, pady=5, sticky=tk.EW)
        self.cartao_var = tk.StringVar(value="Nao")
        tk.Radiobutton(pedidos_frame, text="Sim", variable=self.cartao_var, value="Sim").pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(pedidos_frame, text="Nao", variable=self.cartao_var, value="Nao").pack(side=tk.LEFT, padx=5)

        # Contato
        tk.Label(self.pedidos_frame, text="Pedido realizado por").grid(row=3, column=0, padx=10, pady=5, sticky=tk.W)
        pedidos_frame = tk.Frame(self.pedidos_frame)
        pedidos_frame.grid(row=3, column=1, padx=10, pady=5, sticky=tk.EW)
        self.contato_var = tk.StringVar(value="WhatsApp")
        tk.Radiobutton(pedidos_frame, text="Telefone", variable=self.contato_var, value="Telefone").pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(pedidos_frame, text="WhatsApp", variable=self.contato_var, value="WhatsApp").pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(pedidos_frame, text="Loja", variable=self.contato_var, value="Loja").pack(side=tk.LEFT, padx=5)

        # Destinatário Frame
        self.destinatario_frame = tk.LabelFrame(self.scrollable_frame_content, text="Destinatário", padx=10, pady=10)
        self.destinatario_frame.grid(row=6, column=0, padx=10, pady=10, sticky="ew", columnspan=2)
        self.destinatario_frame.columnconfigure(1, weight=1)

        # Nome do Destinatário
        tk.Label(self.destinatario_frame, text="Nome do Destinatário").grid(row=6, column=0, padx=10, pady=5, sticky=tk.W)
        self.destinatario_entry = tk.Entry(self.destinatario_frame, width=50)
        self.destinatario_entry.grid(row=6, column=1, padx=10, pady=5, sticky=tk.EW)

        # Telefone do Destinatário
        tk.Label(self.destinatario_frame, text="Telefone do Destinatário").grid(row=7, column=0, padx=10, pady=5, sticky=tk.W)
        self.telefone_destinatario_entry = tk.Entry(self.destinatario_frame, width=25)
        self.telefone_destinatario_entry.grid(row=7, column=1, padx=10, pady=5, sticky=tk.W)

        # Endereço de Entrega
        tk.Label(self.destinatario_frame, text="Endereço de Entrega").grid(row=8, column=0, padx=10, pady=5, sticky=tk.W)
        self.endereco_entry = tk.Entry(self.destinatario_frame, width=50)
        self.endereco_entry.grid(row=8, column=1, padx=10, pady=5, sticky=tk.EW)

        # Referência
        tk.Label(self.destinatario_frame, text="Referência").grid(row=9, column=0, padx=10, pady=5, sticky=tk.W)
        self.referencia_entry = tk.Entry(self.destinatario_frame, width=50)
        self.referencia_entry.grid(row=9, column=1, padx=10, pady=5, sticky=tk.EW)

        # Data de Entrega
        tk.Label(self.destinatario_frame, text="Data de Entrega").grid(row=10, column=0, padx=10, pady=5, sticky=tk.W)
        self.data_entrega_entry = DateEntry(self.destinatario_frame, date_pattern='dd/MM/yyyy', width=12)
        self.data_entrega_entry.grid(row=10, column=1, padx=10, pady=5, sticky=tk.W)

        tk.Label(self.destinatario_frame, text="Hora de Entrega").grid(row=11, column=0, padx=10, pady=5, sticky=tk.W)
        self.hora_entrega_entry = tk.Frame(self.destinatario_frame)
        self.hora_entrega_entry.grid(row=11, column=1, padx=10, pady=5, sticky=tk.W)

        self.hora_var = tk.StringVar(value="00")
        self.minuto_var = tk.StringVar(value="00")
        tk.Spinbox(self.hora_entrega_entry, from_=0, to=23, textvariable=self.hora_var, width=3, format="%02.0f").grid(row=0, column=0)
        tk.Label(self.hora_entrega_entry, text=":").grid(row=0, column=1)
        tk.Spinbox(self.hora_entrega_entry, from_=0, to=59, textvariable=self.minuto_var, width=3, format="%02.0f").grid(row=0, column=2)

        # Garanta que o Canvas se ajuste ao redimensionar a janela
        self.adicionar_pedido_tab.grid_rowconfigure(1, weight=1)
        self.adicionar_pedido_tab.grid_columnconfigure(0, weight=1)

        # Botão Adicionar Pedido
        self.adicionar_pedido_btn = tk.Button(self.adicionar_pedido_tab, text="Adicionar Pedido", command=self.adicionar_pedido)
        self.adicionar_pedido_btn.grid(row=12, column=0, columnspan=2, pady=10)


    def add_pedido_entry(self):
        row = len(self.pedido_entries)
        pedido_label = tk.Label(self.pedidos_inner_frame, text=f"Pedido {row + 1}")
        pedido_label.grid(row=row, column=0, padx=10, pady=5, sticky=tk.W)
        pedido_entry = tk.Entry(self.pedidos_inner_frame, width=100)
        pedido_entry.grid(row=row, column=1, padx=10, pady=5, sticky=tk.W)
        self.pedido_entries.append((pedido_label, pedido_entry))

        # Atualizar a visibilidade do botão de excluir
        self.update_del_pedido_btn()

    def del_pedido_entry(self):
        if self.pedido_entries:
            label, entry = self.pedido_entries.pop()
            label.destroy()
            entry.destroy()

        # Atualizar a visibilidade do botão de excluir
        self.update_del_pedido_btn()

    def update_del_pedido_btn(self):
        # Esconder o botão de excluir se houver apenas um pedido
        if len(self.pedido_entries) <= 1:
            self.del_pedido_btn.grid_remove()
        else:
            self.del_pedido_btn.grid()


    def adicionar_pedido(self):
        resposta = messagebox.askyesno("Confirmar", "Deseja realmente adicionar este pedido?")
        if not resposta:
            return

        # Obter os valores dos pedidos
        pedidos = [entry.get() for _, entry in self.pedido_entries]
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
        self.telefone_entry.delete(0, tk.END)
        self.cartao_var.set("Nao")
        self.contato_var.set("WhatsApp")
        self.destinatario_entry.delete(0, tk.END)
        self.telefone_destinatario_entry.delete(0, tk.END)
        self.endereco_entry.delete(0, tk.END)
        self.referencia_entry.delete(0, tk.END)
        self.data_entrega_entry.set_date(datetime.now())
        self.hora_var.set("00")
        self.minuto_var.set("00")

        # Limpar os campos de pedido
        self.pedido_entries.clear()
        for widget in self.pedidos_inner_frame.winfo_children():
            widget.destroy()
        self.add_pedido_entry()




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

    def atualizar_idioma(idioma):
        # Atualiza os textos da interface com base no idioma selecionado
        with open('config.json', 'r') as file:
            config = json.load(file)
        config['idioma'] = idioma
        with open('config.json', 'w') as file:
            json.dump(config, file, indent=4)
        carregar_textos(idioma)

    # Função para carregar textos
    def carregar_textos(idioma):
        textos = {
            "pt": {
                "configuracao": "Configuração",
                "idioma": "Gerenciamento de Idiomas",
                "portugues": "Português",
                "ingles": "Inglês"
            },
            "en": {
                "configuracao": "Configuration",
                "idioma": "Language Management",
                "portugues": "Portuguese",
                "ingles": "English"
            }
        }
        textos_interface = textos[idioma]
        label_configuracao.config(text=textos_interface["configuracao"])
        label_idioma.config(text=textos_interface["idioma"])
        botao_portugues.config(text=textos_interface["portugues"])
        botao_ingles.config(text=textos_interface["ingles"])

    # Função para criar a interface
    def criar_interface():
        root = tk.Tk()
        root.title("Configuração")

        # Frame de configuração
        config_frame = LabelFrame(root, text="Configuração", padx=10, pady=10)
        config_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # LabelFrame para idiomas
        idioma_frame = LabelFrame(config_frame, text="Gerenciamento de Idiomas", padx=10, pady=10)
        idioma_frame.pack(padx=10, pady=10, fill="both", expand=True)

        idioma_var = StringVar(value="pt")
        
        # Botões de idioma
        botao_portugues = Radiobutton(idioma_frame, text="Português", variable=idioma_var, value="pt", command=lambda: atualizar_idioma("pt"))
        botao_portugues.pack(anchor="w")
        
        botao_ingles = Radiobutton(idioma_frame, text="Inglês", variable=idioma_var, value="en", command=lambda: atualizar_idioma("en"))
        botao_ingles.pack(anchor="w")
        
        # Labels para textos
        global label_configuracao, label_idioma
        label_configuracao = tk.Label(config_frame, text="")
        label_configuracao.pack(pady=5)
        
        label_idioma = tk.Label(idioma_frame, text="")
        label_idioma.pack(pady=5)

        # Carregar configuração inicial
        with open('config.json', 'r') as file:
            config = json.load(file)
        idioma = config.get('idioma', 'pt')
        carregar_textos(idioma)



if __name__ == "__main__":
    root = tk.Tk()
    app = PedidoApp(root)
    app.carregar_configuracao()  # Carregar configurações ao iniciar o app
    root.mainloop()
