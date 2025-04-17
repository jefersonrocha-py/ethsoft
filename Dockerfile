# Use uma imagem oficial do Python como base
FROM python:3.9-slim

# Defina o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copie os arquivos necessários para o contêiner
COPY . .

# Instale as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Exponha a porta padrão do Streamlit
EXPOSE 8501

# Comando para executar o aplicativo
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]