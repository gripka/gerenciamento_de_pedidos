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
import locale
import customtkinter as ctk
import sv_ttk

import cProfile
import pstats
import io

import threading

class PedidoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gerenciador de Pedidos")
        self.root.geometry("990x680")
        
        # Aplicar o tema Sun Valley Light
        tema_inicial = "light"  
        sv_ttk.set_theme(tema_inicial)

        self.root.iconbitmap("icons/icogerenciamento2.ico")

        # Definir o tamanho mínimo da janela
        self.root.minsize(780, 680)

        # Obter a resolução do monitor
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Definir o tamanho máximo da janela
        self.root.maxsize(screen_width, screen_height)

        self.widget_cache = {}
        self.pedidos = []
        self.logo_path = ""

        self.tab_control = ttk.Notebook(root)

        self.lista_pedidos_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.lista_pedidos_tab, text="Lista de Pedidos")

        self.adicionar_pedido_tab = ttk.Frame(self.tab_control)
        self.configuracao_tab = ttk.Frame(self.tab_control)

        self.tab_control.add(self.adicionar_pedido_tab, text="Adicionar Pedido")
        self.tab_control.add(self.configuracao_tab, text="Configuração")

        self.tab_control.pack(expand=1, fill="both")

        # Seleciona a aba "Adicionar Pedido" ao iniciar o aplicativo
        self.tab_control.select(self.adicionar_pedido_tab)

        # Inicializar abas
        self.create_lista_pedidos_tab()
        self.create_adicionar_pedido_tab()
        self.create_configuracao_tab()

        self.carregar_pedidos()
        self.atualizar_lista_pedidos()

        # Vincular evento de mudança de aba
        self.tab_control.bind("<<NotebookTabChanged>>", self.on_tab_change)

    def on_tab_change(self, event):
        selected_tab = event.widget.select()
        tab_text = event.widget.tab(selected_tab, "text")
        if tab_text == "Lista de Pedidos":
            self.atualizar_lista_pedidos()
        elif tab_text == "Configuração":
            self.atualizar_lista_impressoras()
            self.atualizar_estado_ids()

    def create_configuracao_tab(self):
        if "configuracao_tab" in self.widget_cache:
            self.configuracao_tab = self.widget_cache["configuracao_tab"]
        else:
            for widget in self.configuracao_tab.winfo_children():
                widget.destroy()

            # Frame para a rolagem
            self.scrollable_config_frame = ttk.Frame(self.configuracao_tab)
            self.scrollable_config_frame.grid(row=0, column=0, sticky="nsew")
            self.configuracao_tab.grid_rowconfigure(0, weight=1)
            self.configuracao_tab.grid_columnconfigure(0, weight=1)

            # Canvas para a rolagem
            self.config_canvas = tk.Canvas(self.scrollable_config_frame, borderwidth=0, highlightthickness=0)
            self.config_canvas.grid(row=0, column=0, sticky="nsew")

            # Scrollbar para a rolagem
            self.config_scrollbar = ttk.Scrollbar(self.scrollable_config_frame, orient="vertical", command=self.config_canvas.yview)
            self.config_scrollbar.grid(row=0, column=1, sticky="ns")
            self.config_canvas.configure(yscrollcommand=self.config_scrollbar.set)

            # Frame que será colocado dentro do Canvas
            self.scrollable_config_content = ttk.Frame(self.config_canvas)
            self.config_canvas.create_window((0, 0), window=self.scrollable_config_content, anchor="nw")

            # Atualiza o scrollregion do canvas quando o conteúdo é modificado
            self.scrollable_config_content.bind("<Configure>", lambda e: self.config_canvas.configure(scrollregion=self.config_canvas.bbox("all")))

            # Configurar o Canvas para ajustar o tamanho da janela
            self.config_canvas.bind("<Configure>", lambda e: self.config_canvas.config(width=self.scrollable_config_frame.winfo_width()))

            # Frame para configuração do logo
            logo_frame = ttk.LabelFrame(self.scrollable_config_content, text="Configuração do Logo", padding=(10, 10))
            logo_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
            logo_frame.columnconfigure(1, weight=1)

            ttk.Label(logo_frame, text="Caminho do Logo").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
            self.logo_path_entry = ttk.Entry(logo_frame, width=60, state='readonly')
            self.logo_path_entry.grid(row=0, column=1, padx=10, pady=5, sticky=tk.EW)

            self.selecionar_logo_btn = ttk.Button(logo_frame, text="Selecionar Logo", command=self.selecionar_logo)
            self.selecionar_logo_btn.grid(row=1, column=0, pady=10, padx=10, sticky=tk.W)

            self.remover_logo_btn = ttk.Button(logo_frame, text="Remover Logo", command=self.remover_logo)
            self.remover_logo_btn.grid(row=1, column=1, pady=10, padx=10, sticky=tk.E)

            # Frame para configuração do cabeçalho e nome do estabelecimento
            cabecalho_frame = ttk.LabelFrame(self.scrollable_config_content, text="Configuração do Pedido", padding=(10, 10))
            cabecalho_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
            cabecalho_frame.columnconfigure(1, weight=1)

            ttk.Label(cabecalho_frame, text="Cabeçalho do Pedido").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
            self.cabecalho_pedido_entry = ttk.Entry(cabecalho_frame, width=88)
            self.cabecalho_pedido_entry.grid(row=0, column=1, padx=10, pady=5, sticky=tk.EW)

            ttk.Label(cabecalho_frame, text="Nome do Estabelecimento").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
            self.nome_estabelecimento_entry = ttk.Entry(cabecalho_frame, width=60)
            self.nome_estabelecimento_entry.grid(row=1, column=1, padx=10, pady=5, sticky=tk.EW)

            # Frame para configuração da impressora
            impressora_frame = ttk.LabelFrame(self.scrollable_config_content, text="Configuração da Impressora", padding=(10, 10))
            impressora_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
            impressora_frame.columnconfigure(1, weight=1)

            ttk.Label(impressora_frame, text="Selecionar Impressora").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
            self.printer_var = tk.StringVar()
            self.printer_combobox = ttk.Combobox(impressora_frame, textvariable=self.printer_var)
            self.printer_combobox.grid(row=0, column=1, padx=10, pady=5, sticky=tk.EW)
            self.printer_combobox.bind("<<ComboboxSelected>>", self.atualizar_impressora_selecionada)

            # Botão para atualizar a lista de impressoras
            self.atualizar_lista_btn = ttk.Button(impressora_frame, text="Atualizar Lista", command=self.atualizar_lista_impressoras)
            self.atualizar_lista_btn.grid(row=0, column=2, padx=10, pady=5)

            ttk.Label(impressora_frame, text="Vendor ID").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
            self.vendor_id_entry = ttk.Entry(impressora_frame, width=30)
            self.vendor_id_entry.grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)

            ttk.Label(impressora_frame, text="Product ID").grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
            self.product_id_entry = ttk.Entry(impressora_frame, width=30)
            self.product_id_entry.grid(row=2, column=1, padx=10, pady=5, sticky=tk.W)

            # Checkbutton para entrada manual dos IDs
            self.entrada_manual_var = tk.BooleanVar()
            self.entrada_manual_check = ttk.Checkbutton(impressora_frame, text="Inserir manualmente", variable=self.entrada_manual_var, command=self.atualizar_estado_ids)
            self.entrada_manual_check.grid(row=3, column=0, columnspan=2, pady=10, padx=10, sticky=tk.W)

            # Label para mostrar a impressora selecionada
            self.impressora_selecionada_label = ttk.Label(impressora_frame, text="Impressora Selecionada: Nenhuma")
            self.impressora_selecionada_label.grid(row=4, column=0, columnspan=3, pady=10, padx=10, sticky=tk.W)

            # Frame para seleção de tema
            tema_frame = ttk.LabelFrame(self.scrollable_config_content, text="Selecionar Tema", padding=(10, 10))
            tema_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
            tema_frame.columnconfigure(1, weight=1)

            self.tema_var = tk.StringVar(value=sv_ttk.get_theme())
            ttk.Radiobutton(tema_frame, text="Claro", variable=self.tema_var, value="light", command=self.mudar_tema).grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
            ttk.Radiobutton(tema_frame, text="Escuro", variable=self.tema_var, value="dark", command=self.mudar_tema).grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)

            # Garanta que o Frame de rolagem se ajuste ao Canvas
            self.scrollable_config_frame.grid_rowconfigure(0, weight=1)
            self.scrollable_config_frame.grid_columnconfigure(0, weight=1)

            # Botão para salvar as configurações
            self.salvar_configuracao_btn = ttk.Button(self.configuracao_tab, text="Salvar Configuração", command=self.salvar_configuracao)
            self.salvar_configuracao_btn.grid(row=3, column=0, columnspan=2, pady=10)

            self.carregar_configuracao()
            self.atualizar_lista_impressoras()
            self.atualizar_estado_ids()
            self.widget_cache["configuracao_tab"] = self.configuracao_tab
    
    def mudar_tema(self):
        tema_selecionado = self.tema_var.get()
        sv_ttk.set_theme(tema_selecionado)
        self.atualizar_estilos()

    def atualizar_estilos(self):
        # Ajustar estilos dos widgets na lista de pedidos
        estilo_treeview = ttk.Style()
        estilo_treeview.configure("Treeview", background="white" if sv_ttk.get_theme() == "light" else "black",
                                foreground="black" if sv_ttk.get_theme() == "light" else "white",
                                fieldbackground="white" if sv_ttk.get_theme() == "light" else "black")
        estilo_treeview.configure("Treeview.Heading", background="white" if sv_ttk.get_theme() == "light" else "black",
                                foreground="black" if sv_ttk.get_theme() == "light" else "white")
    
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
                "impressora_selecionada": self.printer_var.get(),  # Adiciona a impressora selecionada
                "tema": self.tema_var.get()  # Adiciona o tema selecionado
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

                # Carregar e aplicar o tema salvo
                tema_selecionado = config.get("tema", "light")
                self.tema_var.set(tema_selecionado)
                sv_ttk.set_theme(tema_selecionado)
                self.atualizar_estilos()
        
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

            # Tema padrão
            self.tema_var.set("light")
            sv_ttk.set_theme("light")
            self.atualizar_estilos()

    def create_lista_pedidos_tab(self):
        if "lista_pedidos_tab" in self.widget_cache:
            self.lista_pedidos_tab = self.widget_cache["lista_pedidos_tab"]
        else:
            # Configuração do layout da aba de lista de pedidos
            self.lista_pedidos_tab.grid_rowconfigure(0, weight=1)
            self.lista_pedidos_tab.grid_rowconfigure(1, weight=10)
            self.lista_pedidos_tab.grid_rowconfigure(2, weight=0)
            self.lista_pedidos_tab.grid_columnconfigure(0, weight=1)

            # Frame para agrupar o rótulo e a barra de busca
            search_frame = ttk.Frame(self.lista_pedidos_tab)
            search_frame.grid(row=0, column=0, columnspan=2, pady=5, padx=10, sticky=tk.EW)

            # Barra de Busca
            ttk.Label(search_frame, text="Buscar:").grid(row=0, column=0, pady=5, padx=(10, 5), sticky=tk.W)
            self.busca_entry = ttk.Entry(search_frame, width=50)
            self.busca_entry.grid(row=0, column=1, pady=5, padx=(5, 0), sticky=tk.EW)
            self.busca_entry.bind("<KeyRelease>", self.filtrar_pedidos)

            # Botão Editar Selecionado
            self.editar_btn = ttk.Button(search_frame, text="Editar Selecionado", command=self.editar_pedido_selecionado)
            self.editar_btn.grid(row=0, column=2, pady=10, padx=(10, 0), sticky=tk.W)

            # Configurar a coluna para expandir a barra de busca
            search_frame.grid_columnconfigure(1, weight=1)

            # Treeview para exibir os pedidos
            self.tree = ttk.Treeview(self.lista_pedidos_tab, columns=("Nome do Comprador", "Pedidos", "Data do Pedido", "Telefone", "Cartão", "Pedido realizado por", "Nome do Destinatário", "Telefone do Destinatário", "Endereço de Entrega", "Referência", "Data de Entrega", "Hora de Entrega"), show='headings')
            
            # Cabeçalhos das colunas
            col_widths = {
                "Nome do Comprador": 150,
                "Pedidos": 150,
                "Data do Pedido": 150,
                "Telefone": 120,
                "Cartão": 70,
                "Pedido realizado por": 150,
                "Nome do Destinatário": 150,
                "Telefone do Destinatário": 120,
                "Endereço de Entrega": 200,
                "Referência": 100,
                "Data de Entrega": 100,
                "Hora de Entrega": 100
            }
            
            for col, width in col_widths.items():
                self.tree.heading(col, text=col, command=lambda _col=col: self.sort_column(_col, False))
                self.tree.column(col, width=width, anchor=tk.W)
            
            self.tree.grid(row=1, column=0, columnspan=2, sticky="nsew")

            # Scrollbars
            self.scrollbar_y = ttk.Scrollbar(self.lista_pedidos_tab, orient=tk.VERTICAL, command=self.tree.yview)
            self.scrollbar_y.grid(row=1, column=2, sticky="ns")
            self.tree.config(yscrollcommand=self.scrollbar_y.set)
            
            self.scrollbar_x = ttk.Scrollbar(self.lista_pedidos_tab, orient=tk.HORIZONTAL, command=self.tree.xview)
            self.scrollbar_x.grid(row=2, column=0, columnspan=2, sticky="ew")
            self.tree.config(xscrollcommand=self.scrollbar_x.set)

            # Botões
            self.imprimir_btn = ttk.Button(self.lista_pedidos_tab, text="Imprimir Selecionados", command=self.imprimir_pedidos_selecionados)
            self.imprimir_btn.grid(row=3, column=0, pady=10, padx=10, sticky=tk.W)
            
            self.apagar_btn = ttk.Button(self.lista_pedidos_tab, text="Apagar Selecionados", command=self.apagar_pedidos_selecionados)
            self.apagar_btn.grid(row=3, column=1, pady=10, padx=10, sticky=tk.E)

            # Atualizar a lista de pedidos
            self.atualizar_lista_pedidos()
            self.widget_cache["lista_pedidos_tab"] = self.lista_pedidos_tab

    def editar_pedido_selecionado(self):
        # Obter o item selecionado no Treeview
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Nenhum pedido selecionado.")
            return

        # Obter o índice do pedido selecionado
        pedido_index = self.tree.index(selected_item[0])
        pedido = self.pedidos[pedido_index]

        # Chamar abrir_modal_edicao com pedido e pedido_index
        self.abrir_modal_edicao(pedido, pedido_index)

    def abrir_modal_edicao(self, pedido, pedido_index):
        modal = tk.Toplevel(self.root)
        modal.title("Editar Pedido")

        # Definir o ícone do modal
        modal.iconbitmap("icons/icogerenciamento2.ico")

        # Configurar o modal para bloquear a janela de fundo
        modal.transient(self.root)
        modal.grab_set()

        # Campos de edição
        ttk.Label(modal, text="Nome do Comprador").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        self.nome_entry = ttk.Entry(modal, width=40)
        self.nome_entry.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)
        self.nome_entry.insert(0, pedido["Nome do Comprador"])

        ttk.Label(modal, text="Telefone").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        self.telefone_entry = ttk.Entry(modal, width=40)
        self.telefone_entry.grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)
        self.telefone_entry.insert(0, pedido["Telefone"])

        # Inicializar os campos de pedidos
        self.pedido_entries = []
        self.pedidos_inner_frame = ttk.Frame(modal)
        self.pedidos_inner_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky=tk.W)

        for i, pedido_item in enumerate(pedido["Pedidos"]):
            pedido_label = ttk.Label(self.pedidos_inner_frame, text=f"Pedido {i + 1}")
            pedido_label.grid(row=i, column=0, padx=10, pady=5, sticky=tk.W)
            pedido_entry = ttk.Entry(self.pedidos_inner_frame, width=40)
            pedido_entry.grid(row=i, column=1, padx=10, pady=5, sticky=tk.W)
            pedido_entry.insert(0, pedido_item)
            self.pedido_entries.append((pedido_label, pedido_entry))

        # Botões para adicionar e remover pedidos
        self.botoes_frame = ttk.Frame(modal)
        self.botoes_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky=tk.W)

        self.add_pedido_btn = ttk.Button(self.botoes_frame, text="Adicionar Outro Pedido", command=self.add_pedido_entry_modal)
        self.add_pedido_btn.grid(row=0, column=0, pady=10, padx=5, sticky=tk.W)

        self.del_pedido_btn = ttk.Button(self.botoes_frame, text="Excluir Último Pedido", command=self.del_pedido_entry_modal)
        self.del_pedido_btn.grid(row=0, column=1, pady=10, padx=5, sticky=tk.W)
        if len(self.pedido_entries) <= 1:
            self.del_pedido_btn.grid_remove()

        # Cartão
        ttk.Label(modal, text="Cartão").grid(row=4, column=0, padx=10, pady=5, sticky=tk.W)
        cartao_frame = ttk.Frame(modal)
        cartao_frame.grid(row=4, column=1, padx=10, pady=5, sticky=tk.W)
        self.cartao_var = tk.StringVar(value=pedido["Cartão"])
        ttk.Radiobutton(cartao_frame, text="Sim", variable=self.cartao_var, value="Sim").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(cartao_frame, text="Nao", variable=self.cartao_var, value="Nao").pack(side=tk.LEFT, padx=5)

        # Pedido realizado por
        ttk.Label(modal, text="Pedido realizado por").grid(row=5, column=0, padx=10, pady=5, sticky=tk.W)
        contato_frame = ttk.Frame(modal)
        contato_frame.grid(row=5, column=1, padx=10, pady=5, sticky=tk.W)
        self.contato_var = tk.StringVar(value=pedido["Pedido realizado por"])
        ttk.Radiobutton(contato_frame, text="Telefone", variable=self.contato_var, value="Telefone").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(contato_frame, text="WhatsApp", variable=self.contato_var, value="WhatsApp").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(contato_frame, text="Loja", variable=self.contato_var, value="Loja").pack(side=tk.LEFT, padx=5)

        ttk.Label(modal, text="Nome do Destinatário").grid(row=6, column=0, padx=10, pady=5, sticky=tk.W)
        self.destinatario_entry = ttk.Entry(modal, width=40)
        self.destinatario_entry.grid(row=6, column=1, padx=10, pady=5, sticky=tk.W)
        self.destinatario_entry.insert(0, pedido["Nome do Destinatário"])

        ttk.Label(modal, text="Telefone do Destinatário").grid(row=7, column=0, padx=10, pady=5, sticky=tk.W)
        self.telefone_destinatario_entry = ttk.Entry(modal, width=40)
        self.telefone_destinatario_entry.grid(row=7, column=1, padx=10, pady=5, sticky=tk.W)
        self.telefone_destinatario_entry.insert(0, pedido["Telefone do Destinatário"])

        ttk.Label(modal, text="Endereço de Entrega").grid(row=8, column=0, padx=10, pady=5, sticky=tk.W)
        self.endereco_entry = ttk.Entry(modal, width=40)
        self.endereco_entry.grid(row=8, column=1, padx=10, pady=5, sticky=tk.W)
        self.endereco_entry.insert(0, pedido["Endereço de Entrega"])

        ttk.Label(modal, text="Referência").grid(row=9, column=0, padx=10, pady=5, sticky=tk.W)
        self.referencia_entry = ttk.Entry(modal, width=40)
        self.referencia_entry.grid(row=9, column=1, padx=10, pady=5, sticky=tk.W)
        self.referencia_entry.insert(0, pedido["Referência"])

        # Data de Entrega
        ttk.Label(modal, text="Data de Entrega").grid(row=10, column=0, padx=10, pady=5, sticky=tk.W)
        self.data_entrega_entry = DateEntry(modal, width=12, date_pattern='dd/MM/yyyy', locale='pt_BR')
        self.data_entrega_entry.grid(row=10, column=1, padx=10, pady=5, sticky=tk.W)
        self.data_entrega_entry.set_date(datetime.strptime(pedido["Data de Entrega"], "%d/%m/%Y"))

        # Hora de Entrega
        ttk.Label(modal, text="Hora de Entrega").grid(row=11, column=0, padx=10, pady=5, sticky=tk.W)
        hora_entrega_frame = ttk.Frame(modal)
        hora_entrega_frame.grid(row=11, column=1, padx=10, pady=5, sticky=tk.W)

        self.hora_var = tk.StringVar(value=pedido["Hora de Entrega"].split(":")[0])
        self.minuto_var = tk.StringVar(value=pedido["Hora de Entrega"].split(":")[1])

        vcmd_hora = (modal.register(self.validate_hour), '%P')
        vcmd_minuto = (modal.register(self.validate_minute), '%P')

        ttk.Spinbox(hora_entrega_frame, from_=0, to=23, textvariable=self.hora_var, width=3, format="%02.0f", validate='key', validatecommand=vcmd_hora).grid(row=0, column=0, sticky=tk.W)
        ttk.Label(hora_entrega_frame, text=":").grid(row=0, column=1, sticky=tk.W)
        ttk.Spinbox(hora_entrega_frame, from_=0, to=59, textvariable=self.minuto_var, width=3, format="%02.0f", validate='key', validatecommand=vcmd_minuto).grid(row=0, column=2, sticky=tk.W)

        # Pagamento Realizado e Valor do Pedido
        pagamento_frame = ttk.Frame(modal)
        pagamento_frame.grid(row=12, column=0, columnspan=2, padx=10, pady=5, sticky=tk.W)

        self.pagamento_realizado_var = tk.IntVar(value=1 if pedido["Pagamento Realizado"] else 0)
        pagamento_checkbutton = ttk.Checkbutton(pagamento_frame, text="Pagamento Realizado", variable=self.pagamento_realizado_var, command=lambda: self.toggle_pagamento_entry(self.valor_pedido_entry, self.pagamento_realizado_var))
        pagamento_checkbutton.grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)

        valor_pedido_label = ttk.Label(pagamento_frame, text="Valor do Pedido")
        self.valor_pedido_entry = ttk.Entry(pagamento_frame, width=20, validate="key")
        valor_pedido_label.grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        self.valor_pedido_entry.grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)
        self.valor_pedido_entry.insert(0, pedido["Valor do Pedido"])

        # Vincular o evento de formatação ao campo de valor do pedido
        self.valor_pedido_entry.bind('<KeyRelease>', lambda event: self.formatar_valor(event, self.valor_pedido_entry))

        # Inicialmente, desabilite a entrada de valor do pedido se pagamento realizado estiver marcado
        self.toggle_pagamento_entry(self.valor_pedido_entry, self.pagamento_realizado_var)

        # Botão Salvar
        ttk.Button(modal, text="Salvar", command=lambda: self.salvar_edicao(pedido_index, modal), width=15).grid(row=13, column=0, columnspan=2, pady=10)
    
    def add_pedido_entry_modal(self):
        row = len(self.pedido_entries)
        pedido_label = tk.Label(self.pedidos_inner_frame, text=f"Pedido {row + 1}")
        pedido_label.grid(row=row, column=0, padx=10, pady=5, sticky=tk.W)
        pedido_entry = tk.Entry(self.pedidos_inner_frame, width=40)
        pedido_entry.grid(row=row, column=1, padx=10, pady=5, sticky=tk.W)
        self.pedido_entries.append((pedido_label, pedido_entry))
        if len(self.pedido_entries) > 1:
            self.del_pedido_btn.grid()

    def del_pedido_entry_modal(self):
        if self.pedido_entries:
            pedido_label, pedido_entry = self.pedido_entries.pop()
            pedido_label.destroy()
            pedido_entry.destroy()
        if len(self.pedido_entries) <= 1:
            self.del_pedido_btn.grid_remove()

    def salvar_edicao(self, pedido_index, modal):
        if messagebox.askyesno("Confirmação", "Você tem certeza que deseja salvar as alterações?"):
            # Atualizar os valores do pedido
            pedido = self.pedidos[pedido_index]
            pedido["Nome do Comprador"] = self.nome_entry.get()
            pedido["Telefone"] = self.telefone_entry.get()
            pedido["Pedidos"] = [pedido_entry.get() for _, pedido_entry in self.pedido_entries]
            pedido["Cartão"] = self.cartao_var.get()
            pedido["Pedido realizado por"] = self.contato_var.get()
            pedido["Nome do Destinatário"] = self.destinatario_entry.get()
            pedido["Telefone do Destinatário"] = self.telefone_destinatario_entry.get()
            pedido["Endereço de Entrega"] = self.endereco_entry.get()
            pedido["Referência"] = self.referencia_entry.get()
            pedido["Data de Entrega"] = self.data_entrega_entry.get_date().strftime("%d/%m/%Y")
            pedido["Hora de Entrega"] = f"{self.hora_var.get().zfill(2)}:{self.minuto_var.get().zfill(2)}"
            pedido["Pagamento Realizado"] = bool(self.pagamento_realizado_var.get())
            pedido["Valor do Pedido"] = self.valor_pedido_entry.get()

            # Atualizar o pedido correspondente na lista self.pedidos
            self.pedidos[pedido_index] = pedido

            # Salvar os pedidos atualizados no arquivo JSON
            self.salvar_pedidos()

            self.atualizar_lista_pedidos()
            modal.destroy()

    def sort_column(self, col, reverse):
        # Obtém os dados da Treeview
        data = [(self.tree.set(child, col), child) for child in self.tree.get_children('')]
        
        # Ordena os dados
        data.sort(reverse=reverse)
        
        # Reorganiza os itens na Treeview
        for index, (val, child) in enumerate(data):
            self.tree.move(child, '', index)
        
        # Alterna a ordem de classificação
        self.tree.heading(col, command=lambda: self.sort_column(col, not reverse))
    
    def create_adicionar_pedido_tab(self):
        if "adicionar_pedido_tab" in self.widget_cache:
            self.adicionar_pedido_tab = self.widget_cache["adicionar_pedido_tab"]
        else:
            # Configurar o layout da aba de adicionar pedidos
            self.adicionar_pedido_tab.grid_rowconfigure(0, weight=0)
            self.adicionar_pedido_tab.grid_rowconfigure(1, weight=1)
            self.adicionar_pedido_tab.grid_columnconfigure(0, weight=1)
            
            # Frame para a rolagem
            self.scrollable_frame = ttk.Frame(self.adicionar_pedido_tab)
            self.scrollable_frame.grid(row=1, column=0, sticky="nsew")
            
            # Canvas para a rolagem
            self.canvas = tk.Canvas(self.scrollable_frame, borderwidth=0, highlightthickness=0)
            self.canvas.grid(row=0, column=0, sticky="nsew")
            
            # Scrollbar para a rolagem
            self.scrollbar = ttk.Scrollbar(self.scrollable_frame, orient="vertical", command=self.canvas.yview)
            self.scrollbar.grid(row=0, column=1, sticky="ns")
            self.canvas.configure(yscrollcommand=self.scrollbar.set)
            
            # Frame que será colocado dentro do Canvas
            self.scrollable_frame_content = ttk.Frame(self.canvas)
            self.canvas.create_window((0, 0), window=self.scrollable_frame_content, anchor="nw")
            
            # Atualiza o scrollregion do canvas quando o conteúdo é modificado
            self.scrollable_frame_content.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
            
            # Garanta que o Frame de rolagem se ajuste ao Canvas
            self.scrollable_frame.grid_rowconfigure(0, weight=1)
            self.scrollable_frame.grid_columnconfigure(0, weight=1)
            
            # Configurar o Canvas para ajustar o tamanho da janela
            self.canvas.bind("<Configure>", lambda e: self.canvas.config(width=self.scrollable_frame.winfo_width()))
            
            # Frame do Comprador
            self.comprador_frame = ttk.LabelFrame(self.scrollable_frame_content, text="Comprador", padding=(10, 10), style="Custom.TLabelframe")
            self.comprador_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew", columnspan=2)
            self.comprador_frame.columnconfigure(1, weight=1)

            # Nome do Comprador
            ttk.Label(self.comprador_frame, text="Nome", style="Custom.TLabel").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
            self.nome_entry = ttk.Entry(self.comprador_frame, width=50, style="Custom.TEntry")
            self.nome_entry.grid(row=0, column=1, padx=10, pady=5, sticky=tk.EW)

            # Telefone
            ttk.Label(self.comprador_frame, text="Telefone", style="Custom.TLabel").grid(row=3, column=0, padx=10, pady=5, sticky=tk.W)
            self.telefone_entry = ttk.Entry(self.comprador_frame, width=25, style="Custom.TEntry")
            self.telefone_entry.grid(row=3, column=1, padx=10, pady=5, sticky=tk.EW)

            # Configurar o peso das colunas e linhas do grid para que elas se expandam
            self.scrollable_frame_content.columnconfigure(0, weight=1)
            self.scrollable_frame_content.rowconfigure(0, weight=1)
            self.adicionar_pedido_tab.columnconfigure(0, weight=1)
            self.adicionar_pedido_tab.rowconfigure(1, weight=1)

            # Ajustar o tamanho do LabelFrame e dos campos de entrada ao redimensionar a janela
            self.adicionar_pedido_tab.bind("<Configure>", self._resize_widgets)

            
            # Pedidos frame
            self.pedidos_frame = ttk.LabelFrame(self.scrollable_frame_content, text="Pedidos", padding=(10, 10))
            self.pedidos_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew", columnspan=2)
            self.pedidos_frame.columnconfigure(1, weight=1)
            
            # Frame interno para pedidos
            self.pedidos_inner_frame = ttk.Frame(self.pedidos_frame)
            self.pedidos_inner_frame.grid(row=0, column=0, padx=10, pady=5, sticky=tk.EW, columnspan=2)
            
            # Frame para os botões
            self.botoes_frame = ttk.Frame(self.pedidos_frame)
            self.botoes_frame.grid(row=1, column=0, columnspan=2, pady=10, padx=5, sticky=tk.EW)
            
            # Inicializa a lista de entradas de pedido
            self.pedido_entries = []
            
            # Botão Adicionar Pedido
            self.add_pedido_btn = ttk.Button(self.botoes_frame, text="Adicionar Outro Pedido", command=self.add_pedido_entry)
            self.add_pedido_btn.grid(row=0, column=0, pady=10, padx=5, sticky=tk.W)
            
            # Botão Excluir Pedido
            self.del_pedido_btn = ttk.Button(self.botoes_frame, text="Excluir Último Pedido", command=self.del_pedido_entry)
            self.del_pedido_btn.grid(row=0, column=1, pady=10, padx=5, sticky=tk.W)
            self.del_pedido_btn.grid_remove()  # Esconda o botão inicialmente
            
            # Adiciona o primeiro pedido
            self.add_pedido_entry()
            
            # Cartao
            ttk.Label(self.pedidos_frame, text="Cartão").grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
            cartao_frame = ttk.Frame(self.pedidos_frame)
            cartao_frame.grid(row=2, column=1, padx=10, pady=5, sticky=tk.EW)
            self.cartao_var = tk.StringVar(value="Nao")
            ttk.Radiobutton(cartao_frame, text="Sim", variable=self.cartao_var, value="Sim").pack(side=tk.LEFT, padx=5)
            ttk.Radiobutton(cartao_frame, text="Nao", variable=self.cartao_var, value="Nao").pack(side=tk.LEFT, padx=5)
            
            # Contato
            ttk.Label(self.pedidos_frame, text="Pedido realizado por").grid(row=3, column=0, padx=10, pady=5, sticky=tk.W)
            contato_frame = ttk.Frame(self.pedidos_frame)
            contato_frame.grid(row=3, column=1, padx=10, pady=5, sticky=tk.EW)
            self.contato_var = tk.StringVar(value="WhatsApp")
            ttk.Radiobutton(contato_frame, text="Telefone", variable=self.contato_var, value="Telefone").pack(side=tk.LEFT, padx=5)
            ttk.Radiobutton(contato_frame, text="WhatsApp", variable=self.contato_var, value="WhatsApp").pack(side=tk.LEFT, padx=5)
            ttk.Radiobutton(contato_frame, text="Loja", variable=self.contato_var, value="Loja").pack(side=tk.LEFT, padx=5)
            
            # Pagamento Frame
            self.pagamento_frame = ttk.LabelFrame(self.scrollable_frame_content, text="Pagamento", padding=(10, 10))
            self.pagamento_frame.grid(row=5, column=0, padx=10, pady=10, sticky="ew", columnspan=2)
            self.pagamento_frame.columnconfigure(1, weight=1)
            
            # Opção de pagamento
            self.pagamento_realizado_var = tk.IntVar(value=0)
            self.pagamento_checkbutton = ttk.Checkbutton(self.pagamento_frame, text="Pagamento Realizado", variable=self.pagamento_realizado_var, command=self.toggle_pagamento_entry)
            self.pagamento_checkbutton.grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
            
            # Campo para inserir o valor do pedido
            self.valor_pedido_label = ttk.Label(self.pagamento_frame, text="Valor do Pedido")
            self.valor_pedido_entry = ttk.Entry(self.pagamento_frame, width=20, validate="key")
            self.valor_pedido_label.grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
            self.valor_pedido_entry.grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)
            
            # Vincular o evento de formatação ao campo de valor do pedido
            self.valor_pedido_entry.bind('<KeyRelease>', self.formatar_valor)
            
            # Inicialmente, desabilite a entrada de valor do pedido
            self.toggle_pagamento_entry()
            
            # Destinatário Frame
            self.destinatario_frame = ttk.LabelFrame(self.scrollable_frame_content, text="Destinatário", padding=(10, 10))
            self.destinatario_frame.grid(row=6, column=0, padx=10, pady=10, sticky="ew", columnspan=2)
            self.destinatario_frame.columnconfigure(1, weight=1)
            
            # Nome do Destinatário
            ttk.Label(self.destinatario_frame, text="Nome do Destinatário").grid(row=6, column=0, padx=10, pady=5, sticky=tk.W)
            self.destinatario_entry = ttk.Entry(self.destinatario_frame, width=50)
            self.destinatario_entry.grid(row=6, column=1, padx=10, pady=5, sticky=tk.EW)
            
            # Telefone do Destinatário
            ttk.Label(self.destinatario_frame, text="Telefone do Destinatário").grid(row=7, column=0, padx=10, pady=5, sticky=tk.W)
            self.telefone_destinatario_entry = ttk.Entry(self.destinatario_frame, width=25)
            self.telefone_destinatario_entry.grid(row=7, column=1, padx=10, pady=5, sticky=tk.W)
            
            # Endereço de Entrega
            ttk.Label(self.destinatario_frame, text="Endereço de Entrega").grid(row=8, column=0, padx=10, pady=5, sticky=tk.W)
            self.endereco_entry = ttk.Entry(self.destinatario_frame, width=50)
            self.endereco_entry.grid(row=8, column=1, padx=10, pady=5, sticky=tk.EW)
            
            # Referência
            ttk.Label(self.destinatario_frame, text="Referência").grid(row=9, column=0, padx=10, pady=5, sticky=tk.W)
            self.referencia_entry = ttk.Entry(self.destinatario_frame, width=50)
            self.referencia_entry.grid(row=9, column=1, padx=10, pady=5, sticky=tk.EW)
            
            # Data de Entrega
            ttk.Label(self.destinatario_frame, text="Data de Entrega").grid(row=4, column=0, padx=10, pady=5, sticky=tk.W)
            self.data_entrega_entry = DateEntry(
                self.destinatario_frame,
                date_pattern='dd/MM/yyyy',
                width=12,
                locale='pt_BR',
                background='white',
                foreground='black',
                borderwidth=2,
                headersbackground='lightgrey',
                headersforeground='black',
                selectbackground='blue',
                selectforeground='white'
            )
            self.data_entrega_entry.grid(row=4, column=1, padx=10, pady=5, sticky=tk.W)
            
            # Hora de Entrega
            ttk.Label(self.destinatario_frame, text="Hora de Entrega").grid(row=5, column=0, padx=10, pady=5, sticky=tk.W)
            self.hora_entrega_entry = ttk.Frame(self.destinatario_frame)
            self.hora_entrega_entry.grid(row=5, column=1, padx=10, pady=5, sticky=tk.W)
            self.hora_var = tk.StringVar(value="00")
            self.minuto_var = tk.StringVar(value="00")
            vcmd_hora = (self.destinatario_frame.register(self.validate_hour), '%P')
            vcmd_minuto = (self.destinatario_frame.register(self.validate_minute), '%P')
            ttk.Spinbox(self.hora_entrega_entry, from_=0, to=23, textvariable=self.hora_var, width=3, format="%02.0f", validate='key', validatecommand=vcmd_hora).grid(row=0, column=0)
            ttk.Label(self.hora_entrega_entry, text=":").grid(row=0, column=1)
            ttk.Spinbox(self.hora_entrega_entry, from_=0, to=59, textvariable=self.minuto_var, width=3, format="%02.0f", validate='key', validatecommand=vcmd_minuto).grid(row=0, column=2)
            
            # Garanta que o Canvas se ajuste ao redimensionar a janela
            self.adicionar_pedido_tab.grid_rowconfigure(1, weight=1)
            self.adicionar_pedido_tab.grid_columnconfigure(0, weight=1)
            
            # Botão Adicionar Pedido
            self.adicionar_pedido_btn = ttk.Button(self.adicionar_pedido_tab, text="Adicionar Pedido", command=self.adicionar_pedido)
            self.adicionar_pedido_btn.grid(row=12, column=0, columnspan=2, pady=10)
            self.widget_cache["adicionar_pedido_tab"] = self.adicionar_pedido_tab

    def _resize_widgets(self, event):
        self.comprador_frame.grid_configure(sticky="nsew")
        self.nome_entry.grid_configure(sticky="ew")
        self.telefone_entry.grid_configure(sticky="ew")

    def validate_hour(self, value_if_allowed):
        if value_if_allowed.isdigit() and 0 <= int(value_if_allowed) <= 23:
            return True
        elif value_if_allowed == "":
            return True
        return False

    def validate_minute(self, value_if_allowed):
        if value_if_allowed.isdigit() and 0 <= int(value_if_allowed) <= 59:
            return True
        elif value_if_allowed == "":
            return True
        return False

    def toggle_pagamento_entry(self, valor_pedido_entry=None, pagamento_realizado_var=None):
        if valor_pedido_entry is None:
            valor_pedido_entry = self.valor_pedido_entry
        if pagamento_realizado_var is None:
            pagamento_realizado_var = self.pagamento_realizado_var

        if pagamento_realizado_var.get() == 1:
            valor_pedido_entry.config(state='disabled')
        else:
            valor_pedido_entry.config(state='normal')

    def formatar_valor(self, event, valor_pedido_entry=None):
        if valor_pedido_entry is None:
            valor_pedido_entry = self.valor_pedido_entry

        # Obtém o valor atual digitado
        valor = valor_pedido_entry.get()

        # Remove qualquer caractere não numérico (exceto vírgulas e pontos)
        valor = ''.join(filter(str.isdigit, valor))

        # Adiciona a vírgula para os centavos e ponto para separar milhares
        if len(valor) > 2:
            valor = f'{int(valor[:-2]):,}.{valor[-2:]}'
            valor = valor.replace(',', '.')

        elif len(valor) > 0:
            valor = f'0.{valor.zfill(2)}'

        # Atualiza o campo com o valor formatado
        valor_pedido_entry.delete(0, tk.END)
        valor_pedido_entry.insert(0, valor)

    def capturar_valor_pedido(self):
        if self.pagamento_realizado_var.get() == 0:
            valor = self.valor_pedido_entry.get()
            return valor
        return None

    def capturar_pagamento_realizado(self):
        return self.pagamento_realizado_var.get() == 1

    def add_pedido_entry(self):
        row = len(self.pedido_entries)
        pedido_label = ttk.Label(self.pedidos_inner_frame, text=f"Pedido {row + 1}")
        pedido_label.grid(row=row, column=0, padx=10, pady=5, sticky=tk.W)
        pedido_entry = ttk.Entry(self.pedidos_inner_frame, width=100)
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

        # Adicionar dados de pagamento
        pagamento_realizado = bool(self.pagamento_realizado_var.get())
        valor_pedido = self.valor_pedido_entry.get()

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
            "Data do Pedido": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "Pagamento Realizado": pagamento_realizado,
            "Valor do Pedido": valor_pedido
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
        self.valor_pedido_entry.delete(0, tk.END)

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
        self.pedidos.sort(key=lambda x: datetime.strptime(x['Data do Pedido'], "%d/%m/%Y %H:%M:%S"), reverse=True)
        
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Verificar o tema atual
        tema_atual = sv_ttk.get_theme()
        
        # Definir as cores de fundo baseadas no tema
        if tema_atual == "dark":
            oddrow_bg = 'DimGray'
            evenrow_bg = 'Gray'
        else:
            oddrow_bg = 'GhostWhite'
            evenrow_bg = 'white'

        for index, pedido in enumerate(self.pedidos):
            tag = 'evenrow' if index % 2 == 0 else 'oddrow'

            try:
                # Convert the list of pedidos to a string
                pedidos_str = ", ".join(pedido["Pedidos"])
                
                values = (
                    pedido["Nome do Comprador"], 
                    pedidos_str, 
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
                )
            except KeyError as e:
                print(f"Missing key in pedido: {e}")
                continue
            except Exception as e:
                print(f"Error processing pedido: {e}")
                continue

            self.tree.insert("", "end", values=values, tags=(tag,))
        
        self.tree.tag_configure('oddrow', background=oddrow_bg)
        self.tree.tag_configure('evenrow', background=evenrow_bg)

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
            # Adjust the comparison logic to handle the Pedidos field correctly
            pedido = next((p for p in self.pedidos if p["Nome do Comprador"] == valores[0] and p["Data do Pedido"] == valores[2]), None)
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


def run_profiler():
    pr = cProfile.Profile()
    pr.enable()

    # Inicialize o aplicativo
    root = tk.Tk()
    app = PedidoApp(root)
    root.mainloop()

    pr.disable()
    s = io.StringIO()
    sortby = 'cumulative'
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats()
    print(s.getvalue())

if __name__ == "__main__":
    root = tk.Tk()
    app = PedidoApp(root)
    app.carregar_configuracao()  # Carregar configurações ao iniciar o app
    root.mainloop()
    #cProfile.run