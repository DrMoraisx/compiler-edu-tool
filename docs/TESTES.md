
# Registro de testes e validação

Este documento registra a execução dos testes do Compiler Edu Tool.

## 1. Testes do backend

Comando:

```bash
cd backend
python -m pip install -r requirements.txt
python -m pytest -q
```

Os testes verificam:
- Palavras reservadas e identificadores.
- Números inteiros e reais.
- Strings.
- Operadores e delimitadores.
- Comentários e espaços em branco.
- Posição dos tokens.
- Caracteres inválidos.
- Strings não terminadas.
- Endpoints da API.
- Entradas vazias e requisições inválidas.

Data da execução:
Resultado apresentado:
Falhas encontradas:
Correções realizadas:

## 2. Testes do frontend

Comandos:

```bash
cd frontend
npm install
npm test
```

Os testes verificam:
- Presença do editor.
- Seleção dos exemplos.
- Validação de entrada vazia.
- Exibição dos tokens recebidos da API.

Data da execução:
Resultado apresentado:
Falhas encontradas:
Correções realizadas:

## 3. Docker Compose

Comandos:

```bash
docker compose config
docker compose up --build -d
docker compose ps
curl http://localhost:8000/api/health
docker compose logs --tail=100
docker compose down
```

Os testes verificam a configuração e a inicialização dos serviços,
a resposta da API e o encerramento dos contêineres.

Data da execução:
Os serviços iniciaram corretamente?
A interface abriu no navegador?
A API respondeu?
A análise léxica funcionou?
Falhas encontradas:
Correções realizadas:

## 4. Instalação limpa

1. Obter uma cópia limpa do repositório.
2. Seguir as instruções do README.
3. Construir e iniciar os contêineres.
4. Testar a interface e a comunicação com o backend.
5. Executar os testes automatizados.
6. Registrar os resultados reais e as pendências.

Resultado da validação:
Pendências:
