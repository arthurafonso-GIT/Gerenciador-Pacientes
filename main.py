import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from database import Database
from datetime import datetime

class ClinicaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Clínica Médica Laura Myrna - Sistema de Gestão de Pacientes")
        self.root.geometry("1200x700")
        self.root.configure(bg="#f0f0f0")
        
        # Inicializa o banco de dados
        self.db = Database()
        
        # Variável para armazenar o paciente selecionado
        self.paciente_selecionado = None
        
        # Variável para armazenar a pasta filtrada
        self.pasta_filtrada = None
        
        # Configura o estilo
        self.configurar_estilo()
        
        # Cria a interface
        self.criar_interface()
        
        # Carrega a lista de pacientes
        self.atualizar_lista_pacientes()
    
    def configurar_estilo(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Cores principais
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'), background='#2c3e50', foreground='white', padding=10)
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'), background='#f0f0f0')
        style.configure('TButton', font=('Arial', 10), padding=5)
        style.configure('Primary.TButton', font=('Arial', 10, 'bold'), padding=8)
        
    def criar_interface(self):
        # Frame do título
        frame_titulo = tk.Frame(self.root, bg="#2c3e50")
        frame_titulo.pack(fill='x', side='top')
        
        titulo = ttk.Label(frame_titulo, text="🏥 Clínica Médica Laura Myrna", style='Title.TLabel')
        titulo.pack(pady=15)
        
        # Frame principal dividido em duas colunas
        frame_principal = tk.Frame(self.root, bg="#f0f0f0")
        frame_principal.pack(fill='both', expand=True, side='top', padx=10, pady=10)
        
        # Coluna esquerda - Lista de pacientes
        self.criar_coluna_lista(frame_principal)
        
        # Coluna direita - Detalhes e formulário
        self.criar_coluna_detalhes(frame_principal)
    
    def criar_coluna_lista(self, parent):
        frame_esquerda = tk.Frame(parent, bg="#f0f0f0")
        frame_esquerda.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        # Título e botões
        frame_topo = tk.Frame(frame_esquerda, bg="#f0f0f0")
        frame_topo.pack(fill='x', pady=(0, 10))
        
        ttk.Label(frame_topo, text="Lista de Pacientes", style='Header.TLabel').pack(side='left')
        
        btn_novo = ttk.Button(frame_topo, text="➕ Novo Paciente", style='Primary.TButton',
                             command=self.novo_paciente)
        btn_novo.pack(side='right', padx=5)
        
        btn_gerenciar_pastas = ttk.Button(frame_topo, text="📁 Gerenciar Pastas",
                                          command=self.abrir_gerenciar_pastas)
        btn_gerenciar_pastas.pack(side='right', padx=5)
        
        # Campo de pesquisa
        frame_pesquisa = tk.Frame(frame_esquerda, bg="#f0f0f0")
        frame_pesquisa.pack(fill='x', pady=(0, 10))
        
        ttk.Label(frame_pesquisa, text="🔍 Pesquisar:", background="#f0f0f0").pack(side='left', padx=(0, 5))
        
        self.entry_pesquisa = ttk.Entry(frame_pesquisa, font=('Arial', 10))
        self.entry_pesquisa.pack(side='left', fill='x', expand=True)
        self.entry_pesquisa.bind('<KeyRelease>', lambda e: self.atualizar_lista_pacientes())
        
        btn_limpar = ttk.Button(frame_pesquisa, text="Limpar", command=self.limpar_pesquisa)
        btn_limpar.pack(side='left', padx=(5, 0))
        
        # Filtro por pasta
        frame_filtro = tk.Frame(frame_esquerda, bg="#f0f0f0")
        frame_filtro.pack(fill='x', pady=(0, 10))
        
        ttk.Label(frame_filtro, text="📁 Filtrar por pasta:", background="#f0f0f0").pack(side='left', padx=(0, 5))
        
        self.combo_filtro_pasta = ttk.Combobox(frame_filtro, font=('Arial', 10), state='readonly')
        self.combo_filtro_pasta.pack(side='left', fill='x', expand=True)
        self.combo_filtro_pasta.bind('<<ComboboxSelected>>', lambda e: self.filtrar_por_pasta())
        
        self.atualizar_combo_pastas()
        
        # Treeview para lista de pacientes
        frame_tree = tk.Frame(frame_esquerda, bg="white", relief='solid', borderwidth=1)
        frame_tree.pack(fill='both', expand=True)
        
        # Scrollbars
        scrollbar_y = ttk.Scrollbar(frame_tree, orient='vertical')
        scrollbar_y.pack(side='right', fill='y')
        
        scrollbar_x = ttk.Scrollbar(frame_tree, orient='horizontal')
        scrollbar_x.pack(side='bottom', fill='x')
        
        # Treeview
        self.tree = ttk.Treeview(frame_tree, 
                                 columns=('ID', 'Nome', 'CPF', 'Telefone', 'Data Cadastro'),
                                 show='headings',
                                 yscrollcommand=scrollbar_y.set,
                                 xscrollcommand=scrollbar_x.set)
        
        scrollbar_y.config(command=self.tree.yview)
        scrollbar_x.config(command=self.tree.xview)
        
        # Configurar colunas
        self.tree.heading('ID', text='ID')
        self.tree.heading('Nome', text='Nome')
        self.tree.heading('CPF', text='CPF')
        self.tree.heading('Telefone', text='Telefone')
        self.tree.heading('Data Cadastro', text='Data Cadastro')
        
        self.tree.column('ID', width=50, anchor='center')
        self.tree.column('Nome', width=200)
        self.tree.column('CPF', width=120)
        self.tree.column('Telefone', width=120)
        self.tree.column('Data Cadastro', width=130, anchor='center')
        
        self.tree.pack(fill='both', expand=True)
        
        # Evento de seleção
        self.tree.bind('<<TreeviewSelect>>', self.ao_selecionar_paciente)
    
    def criar_coluna_detalhes(self, parent):
        frame_direita = tk.Frame(parent, bg="#f0f0f0")
        frame_direita.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        # Título
        frame_titulo_dir = tk.Frame(frame_direita, bg="#f0f0f0")
        frame_titulo_dir.pack(fill='x', pady=(0, 10))
        
        self.label_titulo_form = ttk.Label(frame_titulo_dir, text="Detalhes do Paciente", 
                                          style='Header.TLabel')
        self.label_titulo_form.pack(side='left')
        
        # Botões de ação
        frame_botoes_topo = tk.Frame(frame_titulo_dir, bg="#f0f0f0")
        frame_botoes_topo.pack(side='right')
        
        self.btn_editar = ttk.Button(frame_botoes_topo, text="✏️ Editar", 
                                     command=self.editar_paciente, state='disabled')
        self.btn_editar.pack(side='left', padx=2)
        
        self.btn_deletar = ttk.Button(frame_botoes_topo, text="🗑️ Excluir", 
                                      command=self.deletar_paciente, state='disabled')
        self.btn_deletar.pack(side='left', padx=2)
        
        self.btn_gerenciar_pastas_paciente = ttk.Button(frame_botoes_topo, text="📁 Pastas", 
                                                        command=self.gerenciar_pastas_paciente, state='disabled')
        self.btn_gerenciar_pastas_paciente.pack(side='left', padx=2)
        
        # Frame com scroll para o formulário
        canvas = tk.Canvas(frame_direita, bg="#f0f0f0", highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame_direita, orient="vertical", command=canvas.yview)
        self.frame_formulario = tk.Frame(canvas, bg="#f0f0f0")
        
        self.frame_formulario.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.frame_formulario, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Campos do formulário
        self.criar_formulario()
        
        # Botões de ação do formulário
        frame_botoes_form = tk.Frame(self.frame_formulario, bg="#f0f0f0")
        frame_botoes_form.grid(row=20, column=0, columnspan=2, pady=20, sticky='ew')
        
        self.btn_salvar = ttk.Button(frame_botoes_form, text="💾 Salvar", 
                                     style='Primary.TButton',
                                     command=self.salvar_paciente, state='disabled')
        self.btn_salvar.pack(side='left', padx=5, expand=True, fill='x')
        
        self.btn_cancelar = ttk.Button(frame_botoes_form, text="❌ Cancelar", 
                                       command=self.cancelar_edicao, state='disabled')
        self.btn_cancelar.pack(side='left', padx=5, expand=True, fill='x')
    
    def criar_formulario(self):
        self.campos = {}
        
        # Informações Pessoais
        self.criar_secao("📋 Informações Pessoais", 0)
        
        self.campos['nome'] = self.criar_campo("Nome Completo*:", 1, obrigatorio=True)
        self.campos['data_nascimento'] = self.criar_campo("Data de Nascimento:", 2, 
                                                          placeholder="DD/MM/AAAA",
                                                          formatar_func=self.formatar_data)
        self.campos['cpf'] = self.criar_campo("CPF:", 3, placeholder="000.000.000-00",
                                              formatar_func=self.formatar_cpf)
        self.campos['sexo'] = self.criar_combo("Sexo:", 4, 
                                               valores=['Masculino', 'Feminino', 'Outro', 'Não informar'])
        
        # Contato
        self.criar_secao("📞 Contato", 5)
        
        self.campos['telefone'] = self.criar_campo("Telefone:", 6, placeholder="(00) 00000-0000",
                                                   formatar_func=self.formatar_telefone)
        self.campos['email'] = self.criar_campo("E-mail:", 7)
        self.campos['endereco'] = self.criar_campo("Endereço:", 8)
        
        # Informações Clínicas
        self.criar_secao("🏥 Informações Clínicas", 9)
        
        self.campos['historico_clinico'] = self.criar_campo_texto("Histórico Clínico:", 10, altura=5)
        self.campos['tratamento_atual'] = self.criar_campo_texto("Tratamento Atual:", 12, altura=4)
        self.campos['observacoes'] = self.criar_campo_texto("Observações:", 14, altura=3)
    
    def criar_secao(self, titulo, row):
        frame_secao = tk.Frame(self.frame_formulario, bg="#34495e", height=35)
        frame_secao.grid(row=row, column=0, columnspan=2, sticky='ew', pady=(10, 5))
        
        label = tk.Label(frame_secao, text=titulo, font=('Arial', 11, 'bold'),
                        bg="#34495e", fg="white", anchor='w')
        label.pack(fill='x', padx=10, pady=5)
    
    def criar_campo(self, label_text, row, obrigatorio=False, placeholder="", formatar_func=None):
        frame = tk.Frame(self.frame_formulario, bg="#f0f0f0")
        frame.grid(row=row, column=0, columnspan=2, sticky='ew', pady=5, padx=5)
        
        label = tk.Label(frame, text=label_text, font=('Arial', 10), 
                        bg="#f0f0f0", anchor='w', width=20)
        label.pack(side='left', padx=(0, 10))
        
        entry = ttk.Entry(frame, font=('Arial', 10), state='disabled')
        entry.pack(side='left', fill='x', expand=True)
        
        # Vincular função de formatação se fornecida
        if formatar_func:
            entry.bind('<KeyRelease>', formatar_func)
        
        return entry
    
    def criar_combo(self, label_text, row, valores):
        frame = tk.Frame(self.frame_formulario, bg="#f0f0f0")
        frame.grid(row=row, column=0, columnspan=2, sticky='ew', pady=5, padx=5)
        
        label = tk.Label(frame, text=label_text, font=('Arial', 10), 
                        bg="#f0f0f0", anchor='w', width=20)
        label.pack(side='left', padx=(0, 10))
        
        combo = ttk.Combobox(frame, font=('Arial', 10), values=valores, state='disabled')
        combo.pack(side='left', fill='x', expand=True)
        
        return combo
    
    def criar_campo_texto(self, label_text, row, altura=4):
        frame = tk.Frame(self.frame_formulario, bg="#f0f0f0")
        frame.grid(row=row, column=0, columnspan=2, sticky='ew', pady=5, padx=5)
        
        label = tk.Label(frame, text=label_text, font=('Arial', 10, 'bold'), 
                        bg="#f0f0f0", anchor='w')
        label.pack(anchor='w', pady=(0, 5))
        
        text = scrolledtext.ScrolledText(frame, font=('Arial', 10), height=altura, 
                                        wrap=tk.WORD, state='disabled')
        text.pack(fill='both', expand=True)
        
        return text
    
    def formatar_data(self, event):
        widget = event.widget
        texto = widget.get().replace('/', '')
        
        # Remove caracteres não numéricos
        texto = ''.join(filter(str.isdigit, texto))
        
        # Limita a 8 dígitos
        texto = texto[:8]
        
        # Adiciona as barras
        if len(texto) > 4:
            texto = texto[:2] + '/' + texto[2:4] + '/' + texto[4:]
        elif len(texto) > 2:
            texto = texto[:2] + '/' + texto[2:]
        
        # Atualiza o campo
        widget.delete(0, tk.END)
        widget.insert(0, texto)
    
    def formatar_cpf(self, event):
        widget = event.widget
        texto = widget.get().replace('.', '').replace('-', '')
        
        # Remove caracteres não numéricos
        texto = ''.join(filter(str.isdigit, texto))
        
        # Limita a 11 dígitos
        texto = texto[:11]
        
        # Adiciona pontos e traço
        if len(texto) > 9:
            texto = texto[:3] + '.' + texto[3:6] + '.' + texto[6:9] + '-' + texto[9:]
        elif len(texto) > 6:
            texto = texto[:3] + '.' + texto[3:6] + '.' + texto[6:]
        elif len(texto) > 3:
            texto = texto[:3] + '.' + texto[3:]
        
        # Atualiza o campo
        widget.delete(0, tk.END)
        widget.insert(0, texto)
    
    def formatar_telefone(self, event):
        widget = event.widget
        texto = widget.get().replace('(', '').replace(')', '').replace(' ', '').replace('-', '')
        
        # Remove caracteres não numéricos
        texto = ''.join(filter(str.isdigit, texto))
        
        # Limita a 11 dígitos
        texto = texto[:11]
        
        # Adiciona formatação
        if len(texto) > 6:
            if len(texto) == 11:  # Celular com 9 dígitos
                texto = '(' + texto[:2] + ') ' + texto[2:7] + '-' + texto[7:]
            elif len(texto) == 10:  # Fixo com 8 dígitos
                texto = '(' + texto[:2] + ') ' + texto[2:6] + '-' + texto[6:]
            else:
                texto = '(' + texto[:2] + ') ' + texto[2:]
        elif len(texto) > 2:
            texto = '(' + texto[:2] + ') ' + texto[2:]
        elif len(texto) > 0:
            texto = '(' + texto
        
        # Atualiza o campo
        widget.delete(0, tk.END)
        widget.insert(0, texto)
    
    def atualizar_lista_pacientes(self):
        # Limpa a lista atual
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Busca pacientes
        termo_busca = self.entry_pesquisa.get()
        pacientes = self.db.buscar_pacientes(termo_busca, self.pasta_filtrada)
        
        # Adiciona à lista
        for paciente in pacientes:
            self.tree.insert('', 'end', values=(
                paciente[0],  # ID
                paciente[1],  # Nome
                paciente[3] if paciente[3] else '-',  # CPF
                paciente[4] if paciente[4] else '-',  # Telefone
                paciente[8]  # Data Cadastro
            ))
    
    def ao_selecionar_paciente(self, event):
        selecao = self.tree.selection()
        if selecao:
            item = self.tree.item(selecao[0])
            id_paciente = item['values'][0]
            
            # Carrega os dados do paciente
            paciente = self.db.obter_paciente(id_paciente)
            if paciente:
                self.paciente_selecionado = paciente
                self.exibir_paciente(paciente)
                self.btn_editar.config(state='normal')
                self.btn_deletar.config(state='normal')
                self.btn_gerenciar_pastas_paciente.config(state='normal')
    
    def exibir_paciente(self, paciente):
        self.desabilitar_campos()
        
        # Preenche os campos
        self.campos['nome'].config(state='normal')
        self.campos['nome'].delete(0, tk.END)
        self.campos['nome'].insert(0, paciente[1])
        self.campos['nome'].config(state='disabled')
        
        campos_simples = {
            'data_nascimento': paciente[2],
            'cpf': paciente[3],
            'telefone': paciente[4],
            'email': paciente[5],
            'endereco': paciente[6],
        }
        
        for campo, valor in campos_simples.items():
            self.campos[campo].config(state='normal')
            self.campos[campo].delete(0, tk.END)
            if valor:
                self.campos[campo].insert(0, valor)
            self.campos[campo].config(state='disabled')
        
        # Sexo
        self.campos['sexo'].config(state='normal')
        if paciente[7]:
            self.campos['sexo'].set(paciente[7])
        else:
            self.campos['sexo'].set('')
        self.campos['sexo'].config(state='disabled')
        
        # Campos de texto
        campos_texto = {
            'historico_clinico': paciente[9],
            'tratamento_atual': paciente[10],
            'observacoes': paciente[11]
        }
        
        for campo, valor in campos_texto.items():
            self.campos[campo].config(state='normal')
            self.campos[campo].delete('1.0', tk.END)
            if valor:
                self.campos[campo].insert('1.0', valor)
            self.campos[campo].config(state='disabled')
        
        self.label_titulo_form.config(text=f"Detalhes do Paciente - {paciente[1]}")
    
    def novo_paciente(self):
        self.paciente_selecionado = None
        self.limpar_formulario()
        self.habilitar_campos()
        self.label_titulo_form.config(text="Novo Paciente")
        self.btn_editar.config(state='disabled')
        self.btn_deletar.config(state='disabled')
        self.btn_gerenciar_pastas_paciente.config(state='disabled')
        self.btn_salvar.config(state='normal')
        self.btn_cancelar.config(state='normal')
    
    def editar_paciente(self):
        if self.paciente_selecionado:
            self.habilitar_campos()
            self.btn_salvar.config(state='normal')
            self.btn_cancelar.config(state='normal')
            self.btn_editar.config(state='disabled')
            self.btn_deletar.config(state='disabled')
            self.btn_gerenciar_pastas_paciente.config(state='disabled')
            self.label_titulo_form.config(text=f"Editando - {self.paciente_selecionado[1]}")
    
    def salvar_paciente(self):
        # Valida campos obrigatórios
        nome = self.campos['nome'].get().strip()
        if not nome:
            messagebox.showerror("Erro", "O nome do paciente é obrigatório!")
            return
        
        # Coleta os dados
        dados = {
            'nome': nome,
            'data_nascimento': self.campos['data_nascimento'].get().strip(),
            'cpf': self.campos['cpf'].get().strip(),
            'telefone': self.campos['telefone'].get().strip(),
            'email': self.campos['email'].get().strip(),
            'endereco': self.campos['endereco'].get().strip(),
            'sexo': self.campos['sexo'].get(),
            'historico_clinico': self.campos['historico_clinico'].get('1.0', tk.END).strip(),
            'tratamento_atual': self.campos['tratamento_atual'].get('1.0', tk.END).strip(),
            'observacoes': self.campos['observacoes'].get('1.0', tk.END).strip()
        }
        
        # Salva no banco
        if self.paciente_selecionado:
            # Atualiza paciente existente
            sucesso, mensagem = self.db.atualizar_paciente(self.paciente_selecionado[0], dados)
        else:
            # Adiciona novo paciente
            sucesso, mensagem = self.db.adicionar_paciente(dados)
        
        if sucesso:
            messagebox.showinfo("Sucesso", mensagem)
            self.atualizar_lista_pacientes()
            self.limpar_formulario()
            self.desabilitar_campos()
            self.btn_salvar.config(state='disabled')
            self.btn_cancelar.config(state='disabled')
            self.label_titulo_form.config(text="Detalhes do Paciente")
        else:
            messagebox.showerror("Erro", mensagem)
    
    def deletar_paciente(self):
        if self.paciente_selecionado:
            resposta = messagebox.askyesno(
                "Confirmar Exclusão",
                f"Tem certeza que deseja excluir o paciente '{self.paciente_selecionado[1]}'?\n\n"
                "Esta ação não pode ser desfeita!"
            )
            
            if resposta:
                sucesso, mensagem = self.db.deletar_paciente(self.paciente_selecionado[0])
                if sucesso:
                    messagebox.showinfo("Sucesso", mensagem)
                    self.atualizar_lista_pacientes()
                    self.limpar_formulario()
                    self.paciente_selecionado = None
                    self.btn_editar.config(state='disabled')
                    self.btn_deletar.config(state='disabled')
                    self.btn_gerenciar_pastas_paciente.config(state='disabled')
                else:
                    messagebox.showerror("Erro", mensagem)
    
    def cancelar_edicao(self):
        self.limpar_formulario()
        self.desabilitar_campos()
        self.btn_salvar.config(state='disabled')
        self.btn_cancelar.config(state='disabled')
        self.label_titulo_form.config(text="Detalhes do Paciente")
        
        if self.paciente_selecionado:
            self.exibir_paciente(self.paciente_selecionado)
            self.btn_editar.config(state='normal')
            self.btn_deletar.config(state='normal')
    
    def limpar_pesquisa(self):
        self.entry_pesquisa.delete(0, tk.END)
        self.atualizar_lista_pacientes()
    
    def limpar_formulario(self):
        for campo_nome, campo in self.campos.items():
            estado_original = str(campo['state'])
            
            if isinstance(campo, scrolledtext.ScrolledText):
                campo.config(state='normal')
                campo.delete('1.0', tk.END)
                if estado_original == 'disabled':
                    campo.config(state='disabled')
            elif isinstance(campo, ttk.Combobox):
                campo.config(state='normal')
                campo.set('')
                if estado_original == 'disabled':
                    campo.config(state='disabled')
            else:
                campo.config(state='normal')
                campo.delete(0, tk.END)
                if estado_original == 'disabled':
                    campo.config(state='disabled')
    
    def habilitar_campos(self):
        for campo in self.campos.values():
            if isinstance(campo, scrolledtext.ScrolledText):
                campo.config(state='normal')
            elif isinstance(campo, ttk.Combobox):
                campo.config(state='readonly')
            else:
                campo.config(state='normal')
    
    def desabilitar_campos(self):
        for campo in self.campos.values():
            campo.config(state='disabled')
    
    def atualizar_combo_pastas(self):
        pastas = self.db.listar_pastas()
        valores = ["Todas as pastas"]
        valores.extend([f"{pasta[1]} ({self.db.contar_pacientes_pasta(pasta[0])})" for pasta in pastas])
        self.combo_filtro_pasta['values'] = valores
        self.combo_filtro_pasta.current(0)
    
    def filtrar_por_pasta(self):
        selecao = self.combo_filtro_pasta.get()
        if selecao == "Todas as pastas":
            self.pasta_filtrada = None
        else:
            # Extrai o nome da pasta (antes do parêntese com contagem)
            nome_pasta = selecao.split(" (")[0]
            pastas = self.db.listar_pastas()
            for pasta in pastas:
                if pasta[1] == nome_pasta:
                    self.pasta_filtrada = pasta[0]
                    break
        self.atualizar_lista_pacientes()
    
    def abrir_gerenciar_pastas(self):
        janela = tk.Toplevel(self.root)
        janela.title("Gerenciar Pastas")
        janela.geometry("1000x600")
        janela.transient(self.root)
        janela.grab_set()
        
        # Frame principal dividido em duas partes
        frame_principal = tk.Frame(janela, bg="#f0f0f0")
        frame_principal.pack(fill='both', expand=True, padx=10, pady=10)
        
        frame_esquerdo = tk.Frame(frame_principal, bg="#f0f0f0")
        frame_esquerdo.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        # Título da lista
        frame_topo_lista = tk.Frame(frame_esquerdo, bg="#f0f0f0")
        frame_topo_lista.pack(fill='x', pady=(0, 10))
        
        ttk.Label(frame_topo_lista, text="Pastas Existentes", font=('Arial', 12, 'bold'), 
                 background="#f0f0f0").pack(side='left')
        
        # Lista de pastas
        frame_lista = tk.Frame(frame_esquerdo, bg="white", relief='solid', borderwidth=1)
        frame_lista.pack(fill='both', expand=True)
        
        scrollbar_y = ttk.Scrollbar(frame_lista, orient='vertical')
        scrollbar_y.pack(side='right', fill='y')
        
        tree_pastas = ttk.Treeview(frame_lista, 
                                    columns=('ID', 'Nome', 'Descrição', 'Pacientes', 'Data'),
                                    show='headings',
                                    yscrollcommand=scrollbar_y.set)
        scrollbar_y.config(command=tree_pastas.yview)
        
        tree_pastas.heading('ID', text='ID')
        tree_pastas.heading('Nome', text='Nome')
        tree_pastas.heading('Descrição', text='Descrição')
        tree_pastas.heading('Pacientes', text='Nº Pacientes')
        tree_pastas.heading('Data', text='Data Criação')
        
        tree_pastas.column('ID', width=50, anchor='center')
        tree_pastas.column('Nome', width=150)
        tree_pastas.column('Descrição', width=200)
        tree_pastas.column('Pacientes', width=80, anchor='center')
        tree_pastas.column('Data', width=100, anchor='center')
        
        tree_pastas.pack(fill='both', expand=True)
        
        # Botões de ação da lista
        frame_botoes_lista = tk.Frame(frame_esquerdo, bg="#f0f0f0")
        frame_botoes_lista.pack(fill='x', pady=(10, 0))
        
        frame_direito = tk.Frame(frame_principal, bg="#f0f0f0")
        frame_direito.pack(side='right', fill='both', expand=False, padx=(5, 0))
        frame_direito.config(width=350)
        
        # Título do formulário
        frame_topo_form = tk.Frame(frame_direito, bg="#2c3e50")
        frame_topo_form.pack(fill='x', pady=(0, 10))
        
        label_titulo_form = tk.Label(frame_topo_form, text="Nova Pasta", 
                                     font=('Arial', 12, 'bold'),
                                     bg="#2c3e50", fg="white", pady=10)
        label_titulo_form.pack()
        
        # Formulário
        frame_form = tk.Frame(frame_direito, bg="#f0f0f0")
        frame_form.pack(fill='both', expand=True)
        
        # Variável para controlar se está editando
        pasta_editando = {'id': None}
        
        # Campo Nome
        tk.Label(frame_form, text="Nome da Pasta*:", font=('Arial', 10, 'bold'),
                bg="#f0f0f0", anchor='w').pack(fill='x', pady=(5, 2))
        entry_nome = ttk.Entry(frame_form, font=('Arial', 10))
        entry_nome.pack(fill='x', pady=(0, 10))
        
        # Campo Descrição
        tk.Label(frame_form, text="Descrição:", font=('Arial', 10, 'bold'),
                bg="#f0f0f0", anchor='w').pack(fill='x', pady=(5, 2))
        text_descricao = scrolledtext.ScrolledText(frame_form, font=('Arial', 10), 
                                                   height=4, wrap=tk.WORD)
        text_descricao.pack(fill='x', pady=(0, 10))
        
        # Campo Cor
        tk.Label(frame_form, text="Cor:", font=('Arial', 10, 'bold'),
                bg="#f0f0f0", anchor='w').pack(fill='x', pady=(5, 2))
        
        cores = {
            "Azul": "#3498db",
            "Verde": "#2ecc71",
            "Vermelho": "#e74c3c",
            "Laranja": "#e67e22",
            "Roxo": "#9b59b6",
            "Amarelo": "#f39c12",
            "Cinza": "#95a5a6"
        }
        
        combo_cor = ttk.Combobox(frame_form, font=('Arial', 10), 
                                values=list(cores.keys()), state='readonly')
        combo_cor.pack(fill='x', pady=(0, 20))
        combo_cor.current(0)
        
        # Função para atualizar lista de pastas
        def atualizar_lista_pastas():
            for item in tree_pastas.get_children():
                tree_pastas.delete(item)
            
            pastas = self.db.listar_pastas()
            for pasta in pastas:
                num_pacientes = self.db.contar_pacientes_pasta(pasta[0])
                tree_pastas.insert('', 'end', values=(
                    pasta[0],  # ID
                    pasta[1],  # Nome
                    pasta[2] if pasta[2] else '-',  # Descrição
                    num_pacientes,  # Número de pacientes
                    pasta[4]  # Data criação
                ))
        
        # Função para limpar formulário
        def limpar_formulario():
            entry_nome.delete(0, tk.END)
            text_descricao.delete('1.0', tk.END)
            combo_cor.current(0)
            pasta_editando['id'] = None
            label_titulo_form.config(text="Nova Pasta")
            btn_salvar.config(text="💾 Salvar")
            btn_cancelar.pack_forget()
        
        # Função para carregar pasta no formulário
        def carregar_pasta_form(pasta_id):
            pasta = self.db.obter_pasta(pasta_id)
            if pasta:
                pasta_editando['id'] = pasta_id
                label_titulo_form.config(text="Editar Pasta")
                
                entry_nome.delete(0, tk.END)
                entry_nome.insert(0, pasta[1])
                
                text_descricao.delete('1.0', tk.END)
                if pasta[2]:
                    text_descricao.insert('1.0', pasta[2])
                
                cor_atual = pasta[3]
                for nome, valor in cores.items():
                    if valor == cor_atual:
                        combo_cor.set(nome)
                        break
                
                btn_salvar.config(text="💾 Atualizar")
                btn_cancelar.pack(side='left', padx=5, expand=True, fill='x')
        
        # Função para salvar pasta
        def salvar_pasta():
            nome = entry_nome.get().strip()
            if not nome:
                messagebox.showerror("Erro", "O nome da pasta é obrigatório!")
                return
            
            descricao = text_descricao.get('1.0', tk.END).strip()
            cor = cores[combo_cor.get()]
            
            if pasta_editando['id']:
                sucesso, mensagem = self.db.atualizar_pasta(pasta_editando['id'], nome, descricao, cor)
            else:
                sucesso, mensagem, _ = self.db.criar_pasta(nome, descricao, cor)
            
            if sucesso:
                messagebox.showinfo("Sucesso", mensagem)
                atualizar_lista_pastas()
                self.atualizar_combo_pastas()
                limpar_formulario()
            else:
                messagebox.showerror("Erro", mensagem)
        
        # Função para editar pasta selecionada
        def editar_pasta_selecionada():
            selecao = tree_pastas.selection()
            if selecao:
                item = tree_pastas.item(selecao[0])
                pasta_id = item['values'][0]
                carregar_pasta_form(pasta_id)
            else:
                messagebox.showwarning("Aviso", "Selecione uma pasta para editar!")
        
        # Função para deletar pasta
        def deletar_pasta_selecionada():
            selecao = tree_pastas.selection()
            if selecao:
                item = tree_pastas.item(selecao[0])
                pasta_id = item['values'][0]
                nome_pasta = item['values'][1]
                num_pacientes = item['values'][3]
                
                msg = f"Tem certeza que deseja excluir a pasta '{nome_pasta}'?"
                if num_pacientes > 0:
                    msg += f"\n\nExistem {num_pacientes} paciente(s) nesta pasta."
                    msg += "\nOs pacientes NÃO serão excluídos, apenas removidos desta pasta."
                
                resposta = messagebox.askyesno("Confirmar Exclusão", msg)
                if resposta:
                    sucesso, mensagem = self.db.deletar_pasta(pasta_id)
                    if sucesso:
                        messagebox.showinfo("Sucesso", mensagem)
                        atualizar_lista_pastas()
                        self.atualizar_combo_pastas()
                        self.atualizar_lista_pacientes()
                        if pasta_editando['id'] == pasta_id:
                            limpar_formulario()
                    else:
                        messagebox.showerror("Erro", mensagem)
            else:
                messagebox.showwarning("Aviso", "Selecione uma pasta para excluir!")
        
        # Botões do formulário
        frame_botoes_form = tk.Frame(frame_form, bg="#f0f0f0")
        frame_botoes_form.pack(fill='x', pady=(10, 0))
        
        btn_salvar = ttk.Button(frame_botoes_form, text="💾 Salvar", command=salvar_pasta,
                               style='Primary.TButton')
        btn_salvar.pack(side='left', padx=5, expand=True, fill='x')
        
        btn_cancelar = ttk.Button(frame_botoes_form, text="❌ Cancelar", command=limpar_formulario)
        # btn_cancelar só aparece quando está editando
        
        # Botões da lista
        btn_editar = ttk.Button(frame_botoes_lista, text="✏️ Editar", command=editar_pasta_selecionada)
        btn_editar.pack(side='left', padx=5)
        
        btn_deletar = ttk.Button(frame_botoes_lista, text="🗑️ Excluir", command=deletar_pasta_selecionada)
        btn_deletar.pack(side='left', padx=5)
        
        btn_fechar = ttk.Button(frame_botoes_lista, text="Fechar", command=janela.destroy)
        btn_fechar.pack(side='right', padx=5)
        
        # Carrega as pastas
        atualizar_lista_pastas()
    
    def criar_editar_pasta_dialog(self, parent, pasta_id=None, callback=None):
        janela = tk.Toplevel(parent)
        janela.title("Nova Pasta" if not pasta_id else "Editar Pasta")
        janela.geometry("500x300")
        janela.transient(parent)
        janela.grab_set()
        
        # Carrega dados da pasta se for edição
        pasta_existente = None
        if pasta_id:
            pasta_existente = self.db.obter_pasta(pasta_id)
        
        # Campos
        frame_form = tk.Frame(janela, bg="#f0f0f0")
        frame_form.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Nome
        tk.Label(frame_form, text="Nome da Pasta*:", font=('Arial', 10, 'bold'),
                bg="#f0f0f0").grid(row=0, column=0, sticky='w', pady=5)
        entry_nome = ttk.Entry(frame_form, font=('Arial', 10))
        entry_nome.grid(row=0, column=1, sticky='ew', pady=5)
        
        # Descrição
        tk.Label(frame_form, text="Descrição:", font=('Arial', 10, 'bold'),
                bg="#f0f0f0").grid(row=1, column=0, sticky='w', pady=5)
        text_descricao = scrolledtext.ScrolledText(frame_form, font=('Arial', 10), 
                                                   height=5, wrap=tk.WORD)
        text_descricao.grid(row=1, column=1, sticky='ew', pady=5)
        
        # Cor
        tk.Label(frame_form, text="Cor:", font=('Arial', 10, 'bold'),
                bg="#f0f0f0").grid(row=2, column=0, sticky='w', pady=5)
        
        cores = {
            "Azul": "#3498db",
            "Verde": "#2ecc71",
            "Vermelho": "#e74c3c",
            "Laranja": "#e67e22",
            "Roxo": "#9b59b6",
            "Amarelo": "#f39c12",
            "Cinza": "#95a5a6"
        }
        
        combo_cor = ttk.Combobox(frame_form, font=('Arial', 10), 
                                values=list(cores.keys()), state='readonly')
        combo_cor.grid(row=2, column=1, sticky='ew', pady=5)
        combo_cor.current(0)
        
        frame_form.columnconfigure(1, weight=1)
        
        # Preenche campos se for edição
        if pasta_existente:
            entry_nome.insert(0, pasta_existente[1])
            if pasta_existente[2]:
                text_descricao.insert('1.0', pasta_existente[2])
            cor_atual = pasta_existente[3]
            for nome, valor in cores.items():
                if valor == cor_atual:
                    combo_cor.set(nome)
                    break
        
        # Botões
        frame_botoes = tk.Frame(janela, bg="#f0f0f0")
        frame_botoes.pack(fill='x', padx=20, pady=(0, 20))
        
        def salvar_pasta():
            nome = entry_nome.get().strip()
            if not nome:
                messagebox.showerror("Erro", "O nome da pasta é obrigatório!")
                return
            
            descricao = text_descricao.get('1.0', tk.END).strip()
            cor = cores[combo_cor.get()]
            
            if pasta_id:
                sucesso, mensagem = self.db.atualizar_pasta(pasta_id, nome, descricao, cor)
            else:
                sucesso, mensagem, _ = self.db.criar_pasta(nome, descricao, cor)
            
            if sucesso:
                messagebox.showinfo("Sucesso", mensagem)
                if callback:
                    callback()
                self.atualizar_combo_pastas()
                janela.destroy()
            else:
                messagebox.showerror("Erro", mensagem)
        
        btn_salvar = ttk.Button(frame_botoes, text="💾 Salvar", command=salvar_pasta,
                               style='Primary.TButton')
        btn_salvar.pack(side='left', padx=5, expand=True, fill='x')
        
        btn_cancelar = ttk.Button(frame_botoes, text="❌ Cancelar", command=janela.destroy)
        btn_cancelar.pack(side='left', padx=5, expand=True, fill='x')
    
    def gerenciar_pastas_paciente(self):
        if not self.paciente_selecionado:
            return
        
        paciente_id = self.paciente_selecionado[0]
        paciente_nome = self.paciente_selecionado[1]
        
        janela = tk.Toplevel(self.root)
        janela.title(f"Pastas de {paciente_nome}")
        janela.geometry("600x500")
        janela.transient(self.root)
        janela.grab_set()
        
        # Frame superior
        frame_topo = tk.Frame(janela, bg="#f0f0f0")
        frame_topo.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(frame_topo, text=f"Gerenciar Pastas - {paciente_nome}", 
                 font=('Arial', 12, 'bold'), background="#f0f0f0").pack()
        
        # Frame com duas listas lado a lado
        frame_listas = tk.Frame(janela, bg="#f0f0f0")
        frame_listas.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Lista de pastas disponíveis
        frame_esq = tk.Frame(frame_listas, bg="#f0f0f0")
        frame_esq.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        ttk.Label(frame_esq, text="Pastas Disponíveis", font=('Arial', 10, 'bold'),
                 background="#f0f0f0").pack(pady=(0, 5))
        
        frame_tree_disp = tk.Frame(frame_esq, bg="white", relief='solid', borderwidth=1)
        frame_tree_disp.pack(fill='both', expand=True)
        
        scrollbar_disp = ttk.Scrollbar(frame_tree_disp, orient='vertical')
        scrollbar_disp.pack(side='right', fill='y')
        
        tree_disponiveis = ttk.Treeview(frame_tree_disp, 
                                        columns=('ID', 'Nome'),
                                        show='tree headings',
                                        yscrollcommand=scrollbar_disp.set)
        scrollbar_disp.config(command=tree_disponiveis.yview)
        
        tree_disponiveis.heading('#0', text='')
        tree_disponiveis.heading('ID', text='ID')
        tree_disponiveis.heading('Nome', text='Nome da Pasta')
        
        tree_disponiveis.column('#0', width=0, stretch=False)
        tree_disponiveis.column('ID', width=50, anchor='center')
        tree_disponiveis.column('Nome', width=200)
        
        tree_disponiveis.pack(fill='both', expand=True)
        
        # Lista de pastas do paciente
        frame_dir = tk.Frame(frame_listas, bg="#f0f0f0")
        frame_dir.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        ttk.Label(frame_dir, text="Pastas do Paciente", font=('Arial', 10, 'bold'),
                 background="#f0f0f0").pack(pady=(0, 5))
        
        frame_tree_pac = tk.Frame(frame_dir, bg="white", relief='solid', borderwidth=1)
        frame_tree_pac.pack(fill='both', expand=True)
        
        scrollbar_pac = ttk.Scrollbar(frame_tree_pac, orient='vertical')
        scrollbar_pac.pack(side='right', fill='y')
        
        tree_paciente = ttk.Treeview(frame_tree_pac, 
                                     columns=('ID', 'Nome'),
                                     show='tree headings',
                                     yscrollcommand=scrollbar_pac.set)
        scrollbar_pac.config(command=tree_paciente.yview)
        
        tree_paciente.heading('#0', text='')
        tree_paciente.heading('ID', text='ID')
        tree_paciente.heading('Nome', text='Nome da Pasta')
        
        tree_paciente.column('#0', width=0, stretch=False)
        tree_paciente.column('ID', width=50, anchor='center')
        tree_paciente.column('Nome', width=200)
        
        tree_paciente.pack(fill='both', expand=True)
        
        # Função para atualizar listas
        def atualizar_listas():
            # Limpa as listas
            for item in tree_disponiveis.get_children():
                tree_disponiveis.delete(item)
            for item in tree_paciente.get_children():
                tree_paciente.delete(item)
            
            # Obtém todas as pastas e as pastas do paciente
            todas_pastas = self.db.listar_pastas()
            pastas_paciente = self.db.obter_pastas_paciente(paciente_id)
            pastas_paciente_ids = [p[0] for p in pastas_paciente]
            
            # Preenche as listas
            for pasta in todas_pastas:
                if pasta[0] in pastas_paciente_ids:
                    tree_paciente.insert('', 'end', values=(pasta[0], pasta[1]))
                else:
                    tree_disponiveis.insert('', 'end', values=(pasta[0], pasta[1]))
        
        # Botões de ação
        frame_botoes = tk.Frame(janela, bg="#f0f0f0")
        frame_botoes.pack(fill='x', padx=10, pady=(0, 10))
        
        def adicionar_pasta():
            selecao = tree_disponiveis.selection()
            if selecao:
                item = tree_disponiveis.item(selecao[0])
                pasta_id = item['values'][0]
                
                sucesso, mensagem = self.db.adicionar_paciente_pasta(paciente_id, pasta_id)
                if sucesso:
                    atualizar_listas()
                    self.atualizar_combo_pastas()
                else:
                    messagebox.showerror("Erro", mensagem)
            else:
                messagebox.showwarning("Aviso", "Selecione uma pasta disponível!")
        
        def remover_pasta():
            selecao = tree_paciente.selection()
            if selecao:
                item = tree_paciente.item(selecao[0])
                pasta_id = item['values'][0]
                
                sucesso, mensagem = self.db.remover_paciente_pasta(paciente_id, pasta_id)
                if sucesso:
                    atualizar_listas()
                    self.atualizar_combo_pastas()
                else:
                    messagebox.showerror("Erro", mensagem)
            else:
                messagebox.showwarning("Aviso", "Selecione uma pasta do paciente!")
        
        btn_adicionar = ttk.Button(frame_botoes, text="➕ Adicionar à Pasta", command=adicionar_pasta)
        btn_adicionar.pack(side='left', padx=5)
        
        btn_remover = ttk.Button(frame_botoes, text="➖ Remover da Pasta", command=remover_pasta)
        btn_remover.pack(side='left', padx=5)
        
        btn_fechar = ttk.Button(frame_botoes, text="Fechar", command=janela.destroy)
        btn_fechar.pack(side='right', padx=5)
        
        # Carrega as listas
        atualizar_listas()
    
    def ao_fechar(self):
        self.db.close()
        self.root.destroy()


def main():
    root = tk.Tk()
    app = ClinicaApp(root)
    root.protocol("WM_DELETE_WINDOW", app.ao_fechar)
    root.mainloop()


if __name__ == "__main__":
    main()
