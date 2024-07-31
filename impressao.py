from escpos.printer import Usb
from PIL import Image
from datetime import datetime
import json

def carregar_configuracoes():
    try:
        with open("config.json", "r") as arquivo:
            config = json.load(arquivo)
            return config.get("logo_path", "")
    except FileNotFoundError:
        return ""

def imprimir_pedido(pedido):
    try:
        # Verificar se pedido é um dicionário
        if not isinstance(pedido, dict):
            raise TypeError("O parâmetro 'pedido' deve ser um dicionário")

        # Inicializar a impressora USB
        printer = Usb(0x04b8, 0x0e03, 0)

        # Carregar o caminho do logo a partir das configurações
        logo_path = carregar_configuracoes()
        if logo_path:
            try:
                logo = Image.open(logo_path).convert('L')
                printer.image(logo)
            except Exception as e:
                print(f"Erro ao carregar a imagem do logo: {e}")

        # Cabeçalho do pedido
        printer.text("\nRecibo de Pedido\n")
        printer.text("==========================================\n")

        # Imprimir os campos do pedido, incluindo a lista de pedidos
        printer.text(f"Nome do Comprador: {pedido.get('Nome do Comprador', '')}\n")
        for i, p in enumerate(pedido.get('Pedidos', []), 1):
            printer.text(f"Pedido {i}: {p}\n")
        printer.text(f"Telefone: {pedido.get('Telefone', '')}\n")
        printer.text(f"Cartão: {pedido.get('Cartão', '')}\n")
        printer.text(f"Contato: {pedido.get('Contato', '')}\n")

        # Adicionar uma linha de separação antes dos detalhes do destinatário
        printer.text("==========================================\n")
        printer.text("Detalhes do Destinatário\n")
        printer.text("==========================================\n")
        printer.text(f"Nome do Destinatário: {pedido.get('Nome do Destinatário', '')}\n")
        printer.text(f"Telefone do Destinatário: {pedido.get('Telefone do Destinatário', '')}\n")
        printer.text(f"Endereço de Entrega: {pedido.get('Endereço de Entrega', '')}\n")
        printer.text(f"Referência: {pedido.get('Referência', '')}\n")
        printer.text(f"Data de Entrega: {pedido.get('Data de Entrega', '')}\n")
        printer.text(f"Hora de Entrega: {pedido.get('Hora de Entrega', '')}\n")

        # Adicionar a data e hora da impressão
        data_hora_impressao = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        printer.text("\n")
        printer.text("==========================================\n")
        printer.text("Adriana Flores\n")
        printer.text(f"Data da Impressão: {data_hora_impressao}\n")
        printer.text("==========================================\n")

        # Cortar o papel
        printer.cut()

    except Exception as e:
        print(f"Erro ao imprimir: {e}")
