FROM python:3.10

# Define diretório de trabalho
WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y netcat-openbsd build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

# Copia requirements
COPY requirements.txt /app/

# Instala pacotes Python
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copia o projeto inteiro
COPY . /app/

# Copia script de espera
COPY wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

# Expõe porta interna do Django
EXPOSE 8000

# Comando padrão ao iniciar o container
CMD [ "sh", "-c", "/wait-for-it.sh db:5432 -- python manage.py migrate && python manage.py runserver 0.0.0.0:8000" ]



