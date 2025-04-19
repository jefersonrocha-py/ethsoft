from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash, send_from_directory
)
import pandas as pd
from datetime import datetime
import unicodedata
import os
from fpdf import FPDF
import plotly.express as px
from werkzeug.security import generate_password_hash
from units import lista_unidades, get_units_with_ids

# Importar funções do banco de dados
from database import (
    init_db, load_history, save_history,
    add_user, verify_credentials
)

app = Flask(__name__)
app.secret_key = 'substitua-por-uma-chave-segura'

# --- Configuração do Diretório ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
REPORT_DIR = os.path.join(DATA_DIR, 'daily-reports')
DASHBOARD_DIR = os.path.join(DATA_DIR, 'dashboard-reports')
EXPORT_DIR = os.path.join(DATA_DIR, 'exports')

os.makedirs(REPORT_DIR, exist_ok=True)
os.makedirs(DASHBOARD_DIR, exist_ok=True)
os.makedirs(EXPORT_DIR, exist_ok=True)

# --- Unidades ---
# Removida a definição duplicada, mantendo apenas uma definição para 'unidades'
unidades = get_units_with_ids()

# --- Limpeza de texto para PDF ---
def limpar_texto(texto):
    if texto is None:
        return ''
    txt = str(texto)
    return unicodedata.normalize('NFKD', txt).encode('latin-1', 'ignore').decode('latin-1')

# --- PDF Report ---
class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, limpar_texto(self.title), ln=True, align='C')
        self.ln(5)

    def generate(self, df, title):
        self.title = title
        self.add_page()
        self.set_font('Arial', '', 10)
        total = len(df)
        on = (df.status == 'ON').sum()
        off = (df.status == 'OFF').sum()
        pct_on = on / total * 100 if total else 0
        pct_off = off / total * 100 if total else 0
        self.cell(0, 8, limpar_texto(f"Total: {total} | ON: {on} ({pct_on:.2f}%) | OFF: {off} ({pct_off:.2f}%)"), ln=True)
        self.ln(5)
        self.set_font('Arial', 'B', 9)
        for h, w in zip(['Data', 'Unidade', 'Status'], [30, 110, 30]):
            self.cell(w, 8, limpar_texto(h), border=1)
        self.ln()
        self.set_font('Arial', '', 8)
        for _, r in df.iterrows():
            self.cell(30, 6, limpar_texto(r.data.strftime('%Y-%m-%d')), border=1)
            self.cell(110, 6, limpar_texto(r.unidade[:60]), border=1)
            self.cell(30, 6, limpar_texto(r.status), border=1)
            self.ln()

# --- Dashboard PDF Report ---
class DashboardPDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, limpar_texto(self.title), ln=True, align='C')
        self.ln(5)

    def generate(self, agg_data, summary, start_date, end_date, group_by):
        self.title = f"Dashboard de Relatórios ({start_date} a {end_date})"
        self.add_page()
        
        # Informações do filtro
        self.set_font('Arial', 'B', 10)
        self.cell(0, 8, limpar_texto(f"Período: {start_date} a {end_date} | Agrupamento: {group_by}"), ln=True)
        self.ln(5)
        
        # Resumo
        self.set_font('Arial', 'B', 12)
        self.cell(0, 8, "Resumo:", ln=True)
        self.set_font('Arial', '', 10)
        self.cell(0, 8, limpar_texto(f"Total de Registros: {summary['total']}"), ln=True)
        self.cell(0, 8, limpar_texto(f"Online: {summary['on']} ({summary['pct_on']:.2f}%)"), ln=True)
        self.cell(0, 8, limpar_texto(f"Offline: {summary['off']}"), ln=True)
        self.ln(10)
        
        # Tabela de dados
        self.set_font('Arial', 'B', 12)
        self.cell(0, 8, "Dados Agregados:", ln=True)
        self.set_font('Arial', 'B', 9)
        
        # Cabeçalhos da tabela
        col_widths = [40, 30, 30, 30, 30]
        headers = ['Data', 'ON', 'OFF', 'Total', '% ON']
        for h, w in zip(headers, col_widths):
            self.cell(w, 8, limpar_texto(h), border=1)
        self.ln()
        
        # Dados da tabela
        self.set_font('Arial', '', 8)
        for idx, row in agg_data.iterrows():
            date_str = idx.strftime('%Y-%m-%d') if hasattr(idx, 'strftime') else str(idx)
            self.cell(col_widths[0], 6, limpar_texto(date_str), border=1)
            self.cell(col_widths[1], 6, limpar_texto(str(row.get('ON', 0))), border=1)
            self.cell(col_widths[2], 6, limpar_texto(str(row.get('OFF', 0))), border=1)
            self.cell(col_widths[3], 6, limpar_texto(str(row.get('Total', 0))), border=1)
            self.cell(col_widths[4], 6, limpar_texto(f"{row.get('% ON', 0):.2f}%"), border=1)
            self.ln()

# --- Full Table PDF Report ---
class FullTablePDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, limpar_texto(self.title), ln=True, align='C')
        self.ln(5)

    def generate(self, df, start_date, end_date):
        self.title = f"Relatório Completo de Unidades ({start_date} a {end_date})"
        self.add_page('L')  # Landscape para acomodar mais colunas
        
        # Informações do filtro
        self.set_font('Arial', 'B', 10)
        self.cell(0, 8, limpar_texto(f"Período: {start_date} a {end_date}"), ln=True)
        self.ln(5)
        
        # Resumo
        self.set_font('Arial', 'B', 12)
        self.cell(0, 8, "Resumo:", ln=True)
        self.set_font('Arial', '', 10)
        total = len(df)
        on = (df.status == 'ON').sum()
        off = (df.status == 'OFF').sum()
        pct_on = on / total * 100 if total else 0
        self.cell(0, 8, limpar_texto(f"Total de Registros: {total}"), ln=True)
        self.cell(0, 8, limpar_texto(f"Online: {on} ({pct_on:.2f}%)"), ln=True)
        self.cell(0, 8, limpar_texto(f"Offline: {off}"), ln=True)
        self.ln(10)
        
        # Tabela de dados
        self.set_font('Arial', 'B', 12)
        self.cell(0, 8, "Tabela Completa de Unidades:", ln=True)
        self.set_font('Arial', 'B', 9)
        
        # Cabeçalhos da tabela
        col_widths = [25, 20, 180, 40]
        headers = ['Data', 'ID', 'Unidade', 'Status']
        for h, w in zip(headers, col_widths):
            self.cell(w, 8, limpar_texto(h), border=1)
        self.ln()
        
        # Dados da tabela
        self.set_font('Arial', '', 8)
        for _, r in df.iterrows():
            date_str = r.data.strftime('%Y-%m-%d') if hasattr(r.data, 'strftime') else str(r.data)
            self.cell(col_widths[0], 6, limpar_texto(date_str), border=1)
            self.cell(col_widths[1], 6, limpar_texto(str(r.id)), border=1)
            self.cell(col_widths[2], 6, limpar_texto(r.unidade[:100]), border=1)
            self.cell(col_widths[3], 6, limpar_texto(r.status), border=1)
            self.ln()

# --- Proteção de Rotas ---
@app.before_request
def require_login():
    open_paths = {'/login', '/register', '/welcome'}
    if request.path.startswith('/static/') or request.path in open_paths:
        return
    if 'user_id' not in session:
        return redirect(url_for('login'))

# --- LOGIN ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password']
        try:
            user_data = verify_credentials(user, pwd)
            if user_data:
                session['user_id'] = user_data['id']
                session['username'] = user_data['username']
                return redirect(url_for('welcome'))
            flash('Usuário ou senha inválidos.', 'error')
        except Exception as e:
            flash(str(e), 'error')
    return render_template('login.html')

# --- REGISTER ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        pwd = request.form['password']
        conf = request.form['confirm_password']
        if pwd != conf:
            flash('Senhas não coincidem.', 'error')
            return redirect(url_for('register'))
        hashed = generate_password_hash(pwd)
        try:
            add_user(username, email, hashed)
            flash('Registrado com sucesso! Faça login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash(str(e), 'error')
    return render_template('register.html')

# --- WELCOME ---
@app.route('/welcome')
def welcome():
    return render_template('welcome.html', username=session.get('username'))

# --- STATUS ---
@app.route('/status', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
def status():
    global df_history
    if request.method == 'POST':
        try:
            # Corrigido: Usar datetime.strptime para converter a data com formato explícito
            report_date_str = request.form['report_date']
            rep_date = datetime.strptime(report_date_str, '%Y-%m-%d').date()
            
            regs = []
            for u in unidades:
                key = f"status_{u['id']}"
                stat = 'ON' if request.form.get(key) == 'on' else 'OFF'
                # Usar objeto datetime completo para compatibilidade com pandas
                regs.append({
                    'data': datetime.combine(rep_date, datetime.min.time()),  # Adiciona componente de tempo
                    'id': u['id'], 
                    'unidade': u['unidade'], 
                    'status': stat
                })
            
            df_new = pd.DataFrame(regs)
            df_history = pd.concat([df_history, df_new], ignore_index=True)
            save_history(df_history)
            
            pdf = PDFReport()
            title = f"Relatório {rep_date.strftime('%d/%m/%Y')}"
            pdf.generate(df_new, title)
            fname = f"relatorio_{rep_date}.pdf"
            pdf.output(os.path.join(REPORT_DIR, fname))
            
            flash(f'Relatório salvo: {fname}', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            flash(f'Erro ao gerar relatório: {str(e)}', 'error')
            return redirect(url_for('status'))
    
    # Por padrão, todas as unidades começam como online
    online_count = len(unidades)
    offline_count = 0
    
    today = datetime.today().strftime('%Y-%m-%d')
    return render_template('status.html', 
                          unidades=unidades, 
                          current_date=today,
                          online_count=online_count,
                          offline_count=offline_count)

# --- DASHBOARD ---
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    global df_history
    if df_history.empty:
        flash('Nenhum relatório encontrado.', 'warning')
        return redirect(url_for('status'))
    
    try:
        df = df_history.copy()
        
        # Garantir que a coluna 'data' seja datetime
        if not pd.api.types.is_datetime64_any_dtype(df['data']):
            df['data'] = pd.to_datetime(df['data'], errors='coerce')
        
        start = df.data.min().date() if not df.empty else datetime.today().date()
        end = df.data.max().date() if not df.empty else datetime.today().date()
        group = 'Diário'
        
        if request.method == 'POST':
            start_str = request.form.get('start_date', start)
            end_str = request.form.get('end_date', end)
            
            # Converter strings para datetime
            try:
                start = datetime.strptime(start_str, '%Y-%m-%d').date()
            except:
                start = datetime.today().date()
                
            try:
                end = datetime.strptime(end_str, '%Y-%m-%d').date()
            except:
                end = datetime.today().date()
                
            group = request.form.get('group_by', 'Diário')
        
        # Converter datas para datetime para comparação
        start_dt = pd.to_datetime(start)
        end_dt = pd.to_datetime(end)
        
        mask = (df.data >= start_dt) & (df.data <= end_dt)
        dff = df.loc[mask]
        
        if dff.empty:
            flash('Nenhum dado disponível para o período selecionado.', 'warning')
            return redirect(url_for('status'))
        
        if group == 'Diário':
            agg = dff.groupby(dff.data.dt.date).status.value_counts().unstack(fill_value=0)
        elif group == 'Semanal':
            agg = dff.groupby(dff.data.dt.to_period('W').apply(lambda r: r.start_time)).status.value_counts().unstack(fill_value=0)
        else:
            agg = dff.groupby(dff.data.dt.to_period('M').dt.to_timestamp()).status.value_counts().unstack(fill_value=0)
        
        agg = agg.assign(ON=lambda x: x.get('ON', 0), OFF=lambda x: x.get('OFF', 0))
        agg['Total'] = agg.ON + agg.OFF
        agg['% ON'] = agg.ON / agg.Total * 100
        
        # Gráfico de Barras
        # Preparar dados para o gráfico de barras
        bar_data = []
        for idx, row in agg.iterrows():
            date_str = idx.strftime('%Y-%m-%d') if hasattr(idx, 'strftime') else str(idx)
            bar_data.append({'data': date_str, 'ON': row.get('ON', 0), 'OFF': row.get('OFF', 0)})
        
        bar_df = pd.DataFrame(bar_data)
        if not bar_df.empty:
            bar = px.bar(bar_df, x='data', y=['ON', 'OFF'], title='Status por Período',
                        labels={'value': 'Quantidade', 'variable': 'Status'},
                        color_discrete_map={'ON': '#4CAF50', 'OFF': '#F44336'})
            bar_graph = bar.to_html(full_html=False)
        else:
            bar_graph = "<p>Sem dados suficientes para gerar o gráfico de barras</p>"
        
        summary = {
            'total': len(dff),
            'on': (dff.status == 'ON').sum(),
            'off': (dff.status == 'OFF').sum(),
            'pct_on': (dff.status == 'ON').sum() / len(dff) * 100 if len(dff) else 0
        }
        
        return render_template(
            'dashboard.html',
            tables=[agg.to_html(classes='data', border=0)],
            bar_graph=bar_graph,
            summary=summary,
            start=start, end=end, group=group
        )
    except Exception as e:
        flash(f'Erro ao carregar dashboard: {str(e)}', 'error')
        return redirect(url_for('status'))

# --- EXPORT DASHBOARD PDF ---
@app.route('/export_dashboard_pdf')
def export_dashboard_pdf():
    global df_history
    if df_history.empty:
        flash('Nenhum relatório encontrado para exportar.', 'warning')
        return redirect(url_for('dashboard'))
    
    try:
        # Obter parâmetros da URL
        start_str = request.args.get('start', datetime.today().date().strftime('%Y-%m-%d'))
        end_str = request.args.get('end', datetime.today().date().strftime('%Y-%m-%d'))
        group = request.args.get('group', 'Diário')
        
        # Converter strings para datetime
        try:
            start = datetime.strptime(start_str, '%Y-%m-%d').date()
        except:
            start = datetime.today().date()
            
        try:
            end = datetime.strptime(end_str, '%Y-%m-%d').date()
        except:
            end = datetime.today().date()
        
        # Processar dados
        df = df_history.copy()
        
        # Garantir que a coluna 'data' seja datetime
        if not pd.api.types.is_datetime64_any_dtype(df['data']):
            df['data'] = pd.to_datetime(df['data'], errors='coerce')
        
        # Converter datas para datetime para comparação
        start_dt = pd.to_datetime(start)
        end_dt = pd.to_datetime(end)
        
        mask = (df.data >= start_dt) & (df.data <= end_dt)
        dff = df.loc[mask]
        
        if dff.empty:
            flash('Nenhum dado disponível para o período selecionado.', 'warning')
            return redirect(url_for('dashboard'))
        
        # Agregar dados
        if group == 'Diário':
            agg = dff.groupby(dff.data.dt.date).status.value_counts().unstack(fill_value=0)
        elif group == 'Semanal':
            agg = dff.groupby(dff.data.dt.to_period('W').apply(lambda r: r.start_time)).status.value_counts().unstack(fill_value=0)
        else:
            agg = dff.groupby(dff.data.dt.to_period('M').dt.to_timestamp()).status.value_counts().unstack(fill_value=0)
        
        agg = agg.assign(ON=lambda x: x.get('ON', 0), OFF=lambda x: x.get('OFF', 0))
        agg['Total'] = agg.ON + agg.OFF
        agg['% ON'] = agg.ON / agg.Total * 100
        
        # Calcular resumo
        summary = {
            'total': len(dff),
            'on': (dff.status == 'ON').sum(),
            'off': (dff.status == 'OFF').sum(),
            'pct_on': (dff.status == 'ON').sum() / len(dff) * 100 if len(dff) else 0
        }
        
        # Gerar PDF
        pdf = DashboardPDFReport()
        pdf.generate(agg, summary, start, end, group)
        
        # Salvar PDF
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        fname = f"dashboard_{timestamp}.pdf"
        pdf_path = os.path.join(DASHBOARD_DIR, fname)
        pdf.output(pdf_path)
        
        flash(f'Dashboard exportado com sucesso!', 'success')
        return send_from_directory(DASHBOARD_DIR, fname, as_attachment=True)
    except Exception as e:
        flash(f'Erro ao exportar dashboard: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

# --- EXPORT FULL TABLE ---
@app.route('/export_full_table')
def export_full_table():
    global df_history
    if df_history.empty:
        flash('Nenhum relatório encontrado para exportar.', 'warning')
        return redirect(url_for('dashboard'))
    
    try:
        # Obter parâmetros da URL
        start_str = request.args.get('start', datetime.today().date().strftime('%Y-%m-%d'))
        end_str = request.args.get('end', datetime.today().date().strftime('%Y-%m-%d'))
        
        # Converter strings para datetime
        try:
            start = datetime.strptime(start_str, '%Y-%m-%d').date()
        except:
            start = datetime.today().date()
            
        try:
            end = datetime.strptime(end_str, '%Y-%m-%d').date()
        except:
            end = datetime.today().date()
        
        # Processar dados
        df = df_history.copy()
        
        # Garantir que a coluna 'data' seja datetime
        if not pd.api.types.is_datetime64_any_dtype(df['data']):
            df['data'] = pd.to_datetime(df['data'], errors='coerce')
        
        # Converter datas para datetime para comparação
        start_dt = pd.to_datetime(start)
        end_dt = pd.to_datetime(end)
        
        mask = (df.data >= start_dt) & (df.data <= end_dt)
        dff = df.loc[mask]
        
        if dff.empty:
            flash('Nenhum dado disponível para o período selecionado.', 'warning')
            return redirect(url_for('dashboard'))
        
        # Ordenar por data e ID
        dff = dff.sort_values(['data', 'id'])
        
        # Gerar PDF com tabela completa
        pdf = FullTablePDFReport()
        pdf.generate(dff, start, end)
        
        # Salvar PDF
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        fname = f"tabela_completa_{timestamp}.pdf"
        pdf_path = os.path.join(EXPORT_DIR, fname)
        pdf.output(pdf_path)
        
        flash(f'Tabela completa exportada com sucesso!', 'success')
        return send_from_directory(EXPORT_DIR, fname, as_attachment=True)
    except Exception as e:
        flash(f'Erro ao exportar tabela completa: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

# --- LOGOUT ---
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- DOWNLOAD PDF ---
@app.route('/reports/<filename>')
def download_report(filename):
    return send_from_directory(REPORT_DIR, filename)

if __name__ == '__main__':
    init_db()
    df_history = load_history()
    app.run(host='0.0.0.0', port=5000, debug=True)
