# Compiler Edu Tool — Compilador Educacional de Mini-Python

## 1. Objetivo do Projeto
Ferramenta educacional desenvolvida para auxiliar estudantes no aprendizado de conceitos de compilação de linguagens de programação, utilizando o subconjunto **Mini-Python**.

## 2. Linguagem e Subconjunto Escolhido
* **Linguagem-alvo:** Subconjunto da linguagem Python (Mini-Python).
* **Construções Suportadas:**
  * Declaração de variáveis e atribuições (`=`).
  * Operações aritméticas e de comparação (`+`, `-`, `*`, `/`, `==`, `!=`, `<`, `>`).
  * Estruturas condicionais (`if`, `else`).
  * Chamadas de função nativa (`print()`).
  * Definição de funções simples (`def`).

## 3. Tecnologias Utilizadas
* **Backend:** Python 3.10+, FastAPI, Pytest (testes automatizados).
* **Frontend:** React, HTML5, CSS3.
* **Orquestração e Execução:** Docker, Docker Compose.

## 4. Instruções de Execução com Docker Compose
Para iniciar toda a aplicação:
```bash
docker compose up --build -d