#!/bin/bash
# wait-for-it.sh
# Aguarda um host/porta estar disponível antes de executar um comando

set -e

HOST=""
PORT=""
TIMEOUT=30  # segundos padrão
CMD=""

print_usage() {
    echo "Uso: $0 host:porta [-t timeout] -- comando"
    echo "Exemplo: $0 db:5432 -- python manage.py runserver 0.0.0.0:8000"
}

# Parse arguments
while [[ "$#" -gt 0 ]]; do
    case "$1" in
        -t) TIMEOUT="$2"; shift 2 ;;
        --) CMD="${@:2}"; break ;;
        *) 
            if [[ "$1" == *:* ]]; then
                HOST="${1%%:*}"
                PORT="${1##*:}"
            else
                print_usage
                exit 1
            fi
            shift
            ;;
    esac
done

if [[ -z "$HOST" || -z "$PORT" || -z "$CMD" ]]; then
    print_usage
    exit 1
fi

echo "Aguardando $HOST:$PORT (timeout = $TIMEOUT s)..."

# Loop de espera
for ((i=0;i<TIMEOUT;i++)); do
    nc -z "$HOST" "$PORT" && break
    sleep 1
done

# Última verificação
if ! nc -z "$HOST" "$PORT"; then
    echo "Erro: $HOST:$PORT não disponível após $TIMEOUT segundos."
    exit 1
fi

echo "$HOST:$PORT está disponível. Executando comando..."
exec $CMD

