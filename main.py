from gui import PedidoApp
import tkinter as tk

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = PedidoApp(root)
        app.carregar_pedidos()  
        root.mainloop()
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
        input("Pressione Enter para sair...")
