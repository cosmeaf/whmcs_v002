#!/bin/bash

# Definir o PATH do servidor automaticamente
PROJECT_PATH="/opt/whmcs"
LOG_DIR="/var/log/django"
LOG_FILE="$LOG_DIR/django.log"
CELERY_CMD="celery -A core worker -l info -n worker1@%h"
DJANGO_CMD="python3 manage.py runserver 0.0.0.0:7000"

# Função para criar o diretório de log e o arquivo de log se não existirem
create_log_file() {
    mkdir -p "$LOG_DIR"
    if [ ! -f "$LOG_FILE" ]; then
        touch "$LOG_FILE"
    fi
}

# Função para logar as mensagens no formato especificado
log_message() {
    local LOG_TYPE=$1
    local LOG_NAME=$2
    local LOGO=$3
    local MESSAGE=$4
    local DATE=$(date +"%d-%m-%Y %H:%M:%S")

    # Mensagem colorida no terminal
    echo -e "\e[${LOGO}m$DATE - $LOG_TYPE - $LOG_NAME - $MESSAGE\e[0m"
    
    # Mensagem sem cor no arquivo de log
    echo "$DATE - $LOG_TYPE - $LOG_NAME - $MESSAGE" >> "$LOG_FILE"
}

# Função para fazer a rotação dos logs a cada 30 dias
rotate_logs() {
    find "$LOG_DIR" -name "django.log*" -mtime +30 -exec gzip {} \;
    find "$LOG_DIR" -name "django.log*.gz" -mtime +30 -exec rm {} \;
}

# Função para iniciar os serviços
start_server() {
    log_message "INFO" "START" "32" "Iniciando Celery..."
    cd "$PROJECT_PATH" || { log_message "ERROR" "START" "31" "Erro ao acessar o diretório $PROJECT_PATH"; exit 1; }
    $CELERY_CMD &>> "$LOG_FILE" &
    CELERY_PID=$!
    log_message "INFO" "START" "32" "Celery iniciado com PID $CELERY_PID"

    log_message "INFO" "START" "32" "Iniciando Django..."
    $DJANGO_CMD &>> "$LOG_FILE" &
    DJANGO_PID=$!
    log_message "INFO" "START" "32" "Django iniciado com PID $DJANGO_PID"

    echo "$CELERY_PID" > celery.pid
    echo "$DJANGO_PID" > django.pid
}

# Função para parar os serviços
stop_server() {
    if [ -f "celery.pid" ]; then
        CELERY_PID=$(cat celery.pid)
        if ps -p "$CELERY_PID" > /dev/null; then
            log_message "INFO" "STOP" "33" "Parando Celery com PID $CELERY_PID..."
            kill "$CELERY_PID" && rm -f celery.pid
        else
            log_message "WARNING" "STOP" "33" "Celery já está parado. Removendo o arquivo celery.pid."
            rm -f celery.pid
        fi
    else
        log_message "WARNING" "STOP" "33" "Arquivo celery.pid não encontrado. Celery pode já estar parado."
    fi

    if [ -f "django.pid" ]; then
        DJANGO_PID=$(cat django.pid)
        if ps -p "$DJANGO_PID" > /dev/null; then
            log_message "INFO" "STOP" "33" "Parando Django com PID $DJANGO_PID..."
            kill "$DJANGO_PID" && rm -f django.pid
        else
            log_message "WARNING" "STOP" "33" "Django já está parado. Removendo o arquivo django.pid."
            rm -f django.pid
        fi
    else
        log_message "WARNING" "STOP" "33" "Arquivo django.pid não encontrado. Django pode já estar parado."
    fi
}

# Função para reiniciar os serviços
restart_server() {
    stop_server
    start_server
}

# Tratamento de erros
error_handling() {
    log_message "ERROR" "SCRIPT" "31" "Erro ao executar $0. Saindo..."
    echo "Erro crítico ao executar o script. Veja $LOG_FILE para mais detalhes."
    exit 1
}

# Captura qualquer erro de execução do script
trap error_handling ERR

# Criar diretório e arquivo de log se não existirem
create_log_file

# Rodar a rotação de logs
rotate_logs

# Verificar o comando passado (start, stop, restart)
case "$1" in
    start)
        start_server
        ;;
    stop)
        stop_server
        ;;
    restart)
        restart_server
        ;;
    *)
        echo "Uso: $0 {start|stop|restart}"
        exit 1
        ;;
esac
