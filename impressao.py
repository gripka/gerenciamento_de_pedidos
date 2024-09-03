from escpos.printer import Usb
from PIL import Image
from datetime import datetime
import json
import textwrap
from unidecode import unidecode

def converter_para_cp437(texto):
    try:
        # Converter caracteres Unicode para seus equivalentes ASCII
        texto_ascii = unidecode(texto)
        # Codificar o texto ASCII para CP437
        texto_cp437 = texto_ascii.encode('cp437', errors='replace').decode('cp437')
        return texto_cp437
    except UnicodeEncodeError:
        print("Erro ao converter texto para CP437.")
        return texto
    
def carregar_configuracoes():
    try:
        with open("config.json", "r") as arquivo:
            config = json.load(arquivo)
            return {
                "logo_path": config.get("logo_path", ""),
                "cabecalho_pedido": config.get("cabecalho_pedido"),
                "nome_estabelecimento": config.get("nome_estabelecimento"),
                "printer_vendor_id": config.get("printer_vendor_id", 0x04b8),
                "printer_product_id": config.get("printer_product_id", 0x0e03)
            }
    except FileNotFoundError:
        return {
            "logo_path": "",
            "cabecalho_pedido": "Cabeçalho não configurado",
            "nome_estabelecimento": "Estabelecimento não configurado",
            "printer_vendor_id": 0x04b8,
            "printer_product_id": 0x0e03
        }

def imprimir_pedido(pedido):
    try:
        # Verificar se pedido é um dicionário
        if not isinstance(pedido, dict):
            raise TypeError("O parâmetro 'pedido' deve ser um dicionário")

        # Carregar o caminho do logo e outras configurações a partir das configurações
        config = carregar_configuracoes()
        logo_path = config.get("logo_path", "")
        cabecalho_pedido = config.get("cabecalho_pedido")
        nome_estabelecimento = config.get("nome_estabelecimento")
        printer_vendor_id = config.get("printer_vendor_id")
        printer_product_id = config.get("printer_product_id")

        # Inicializar a impressora USB
        printer = Usb(printer_vendor_id, printer_product_id, 0)

        # Carregar o caminho do logo e outras configurações a partir das configurações
        config = carregar_configuracoes()
        logo_path = config.get("logo_path", "")
        cabecalho_pedido = config.get("cabecalho_pedido")
        nome_estabelecimento = config.get("nome_estabelecimento")

        if logo_path:
            try:
                logo = Image.open(logo_path).convert('L')
                printer.image(logo)
            except Exception as e:
                print(f"Erro ao carregar a imagem do logo: {e}")

        # Centralizar o cabeçalho do pedido
        printer.text("\n")
        printer.set(align='center')
        printer.text(f"{cabecalho_pedido}\n")
        printer.set(align='center')
        printer.text("==========================================\n")

        # Imprimir os campos do pedido, incluindo a lista de pedidos
        printer.set(align='left')
        printer.text(f"Nome do Comprador: {pedido.get('Nome do Comprador', '')}\n")
        for i, p in enumerate(pedido.get('Pedidos', []), 1):
            printer.text(f"Pedido {i}: {p}\n")
        printer.text(f"Telefone: {pedido.get('Telefone', '')}\n")
        printer.text(f"Cartao: {pedido.get('Cartão', '')}\n")
        #printer.text(f"Contato: {pedido.get('Contato', '')}\n")
        
        # Imprimir informações de pagamento
        print(f"Conteúdo do pedido: {pedido}")  # Debugging line
        pagamento_realizado = pedido.get('Pagamento Realizado', False)
        print(f"Pagamento realizado: {pagamento_realizado}")  # Debugging line
        if pagamento_realizado:
            printer.text(f"Pagamento Realizado\n")
        else:
            valor_pagamento = pedido.get('Valor do Pedido', '')
            printer.text(f"Pagamento pendente: R$ {valor_pagamento}\n")

        printer.set(align='center')
        printer.text(converter_para_cp437("==========================================\n"))
        printer.text(converter_para_cp437("Detalhes do Destinatario\n"))
        printer.text(converter_para_cp437("==========================================\n"))
        printer.set(align='left')

        def imprimir_endereco(printer, endereco_entrega, total_width=45):
            prefix = "Endereco de Entrega: "
            prefix_length = len(prefix)

            # Quebrar o endereço em linhas, ajustando a largura da primeira linha
            endereco_quebrado = textwrap.wrap(endereco_entrega, width=total_width - prefix_length)

            if endereco_quebrado:
                # Imprimir a primeira linha com o prefixo
                printer.text(converter_para_cp437(f"{prefix}{endereco_quebrado[0]}\n"))
                # Quebrar o restante do endereço com a largura total
                restante_endereco = endereco_entrega[len(endereco_quebrado[0]):].strip()
                restante_quebrado = textwrap.wrap(restante_endereco, width=total_width)
                # Imprimir as linhas restantes
                for line in restante_quebrado:
                    printer.text(converter_para_cp437(f"{line}\n"))
        endereco_entrega = pedido.get('Endereço de Entrega', '')

        printer.text(converter_para_cp437(f"Nome do Destinatario: {pedido.get('Nome do Destinatário', '')}\n"))
        printer.text(converter_para_cp437(f"Telefone do Destinatario: {pedido.get('Telefone do Destinatário', '')}\n"))
        imprimir_endereco(printer, endereco_entrega)
        printer.text(converter_para_cp437(f"Referencia: {pedido.get('Referência', '')}\n"))
        printer.text(converter_para_cp437(f"Data de Entrega: {pedido.get('Data de Entrega', '')}\n"))
        printer.text(converter_para_cp437(f"Hora de Entrega: {pedido.get('Hora de Entrega', '')}\n"))

        # Adicionar a data e hora da impressão
        printer.set(align='center')

        data_hora_impressao = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        printer.text(converter_para_cp437("\n"))
        printer.text(converter_para_cp437("==========================================\n"))
        printer.set(align='center')
        printer.text(converter_para_cp437(f"{config['nome_estabelecimento']}\n"))
        printer.text(converter_para_cp437(f"Data da Impressao: {data_hora_impressao}\n"))
        printer.text(converter_para_cp437("==========================================\n"))

        printer.cut()

    except Exception as e:
        print(f"Erro ao imprimir: {e}")
