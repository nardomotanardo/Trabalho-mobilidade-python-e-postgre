import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import pg8000
import webbrowser
import requests
import os

# Classe de Login
class LoginScreen(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Login")
        self.geometry("400x200")
        self.configure(bg="#f0f0f5")

        # Campos de login
        tk.Label(self, text="Usuário:", anchor="w").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.entrada_usuario = tk.Entry(self)
        self.entrada_usuario.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(self, text="Senha:", anchor="w").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.entrada_senha = tk.Entry(self, show="*")
        self.entrada_senha.grid(row=1, column=1, padx=10, pady=10)

        # Botão de login
        tk.Button(self, text="Entrar", command=self.verificar_login).grid(row=2, column=0, columnspan=2, padx=10, pady=10)

    def conectar_banco(self):
        try:
            conn = pg8000.connect(database='dbacessibilidade', user='postgres', password='1234', host='localhost', port=5432)
            return conn
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao conectar ao banco de dados: {e}")
            return None

    def verificar_login(self):
        username = self.entrada_usuario.get()
        senha = self.entrada_senha.get()

        conn = self.conectar_banco()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("SELECT * FROM usuarios WHERE username = %s AND senha = %s", (username, senha))
                usuario = cur.fetchone()
                if usuario:
                    messagebox.showinfo("Sucesso", "Login realizado com sucesso!")
                    self.destroy()  # Fecha a janela de login
                    SistemaAcessibilidade()  # Abre a janela principal
                else:
                    messagebox.showerror("Erro", "Nome de usuário ou senha incorretos!")
                cur.close()
                conn.close()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao autenticar: {e}")

# Classe principal do sistema
class SistemaAcessibilidade(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Mapeamento de Acessibilidade")
        self.geometry("900x600")
        self.configure(bg="#f0f0f5")

        # Variáveis para armazenar a seleção e os filtros
        self.id_problema_selecionado = None  # Variável para armazenar o ID do problema selecionado
        self.rua_selecionada = ""
        self.numero_selecionado = ""
        self.foto_caminho = ""  # Variável para armazenar o caminho da foto
        self.filtro_rua = tk.StringVar()
        self.filtro_problema = tk.StringVar()
        self.filtro_gravidade = tk.StringVar()
        self.filtro_relator = tk.StringVar()

        # Criando a interface
        self.criar_widgets()
        self.carregar_primeiros_resultados()

    def conectar_banco(self):
        try:
            conn = pg8000.connect(database='dbacessibilidade', user='postgres', password='1234', host='localhost', port=5432)
            return conn
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao conectar ao banco de dados: {e}")
            return None

    def carregar_primeiros_resultados(self):
        """Carrega os primeiros 100 resultados na lista ao abrir a tela."""
        self.lista_problemas.delete(0, tk.END)
        conn = self.conectar_banco()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("SELECT p.id, l.rua, l.numero, l.cep, p.tipo, p.gravidade, p.relator FROM problemas_acessibilidade p JOIN localizacao l ON p.id_localizacao = l.id LIMIT 100")
                problemas = cur.fetchall()

                self.lista_problemas.delete(0, tk.END)
                for problema in problemas:
                    self.lista_problemas.insert(tk.END, f"{problema[0]} - Rua: {problema[1]}, Número: {problema[2]}, CEP: {problema[3]}, Problema: {problema[4]}, Gravidade: {problema[5]}, Relator: {problema[6]}")
                cur.close()
                conn.close()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao carregar os primeiros resultados: {e}")

    def listar_problemas(self):
        """Lista todos os problemas registrados e carrega na lista de problemas."""
        self.lista_problemas.delete(0, tk.END)  # Limpa a lista antes de carregar
        conn = self.conectar_banco()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("SELECT p.id, l.rua, l.numero, l.cep, p.tipo, p.gravidade, p.relator FROM problemas_acessibilidade p JOIN localizacao l ON p.id_localizacao = l.id")
                problemas = cur.fetchall()
                for problema in problemas:
                    self.lista_problemas.insert(tk.END, f"{problema[0]} - Rua: {problema[1]}, Número: {problema[2]}, CEP: {problema[3]}, Problema: {problema[4]}, Gravidade: {problema[5]}, Relator: {problema[6]}")
                cur.close()
                conn.close()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao listar os problemas: {e}")

    def aplicar_filtros(self):
        """Aplica os filtros e carrega os resultados filtrados na lista."""
        conn = self.conectar_banco()
        if conn:
            try:
                cur = conn.cursor()
                query = """
                    SELECT p.id, l.rua, l.numero, l.cep, p.tipo, p.gravidade, p.relator 
                    FROM problemas_acessibilidade p 
                    JOIN localizacao l ON p.id_localizacao = l.id
                    WHERE l.rua ILIKE %s AND p.tipo ILIKE %s AND p.gravidade ILIKE %s AND p.relator ILIKE %s
                """
                cur.execute(query, (
                    f"%{self.filtro_rua.get()}%", 
                    f"%{self.filtro_problema.get()}%", 
                    f"%{self.filtro_gravidade.get()}%", 
                    f"%{self.filtro_relator.get()}%"
                ))
                problemas = cur.fetchall()

                self.lista_problemas.delete(0, tk.END)
                for problema in problemas:
                    self.lista_problemas.insert(tk.END, f"{problema[0]} - Rua: {problema[1]}, Número: {problema[2]}, CEP: {problema[3]}, Problema: {problema[4]}, Gravidade: {problema[5]}, Relator: {problema[6]}")
                cur.close()
                conn.close()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao aplicar filtros: {e}")

    def buscar_cep(self):
        cep = self.entrada_cep.get().replace("-", "").strip()
        if len(cep) == 8:
            try:
                url = f"https://viacep.com.br/ws/{cep}/json/"
                response = requests.get(url)
                dados = response.json()

                if "erro" not in dados:
                    self.entrada_rua.delete(0, tk.END)
                    self.entrada_rua.insert(0, dados['logradouro'])
                    self.entrada_bairro.delete(0, tk.END)
                    self.entrada_bairro.insert(0, dados['bairro'])
                else:
                    messagebox.showerror("Erro", "CEP não encontrado.")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao buscar CEP: {e}")
        else:
            messagebox.showwarning("Erro", "CEP inválido.")

    def upload_foto(self):
        """Função para fazer o upload de uma foto."""
        self.foto_caminho = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.jpeg;*.png")])
        if self.foto_caminho:
            messagebox.showinfo("Sucesso", f"Foto selecionada: {self.foto_caminho}")

    def registrar_problema(self):
        cep = self.entrada_cep.get()
        rua = self.entrada_rua.get()
        numero = self.entrada_numero.get()
        bairro = self.entrada_bairro.get()
        problema = self.combo_problema.get()
        gravidade = self.combo_gravidade.get()
        relator = self.entrada_relator.get()

        if rua and numero and problema and gravidade and relator and self.foto_caminho:
            conn = self.conectar_banco()
            if conn:
                try:
                    cur = conn.cursor()
                    cur.execute("INSERT INTO localizacao (rua, numero, bairro, cep, latitude, longitude, foto) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id",
                                (rua, numero, bairro, cep, 0.0, 0.0, self.foto_caminho))
                    id_localizacao = cur.fetchone()[0]

                    cur.execute("INSERT INTO problemas_acessibilidade (id_localizacao, tipo, descricao, gravidade, relator) VALUES (%s, %s, %s, %s, %s)",
                                (id_localizacao, problema, problema, gravidade, relator))

                    conn.commit()
                    cur.close()
                    conn.close()

                    self.limpar_campos()
                    messagebox.showinfo("Sucesso", "Problema registrado com sucesso!")
                    self.listar_problemas()
                except Exception as e:
                    messagebox.showerror("Erro", f"Erro ao registrar o problema: {e}")
                    conn.rollback()
                    conn.close()
        else:
            messagebox.showwarning("Erro", "Preencha todos os campos e selecione uma foto.")

    def selecionar_problema(self, event):
        try:
            selecionado = self.lista_problemas.curselection()
            if selecionado:
                dados = self.lista_problemas.get(selecionado)
                self.id_problema_selecionado, descricao = dados.split(" - Rua: ")
                rua, resto = descricao.split(", Número:")
                numero, resto = resto.split(", CEP:")
                self.rua_selecionada = rua.strip()
                self.numero_selecionado = numero.strip()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao selecionar o problema: {e}")

    def abrir_mapa(self):
        if self.rua_selecionada and self.numero_selecionado:
            url = f"https://www.google.com/maps/search/?api=1&query={self.rua_selecionada.replace(' ', '+')}+{self.numero_selecionado}"
            webbrowser.open(url, new=2)
        else:
            messagebox.showwarning("Erro", "Selecione uma rua e número da lista.")

    def limpar_campos(self):
        self.id_problema_selecionado = None
        self.entrada_cep.delete(0, tk.END)
        self.entrada_rua.delete(0, tk.END)
        self.entrada_numero.delete(0, tk.END)
        self.entrada_bairro.delete(0, tk.END)
        self.combo_problema.set("")
        self.combo_gravidade.set("")
        self.entrada_relator.delete(0, tk.END)
        self.foto_caminho = ""

    def criar_widgets(self):
        # Layout principal (duas colunas)
        frame_inclusao = tk.Frame(self)
        frame_inclusao.grid(row=0, column=0, padx=10, pady=10)

        frame_filtros = tk.Frame(self)
        frame_filtros.grid(row=0, column=2, padx=10, pady=10)

        # Separador entre as colunas
        separator = ttk.Separator(self, orient='vertical')
        separator.grid(row=0, column=1, sticky='ns', padx=5)

        # ========== Frame de Inclusão ==========
        tk.Label(frame_inclusao, text="CEP:", anchor="w").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.entrada_cep = tk.Entry(frame_inclusao)
        self.entrada_cep.grid(row=0, column=1, padx=10, pady=5)
        tk.Button(frame_inclusao, text="Buscar", command=self.buscar_cep).grid(row=0, column=2, padx=10, pady=5)

        tk.Label(frame_inclusao, text="Rua:", anchor="w").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.entrada_rua = tk.Entry(frame_inclusao)
        self.entrada_rua.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(frame_inclusao, text="Número:", anchor="w").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.entrada_numero = tk.Entry(frame_inclusao)
        self.entrada_numero.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(frame_inclusao, text="Bairro:", anchor="w").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.entrada_bairro = tk.Entry(frame_inclusao)
        self.entrada_bairro.grid(row=3, column=1, padx=10, pady=5)

        tk.Label(frame_inclusao, text="Relator:", anchor="w").grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self.entrada_relator = tk.Entry(frame_inclusao)
        self.entrada_relator.grid(row=4, column=1, padx=10, pady=5)

        tk.Label(frame_inclusao, text="Problema:", anchor="w").grid(row=5, column=0, padx=10, pady=5, sticky="w")
        self.combo_problema = ttk.Combobox(frame_inclusao, values=["Buraco", "Calçada Irregular", "Falta de Acessibilidade"])
        self.combo_problema.grid(row=5, column=1, padx=10, pady=5)

        tk.Label(frame_inclusao, text="Gravidade:", anchor="w").grid(row=6, column=0, padx=10, pady=5, sticky="w")
        self.combo_gravidade = ttk.Combobox(frame_inclusao, values=["Baixa", "Média", "Alta"])
        self.combo_gravidade.grid(row=6, column=1, padx=10, pady=5)

        tk.Button(frame_inclusao, text="Selecionar Foto", command=self.upload_foto).grid(row=7, column=0, padx=10, pady=5)

        # Botões para Registrar e Map
        tk.Button(frame_inclusao, text="Registrar Problema", command=self.registrar_problema).grid(row=8, column=0, padx=10, pady=10)
        tk.Button(frame_inclusao, text="Visualizar no Mapa", command=self.abrir_mapa).grid(row=8, column=1, padx=10, pady=10)

        # ========== Frame de Filtros ==========
        tk.Label(frame_filtros, text="Filtrar por Rua:", anchor="w").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.entrada_filtro_rua = tk.Entry(frame_filtros, textvariable=self.filtro_rua)
        self.entrada_filtro_rua.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(frame_filtros, text="Filtrar por Problema:", anchor="w").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.combo_filtro_problema = ttk.Combobox(frame_filtros, values=["Buraco", "Calçada Irregular", "Falta de Acessibilidade"], textvariable=self.filtro_problema)
        self.combo_filtro_problema.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(frame_filtros, text="Filtrar por Gravidade:", anchor="w").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.combo_filtro_gravidade = ttk.Combobox(frame_filtros, values=["Baixa", "Média", "Alta"], textvariable=self.filtro_gravidade)
        self.combo_filtro_gravidade.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(frame_filtros, text="Filtrar por Relator:", anchor="w").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.entrada_filtro_relator = tk.Entry(frame_filtros, textvariable=self.filtro_relator)
        self.entrada_filtro_relator.grid(row=3, column=1, padx=10, pady=5)

        tk.Button(frame_filtros, text="Aplicar Filtros", command=self.aplicar_filtros).grid(row=4, column=0, columnspan=2, padx=10, pady=10)

        # Lista de problemas
        tk.Label(self, text="Problemas Registrados:").grid(row=1, column=0, columnspan=3, padx=10, pady=5)
        self.lista_problemas = tk.Listbox(self, width=100, height=10)
        self.lista_problemas.grid(row=2, column=0, columnspan=3, padx=10, pady=5)
        self.lista_problemas.bind('<<ListboxSelect>>', self.selecionar_problema)

# Inicializa a tela de login
if __name__ == "__main__":
    login_app = LoginScreen()
    login_app.mainloop()
