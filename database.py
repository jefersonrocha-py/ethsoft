import sqlite3
import os
import pandas as pd

# --- Configuração do Diretório ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
USERS_DB = os.path.join(DATA_DIR, 'users.db')
HISTORY_CSV = os.path.join(DATA_DIR, 'status_history.csv')

os.makedirs(DATA_DIR, exist_ok=True)

# --- Conexão com o Banco de Dados ---
def get_db_connection():
    conn = sqlite3.connect(USERS_DB)
    conn.row_factory = sqlite3.Row
    return conn

# --- Inicialização do Banco de Dados ---
def init_db():
    conn = get_db_connection()
    conn.execute('''
      CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email    TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
      )
    ''')
    conn.commit()
    conn.close()

# --- Carregar Histórico de Status ---
def load_history():
    if os.path.exists(HISTORY_CSV):
        return pd.read_csv(HISTORY_CSV, parse_dates=['data'])
    return pd.DataFrame(columns=['data', 'id', 'unidade', 'status'])

# --- Salvar Histórico de Status ---
def save_history(df):
    df.to_csv(HISTORY_CSV, index=False)

# --- Adicionar Usuário ---
def add_user(username, email, password):
    conn = get_db_connection()
    try:
        conn.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', (username, email, password))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        raise ValueError("Usuário ou email já cadastrado.")
    conn.close()

# --- Verificar Credenciais de Login ---
def verify_credentials(username, password):
    from werkzeug.security import check_password_hash  # Importação local para evitar conflitos
    conn = get_db_connection()
    row = conn.execute('SELECT * FROM users WHERE username=?', (username,)).fetchone()
    conn.close()
    if row and check_password_hash(row['password'], password):
        return {'id': row['id'], 'username': row['username']}
    return None