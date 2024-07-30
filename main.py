print("Executando main.py")

from gui import PedidoApp
import tkinter as tk

if __name__ == "__main__":
    root = tk.Tk()
    app = PedidoApp(root)
    app.carregar_pedidos()  # Carrega os pedidos do arquivo JSON
    root.mainloop()
