from escpos.printer import Usb
from datetime import datetime

def imprimir_pedido(pedido):
    try:
        # Verificar se pedido é um dicionário
        if not isinstance(pedido, dict):
            raise TypeError("O parâmetro 'pedido' deve ser um dicionário")

        # Inicializar a impressora USB
        printer = Usb(0x04b8, 0x0e03, 0)

        # Cabeçalho do pedido
        printer.text("Recibo de Pedido - Adriana Flores\n")
        printer.text("=====================\n")

        # Imprimir os campos do pedido
        for campo, valor in pedido.items():
            if campo not in ["Nome do Destinatário", "Telefone do Destinatário", "Endereço de Entrega", "Data de Entrega", "Hora de Entrega", "Referência"]:
                printer.text(f"{campo}: {valor}\n")

        # Adicionar uma linha de separação antes dos detalhes do destinatário
        printer.text("=====================\n")

        # Imprimir os detalhes do destinatário
        printer.text("Detalhes do Destinatário\n")
        printer.text("=====================\n")
        printer.text(f"Nome do Destinatário: {pedido.get('Nome do Destinatário', '')}\n")
        printer.text(f"Telefone do Destinatário: {pedido.get('Telefone do Destinatário', '')}\n")
        printer.text(f"Endereço de Entrega: {pedido.get('Endereço de Entrega', '')}\n")
        printer.text(f"Referência: {pedido.get('Referência', '')}\n")
        printer.text(f"Data de Entrega: {pedido.get('Data de Entrega', '')}\n")
        printer.text(f"Hora de Entrega: {pedido.get('Hora de Entrega', '')}\n")

        # Adicionar a data e hora da impressão
        data_hora_impressao = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        printer.text("\n")
        printer.text("=====================\n")
        printer.text("Adriana Flores\n")
        printer.text(f"Data da Impressão: {data_hora_impressao}\n")
        printer.text("=====================\n")

        # Cortar o papel
        printer.cut()

    except Exception as e:
        print(f"Erro ao imprimir: {e}")
