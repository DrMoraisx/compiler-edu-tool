# 🛠️ Compiler Edu Tool - Ferramenta Educacional de Compiladores

Software educacional desenvolvido para a disciplina de compiladores. O objetivo deste projeto é implementar de forma didática as fases de um compilador (começando pela análise léxica), utilizando uma arquitetura moderna baseada em microrserviços web.

## 🎯 1. Escolha da Linguagem e Subconjunto

* **Linguagem Escolhida:** **Mini-Python (Subconjunto Educacional)**
* **Justificativa:** A escolha de uma variação simplificada de Python permite focar nos conceitos fundamentais de análise léxica e sintática (como reconhecimento de palavras-chave, identificadores, literais e operadores) sem a complexidade de construções avançadas da linguagem completa.
* **Subconjunto Inicial (Etapa 1):**
  * Atribuição de variáveis (`=`)
  * Operadores aritméticos básicos (`+`, `-`, `*`, `/`)
  * Identificadores e números inteiros/reais
  * Comentários de linha (`#`)

---

## 🏗️ 2. Arquitetura do Projeto

O projeto está dividido em dois componentes principais orquestrados via Docker Compose:
* **Backend:** Desenvolvido em **Python (FastAPI)** na porta `8000`, responsável pelas regras de processamento e futuros algoritmos do compilador.
* **Frontend:** Desenvolvido em **React (Node.js)** na porta `3000`, responsável pela interface gráfica do utilizador.

---

## 🚀 3. Pré-requisitos

Para executar este projeto na sua máquina, certifique-se de ter instalado:
* [Docker Desktop](https://www.docker.com/products/docker-desktop/) (com suporte ao WSL2 no Windows)
* [Docker Compose](https://docs.docker.com/compose/) (geralmente já incluso no Docker Desktop)

---

## ⚙️ 4. Como Executar o Projeto (Inicialização)

1. Clone o repositório para a sua máquina local:
   ```bash
   git clone [https://github.com/DrMoraisx/compiler-edu-tool.git](https://github.com/DrMoraisx/compiler-edu-tool.git)
   cd compiler-edu-tool