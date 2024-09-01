#!/bin/bash

# Caminho para o diretório do projeto Django
PROJECT_DIR="/opt/whmcs"

# Caminho para o ambiente virtual (opcional)
VENV_DIR="$PROJECT_DIR/venv"

# Ativar o ambiente virtual
source $VENV_DIR/bin/activate

# Navegar para o diretório do projeto
cd $PROJECT_DIR

echo "Removendo o banco de dados SQLite..."
# Remover o banco de dados SQLite
rm -f db.sqlite3

echo "Removendo todas as migrações..."
# Remover todas as migrações de todas as apps
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc"  -delete

echo "Removendo todos os diretórios __pycache__..."
# Remover todos os diretórios __pycache__ e arquivos .pyc
find . -type d -name "__pycache__" -exec rm -r {} +

echo "Criando novas migrações..."
# Criar novas migrações
python manage.py makemigrations

echo "Aplicando migrações..."
# Aplicar as migrações para recriar o banco de dados
python manage.py migrate

echo "Operação concluída com sucesso!"
