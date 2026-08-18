FROM python:3.11-slim

WORKDIR /app

# Copia e instala as dependências primeiro para aproveitar o cache do Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código do projeto para dentro do container
COPY . .

# Comando padrão executado quando o container subir
CMD ["python", "bot.py"]