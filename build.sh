echo "Acesse Criar Chave de Acesso no IMA para prover a chave de acesso e a chave de acesso secreta"
aws configure
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 752927261281.dkr.ecr.us-east-1.amazonaws.com
docker build -t unicatech .
docker tag unicatech:latest 752927261281.dkr.ecr.us-east-1.amazonaws.com/unicatech:latest
docker push 752927261281.dkr.ecr.us-east-1.amazonaws.com/unicatech:latest
