import sqlite3
import os
from datetime import datetime

class Database:
    def __init__(self, db_name="clinica.db"):
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_tables()
    
    def connect(self):
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
    
    def create_tables(self):
        # Tabela de pacientes
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS pacientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                data_nascimento TEXT,
                cpf TEXT,
                telefone TEXT,
                email TEXT,
                endereco TEXT,
                sexo TEXT,
                data_cadastro TEXT NOT NULL,
                historico_clinico TEXT,
                tratamento_atual TEXT,
                observacoes TEXT
            )
        ''')
        
        # Tabela de pastas/categorias
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS pastas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL UNIQUE,
                descricao TEXT,
                cor TEXT,
                data_criacao TEXT NOT NULL
            )
        ''')
        
        # Tabela de relacionamento paciente-pasta (muitos para muitos)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS paciente_pasta (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                paciente_id INTEGER NOT NULL,
                pasta_id INTEGER NOT NULL,
                data_adicao TEXT NOT NULL,
                FOREIGN KEY (paciente_id) REFERENCES pacientes (id) ON DELETE CASCADE,
                FOREIGN KEY (pasta_id) REFERENCES pastas (id) ON DELETE CASCADE,
                UNIQUE(paciente_id, pasta_id)
            )
        ''')
        
        self.conn.commit()
    
    def adicionar_paciente(self, dados):
        try:
            self.cursor.execute('''
                INSERT INTO pacientes (
                    nome, data_nascimento, cpf, telefone, email, 
                    endereco, sexo, data_cadastro, historico_clinico, 
                    tratamento_atual, observacoes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                dados['nome'].upper(),
                dados.get('data_nascimento', ''),
                dados.get('cpf', ''),
                dados.get('telefone', ''),
                dados.get('email', ''),
                dados.get('endereco', ''),
                dados.get('sexo', ''),
                datetime.now().strftime("%d/%m/%Y %H:%M"),
                dados.get('historico_clinico', ''),
                dados.get('tratamento_atual', ''),
                dados.get('observacoes', '')
            ))
            self.conn.commit()
            return True, "Paciente cadastrado com sucesso!"
        except Exception as e:
            return False, f"Erro ao cadastrar paciente: {str(e)}"
    
    def atualizar_paciente(self, id_paciente, dados):
        try:
            self.cursor.execute('''
                UPDATE pacientes SET
                    nome = ?,
                    data_nascimento = ?,
                    cpf = ?,
                    telefone = ?,
                    email = ?,
                    endereco = ?,
                    sexo = ?,
                    historico_clinico = ?,
                    tratamento_atual = ?,
                    observacoes = ?
                WHERE id = ?
            ''', (
                dados['nome'].upper(),
                dados.get('data_nascimento', ''),
                dados.get('cpf', ''),
                dados.get('telefone', ''),
                dados.get('email', ''),
                dados.get('endereco', ''),
                dados.get('sexo', ''),
                dados.get('historico_clinico', ''),
                dados.get('tratamento_atual', ''),
                dados.get('observacoes', ''),
                id_paciente
            ))
            self.conn.commit()
            return True, "Paciente atualizado com sucesso!"
        except Exception as e:
            return False, f"Erro ao atualizar paciente: {str(e)}"
    
    def buscar_pacientes(self, termo_busca="", pasta_id=None):
        try:
            if pasta_id:
                # Busca pacientes de uma pasta específica
                if termo_busca:
                    self.cursor.execute('''
                        SELECT DISTINCT p.* FROM pacientes p
                        INNER JOIN paciente_pasta pp ON p.id = pp.paciente_id
                        WHERE pp.pasta_id = ? 
                        AND (p.nome LIKE ? OR p.cpf LIKE ? OR p.telefone LIKE ?)
                        ORDER BY p.nome
                    ''', (pasta_id, f'%{termo_busca}%', f'%{termo_busca}%', f'%{termo_busca}%'))
                else:
                    self.cursor.execute('''
                        SELECT DISTINCT p.* FROM pacientes p
                        INNER JOIN paciente_pasta pp ON p.id = pp.paciente_id
                        WHERE pp.pasta_id = ?
                        ORDER BY p.nome
                    ''', (pasta_id,))
            else:
                # Busca todos os pacientes
                if termo_busca:
                    self.cursor.execute('''
                        SELECT * FROM pacientes 
                        WHERE nome LIKE ? OR cpf LIKE ? OR telefone LIKE ?
                        ORDER BY nome
                    ''', (f'%{termo_busca}%', f'%{termo_busca}%', f'%{termo_busca}%'))
                else:
                    self.cursor.execute('SELECT * FROM pacientes ORDER BY nome')
            
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Erro ao buscar pacientes: {str(e)}")
            return []
    
    def obter_paciente(self, id_paciente):
        try:
            self.cursor.execute('SELECT * FROM pacientes WHERE id = ?', (id_paciente,))
            return self.cursor.fetchone()
        except Exception as e:
            print(f"Erro ao obter paciente: {str(e)}")
            return None
    
    def deletar_paciente(self, id_paciente):
        try:
            self.cursor.execute('DELETE FROM pacientes WHERE id = ?', (id_paciente,))
            self.conn.commit()
            return True, "Paciente removido com sucesso!"
        except Exception as e:
            return False, f"Erro ao remover paciente: {str(e)}"
    
    def criar_pasta(self, nome, descricao="", cor="#3498db"):
        try:
            self.cursor.execute('''
                INSERT INTO pastas (nome, descricao, cor, data_criacao)
                VALUES (?, ?, ?, ?)
            ''', (nome, descricao, cor, datetime.now().strftime("%d/%m/%Y %H:%M")))
            self.conn.commit()
            return True, "Pasta criada com sucesso!", self.cursor.lastrowid
        except sqlite3.IntegrityError:
            return False, "Já existe uma pasta com este nome!", None
        except Exception as e:
            return False, f"Erro ao criar pasta: {str(e)}", None
    
    def atualizar_pasta(self, pasta_id, nome, descricao="", cor="#3498db"):
        try:
            self.cursor.execute('''
                UPDATE pastas SET nome = ?, descricao = ?, cor = ?
                WHERE id = ?
            ''', (nome, descricao, cor, pasta_id))
            self.conn.commit()
            return True, "Pasta atualizada com sucesso!"
        except sqlite3.IntegrityError:
            return False, "Já existe uma pasta com este nome!"
        except Exception as e:
            return False, f"Erro ao atualizar pasta: {str(e)}"
    
    def deletar_pasta(self, pasta_id):
        try:
            self.cursor.execute('DELETE FROM pastas WHERE id = ?', (pasta_id,))
            self.conn.commit()
            return True, "Pasta removida com sucesso!"
        except Exception as e:
            return False, f"Erro ao remover pasta: {str(e)}"
    
    def listar_pastas(self):
        try:
            self.cursor.execute('SELECT * FROM pastas ORDER BY nome')
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Erro ao listar pastas: {str(e)}")
            return []
    
    def obter_pasta(self, pasta_id):
        try:
            self.cursor.execute('SELECT * FROM pastas WHERE id = ?', (pasta_id,))
            return self.cursor.fetchone()
        except Exception as e:
            print(f"Erro ao obter pasta: {str(e)}")
            return None
    
    def adicionar_paciente_pasta(self, paciente_id, pasta_id):
        try:
            self.cursor.execute('''
                INSERT INTO paciente_pasta (paciente_id, pasta_id, data_adicao)
                VALUES (?, ?, ?)
            ''', (paciente_id, pasta_id, datetime.now().strftime("%d/%m/%Y %H:%M")))
            self.conn.commit()
            return True, "Paciente adicionado à pasta com sucesso!"
        except sqlite3.IntegrityError:
            return False, "Paciente já está nesta pasta!"
        except Exception as e:
            return False, f"Erro ao adicionar paciente à pasta: {str(e)}"
    
    def remover_paciente_pasta(self, paciente_id, pasta_id):
        try:
            self.cursor.execute('''
                DELETE FROM paciente_pasta 
                WHERE paciente_id = ? AND pasta_id = ?
            ''', (paciente_id, pasta_id))
            self.conn.commit()
            return True, "Paciente removido da pasta com sucesso!"
        except Exception as e:
            return False, f"Erro ao remover paciente da pasta: {str(e)}"
    
    def obter_pastas_paciente(self, paciente_id):
        try:
            self.cursor.execute('''
                SELECT p.* FROM pastas p
                INNER JOIN paciente_pasta pp ON p.id = pp.pasta_id
                WHERE pp.paciente_id = ?
                ORDER BY p.nome
            ''', (paciente_id,))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Erro ao obter pastas do paciente: {str(e)}")
            return []
    
    def contar_pacientes_pasta(self, pasta_id):
        try:
            self.cursor.execute('''
                SELECT COUNT(*) FROM paciente_pasta
                WHERE pasta_id = ?
            ''', (pasta_id,))
            resultado = self.cursor.fetchone()
            return resultado[0] if resultado else 0
        except Exception as e:
            print(f"Erro ao contar pacientes da pasta: {str(e)}")
            return 0
    
    def close(self):
        if self.conn:
            self.conn.close()

