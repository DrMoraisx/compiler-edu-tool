
import React, { useMemo, useState } from "react";
import "./App.css";

const LIMITE_CODIGO = 20000;

const EXEMPLOS = {
  1: `numero = 10
resultado = numero
print(resultado)`,
  2: `x = 10
y = 5
resultado = x + y * 2
print(resultado)`,
  3: `idade = 20

if idade >= 18:
    print("Maior que 10")
else:
    print("Menor ou igual a 10")`,
  4: `resultado = (10 + 5) * 2
print(resultado)`
};

const REGRAS_GRAMATICAIS = {
  Programa: "programa → { nova_linha | declaracao }",
  Atribuicao: "atribuicao → IDENTIFICADOR '=' expressao",
  Print: "comando_print → 'print' '(' expressao ')'",
  Condicional: "condicional → 'if' expressao ':' bloco ['else' bloco]",
  ExpressaoBinaria: "expressao → soma { operador soma }",
  ExpressaoUnaria: "fator → '-' fator",
  Literal: "fator → LITERAL_INTEIRO | LITERAL_REAL | LITERAL_STRING",
  Identificador: "fator → IDENTIFICADOR"
};

function obterFilhos(no) {
  if (!no || typeof no !== "object") {
    return [];
  }

  const propriedadesIgnoradas = new Set([
    "tipo",
    "operador",
    "nome",
    "identificador",
    "tipo_valor",
    "posicao"
  ]);

  const filhos = [];

  Object.entries(no).forEach(([chave, valor]) => {
    if (propriedadesIgnoradas.has(chave)) {
      return;
    }

    if (Array.isArray(valor)) {
      valor.forEach((item, indice) => {
        if (item && typeof item === "object" && item.tipo) {
          filhos.push({
            chave,
            indice,
            no: item
          });
        }
      });

      return;
    }

    if (valor && typeof valor === "object" && valor.tipo) {
      filhos.push({
        chave,
        indice: 0,
        no: valor
      });
    }
  });

  return filhos;
}

function possuiCorrespondencia(no, filtro) {
  if (!filtro) {
    return true;
  }

  const tipo = String(no?.tipo || "").toLowerCase();

  if (tipo.includes(filtro.toLowerCase())) {
    return true;
  }

  return obterFilhos(no).some((filho) =>
    possuiCorrespondencia(filho.no, filtro)
  );
}

function coletarTipos(no, tipos = new Set()) {
  if (!no || typeof no !== "object") {
    return tipos;
  }

  if (no.tipo) {
    tipos.add(no.tipo);
  }

  obterFilhos(no).forEach((filho) => {
    coletarTipos(filho.no, tipos);
  });

  return tipos;
}

function rotuloDoNo(no) {
  const partes = [no.tipo || "Nó"];

  if (no.operador) {
    partes.push(`Operador: ${no.operador}`);
  }

  if (no.nome) {
    partes.push(`Nome: ${no.nome}`);
  }

  if (no.identificador) {
    partes.push(`Variável: ${no.identificador}`);
  }

  if (
    no.valor !== undefined &&
    no.valor !== null &&
    typeof no.valor !== "object"
  ) {
    partes.push(`Valor: ${no.valor}`);
  }

  if (no.tipo_valor) {
    partes.push(`Categoria: ${no.tipo_valor}`);
  }

  return partes.join(" | ");
}

function ArvoreAST({
  no,
  caminho,
  expanded,
  setExpanded,
  filtro,
  selecionarNo,
  selecionado
}) {
  if (!no || typeof no !== "object") {
    return null;
  }

  const filhos = obterFilhos(no);
  const aberto = expanded === null
    ? true
    : Boolean(expanded[caminho]);

  if (!possuiCorrespondencia(no, filtro)) {
    return null;
  }

  const estaSelecionado = selecionado === no;

  const alternar = () => {
    setExpanded((estadoAtual) => {
      const novoEstado = estadoAtual === null
        ? {}
        : { ...estadoAtual };

      novoEstado[caminho] = !aberto;

      return novoEstado;
    });
  };

  return (
    <div className="ast-node" data-node-type={no.tipo}>
      <div
        className={`ast-row ${estaSelecionado ? "ast-selected" : ""}`}
      >
        {filhos.length > 0 && (
          <button
            type="button"
            className="ast-toggle"
            aria-label={
              `${aberto ? "Recolher" : "Expandir"} ${no.tipo}`
            }
            onClick={alternar}
          >
            {aberto ? "−" : "+"}
          </button>
        )}

        <button
          type="button"
          className="ast-select"
          onClick={() => selecionarNo(no)}
        >
          <strong>{no.tipo}</strong>

          {no.operador && (
            <span>Operador: {no.operador}</span>
          )}

          {no.nome && (
            <span>Nome: {no.nome}</span>
          )}

          {no.identificador && (
            <span>Variável: {no.identificador}</span>
          )}

          {no.valor !== undefined &&
            no.valor !== null &&
            typeof no.valor !== "object" && (
              <span>Valor: {no.valor}</span>
            )}

          {no.tipo_valor && (
            <span>Categoria: {no.tipo_valor}</span>
          )}

          {no.posicao && (
            <small>
              Linha {no.posicao.linha},
              coluna {no.posicao.coluna}
            </small>
          )}
        </button>
      </div>

      {aberto && filhos.length > 0 && (
        <div className="ast-children">
          {filhos.map((filho) => (
            <div
              className="ast-child"
              key={`${caminho}-${filho.chave}-${filho.indice}`}
            >
              <small className="ast-property">
                {filho.chave}
                {Array.isArray(no[filho.chave])
                  ? ` [${filho.indice}]`
                  : ""}
              </small>

              <ArvoreAST
                no={filho.no}
                caminho={
                  `${caminho}.${filho.chave}.${filho.indice}`
                }
                expanded={expanded}
                setExpanded={setExpanded}
                filtro={filtro}
                selecionarNo={selecionarNo}
                selecionado={selecionado}
              />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function VisualizacaoCodigo({ codigo, linhaSelecionada }) {
  const linhas = String(codigo || "").split("\n");

  return (
    <div className="source-preview">
      {linhas.map((linha, indice) => {
        const numero = indice + 1;
        const selecionada = numero === linhaSelecionada;

        return (
          <div
            className={
              selecionada
                ? "source-line source-line-selected"
                : "source-line"
            }
            key={numero}
          >
            <span className="source-line-number">
              {numero}
            </span>
            <code>{linha || " "}</code>
          </div>
        );
      })}
    </div>
  );
}

function App() {
  const [code, setCode] = useState(EXEMPLOS[2]);
  const [resultado, setResultado] = useState(null);
  const [aba, setAba] = useState("ast");
  const [loading, setLoading] = useState(false);
  const [mensagem, setMensagem] = useState("");
  const [expanded, setExpanded] = useState(null);
  const [filtroNo, setFiltroNo] = useState("");
  const [noSelecionado, setNoSelecionado] = useState(null);

  const tiposAST = useMemo(() => {
    if (!resultado?.ast) {
      return [];
    }

    return Array.from(
      coletarTipos(resultado.ast)
    ).sort();
  }, [resultado]);

  const errosLexicos = resultado?.erros_lexicos || [];
  const errosSintaticos = resultado?.erros_sintaticos || [];

  const tokensExibidos = (
    resultado?.tokens_parser ||
    resultado?.tokens ||
    []
  );

  const totalErros = (
    errosLexicos.length + errosSintaticos.length
  );

  const analisarCodigo = async () => {
    if (!code.trim()) {
      setMensagem("Informe um código-fonte antes de analisar.");
      setResultado(null);
      return;
    }

    if (code.length > LIMITE_CODIGO) {
      setMensagem(
        `O código ultrapassa o limite de ${LIMITE_CODIGO} caracteres.`
      );
      return;
    }

    setMensagem("");
    setLoading(true);
    setNoSelecionado(null);
    setFiltroNo("");
    setExpanded(null);

    try {
      const resposta = await fetch("/api/parse", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ code })
      });

      const dados = await resposta.json();

      if (!resposta.ok) {
        throw new Error(
          dados.detail || "Não foi possível analisar o código."
        );
      }

      setResultado(dados);

      if (!dados.sucesso_lexico) {
        setAba("errors");
      } else if (!dados.sucesso_sintatico) {
        setAba("errors");
      } else {
        setAba("ast");
      }
    } catch (erro) {
      setResultado(null);
      setMensagem(
        erro.message ||
        "Não foi possível comunicar com o backend."
      );
    } finally {
      setLoading(false);
    }
  };

  const carregarExemplo = (evento) => {
    const valor = evento.target.value;

    if (EXEMPLOS[valor]) {
      setCode(EXEMPLOS[valor]);
      setResultado(null);
      setMensagem("");
      setNoSelecionado(null);
      setFiltroNo("");
      setExpanded(null);
    }
  };

  const exportarAST = () => {
    if (!resultado?.ast) {
      return;
    }

    const conteudo = JSON.stringify(
      resultado.ast,
      null,
      2
    );

    const arquivo = new Blob(
      [conteudo],
      { type: "application/json;charset=utf-8" }
    );

    const endereco = URL.createObjectURL(arquivo);
    const link = document.createElement("a");

    link.href = endereco;
    link.download = "ast-minipython.json";
    document.body.appendChild(link);
    link.click();
    link.remove();

    URL.revokeObjectURL(endereco);
  };

  const copiarJSON = async () => {
    if (!resultado?.ast) {
      return;
    }

    try {
      await navigator.clipboard.writeText(
        JSON.stringify(resultado.ast, null, 2)
      );

      setMensagem("AST copiada para a área de transferência.");
    } catch {
      setMensagem(
        "Não foi possível copiar. Utilize a aba JSON para visualizar."
      );
    }
  };

  const selecionarNo = (no) => {
    setNoSelecionado(no);
  };

  const linhaSelecionada = noSelecionado?.posicao?.linha || null;
  const colunaSelecionada = noSelecionado?.posicao?.coluna || null;

  return (
    <main className="compiler-container">
      <header className="compiler-header">
        <div className="logo-area">
          <div className="logo-icon" aria-hidden="true">
            {"</>"}
          </div>

          <div>
            <h1>EDUTER TOOL</h1>
            <span className="badge-lang">
              MINI-PYTHON COMPILER
            </span>
          </div>
        </div>

        <div className="header-info">
          Etapa 4 — Análise Sintática e AST
        </div>
      </header>

      <section className="intro">
        <h2>Ambiente de análise de código</h2>
        <p>
          Escreva um programa Mini-Python, execute a análise
          e acompanhe os tokens, a estrutura sintática e a AST.
        </p>
      </section>

      <section className="compiler-grid">
        <div className="editor-panel">
          <div className="panel-toolbar">
            <label htmlFor="code-editor">
              EDITOR DE CÓDIGO
            </label>

            <select
              aria-label="Selecionar exemplo"
              onChange={carregarExemplo}
              defaultValue=""
            >
              <option value="" disabled>
                Selecionar exemplo
              </option>
              <option value="1">
                Atribuições e saída
              </option>
              <option value="2">
                Operações aritméticas
              </option>
              <option value="3">
                Condicional if/else
              </option>
              <option value="4">
                Precedência e parênteses
              </option>
            </select>
          </div>

          <textarea
            id="code-editor"
            aria-label="Código-fonte"
            className="code-editor"
            value={code}
            onChange={(evento) => {
              setCode(evento.target.value);
              setResultado(null);
              setMensagem("");
              setNoSelecionado(null);
            }}
            spellCheck="false"
            placeholder="Digite seu código Mini-Python..."
            maxLength={LIMITE_CODIGO}
          />

          <div className="editor-footer">
            <span>
              {code.length} / {LIMITE_CODIGO} caracteres
            </span>

            <span>
              Linguagem: Mini-Python
            </span>
          </div>

          <div className="editor-actions">
            <button
              type="button"
              className="btn-analyze"
              onClick={analisarCodigo}
              disabled={loading}
            >
              {loading ? "ANALISANDO..." : "ANALISAR CÓDIGO"}
            </button>
          </div>

          {mensagem && (
            <div className="feedback-message" role="alert">
              {mensagem}
            </div>
          )}
        </div>

        <div className="result-card">
          <h2>RESULTADO DA ANÁLISE</h2>

          {!resultado && (
            <p className="empty-result">
              Execute uma análise para visualizar os tokens,
              a AST e os possíveis erros.
            </p>
          )}

          {resultado && (
            <>
              <div
                className={
                  totalErros === 0
                    ? "analysis-status status-success"
                    : "analysis-status status-error"
                }
                role="status"
              >
                <p>
                  Análise léxica:{" "}
                  <strong>
                    {resultado.sucesso_lexico
                      ? "SUCESSO"
                      : "ERRO"}
                  </strong>
                </p>

                <p>
                  Análise sintática:{" "}
                  <strong>
                    {resultado.sintatico_executado
                      ? (
                        resultado.sucesso_sintatico
                          ? "SUCESSO"
                          : "ERRO"
                      )
                      : "NÃO EXECUTADA"}
                  </strong>
                </p>

                <p>{resultado.message}</p>
              </div>

              <nav
                className="result-tabs"
                aria-label="Resultados da análise"
              >
                <button
                  type="button"
                  className={aba === "ast" ? "active" : ""}
                  onClick={() => setAba("ast")}
                >
                  Árvore AST
                </button>

                <button
                  type="button"
                  className={aba === "tokens" ? "active" : ""}
                  onClick={() => setAba("tokens")}
                >
                  Tokens ({tokensExibidos.length})
                </button>

                <button
                  type="button"
                  className={aba === "errors" ? "active" : ""}
                  onClick={() => setAba("errors")}
                >
                  Erros ({totalErros})
                </button>

                <button
                  type="button"
                  className={aba === "grammar" ? "active" : ""}
                  onClick={() => setAba("grammar")}
                >
                  Gramática
                </button>

                <button
                  type="button"
                  className={aba === "json" ? "active" : ""}
                  onClick={() => setAba("json")}
                >
                  JSON
                </button>
              </nav>

              <div className="result-content">
                {aba === "ast" && (
                  resultado.ast ? (
                    <section>
                      <div className="tree-toolbar">
                        <button
                          type="button"
                          onClick={() => setExpanded(null)}
                        >
                          Expandir tudo
                        </button>

                        <button
                          type="button"
                          onClick={() => setExpanded({})}
                        >
                          Recolher tudo
                        </button>

                        <button
                          type="button"
                          onClick={exportarAST}
                        >
                          Exportar AST JSON
                        </button>

                        <button
                          type="button"
                          onClick={copiarJSON}
                        >
                          Copiar AST
                        </button>
                      </div>

                      <label
                        className="filter-label"
                        htmlFor="filter-node"
                      >
                        Filtrar por tipo de nó
                      </label>

                      <input
                        id="filter-node"
                        className="node-filter"
                        type="text"
                        value={filtroNo}
                        onChange={(evento) =>
                          setFiltroNo(evento.target.value)
                        }
                        placeholder="Ex.: Atribuicao, Literal..."
                        list="ast-node-types"
                      />

                      <datalist id="ast-node-types">
                        {tiposAST.map((tipo) => (
                          <option key={tipo} value={tipo} />
                        ))}
                      </datalist>

                      <div className="ast-explanation">
                        A AST representa a estrutura reconhecida
                        pelo parser. Selecione um nó para consultar
                        sua posição e a regra gramatical relacionada.
                      </div>

                      <div className="ast-tree">
                        <ArvoreAST
                          no={resultado.ast}
                          caminho="raiz"
                          expanded={expanded}
                          setExpanded={setExpanded}
                          filtro={filtroNo}
                          selecionarNo={selecionarNo}
                          selecionado={noSelecionado}
                        />
                      </div>

                      {noSelecionado && (
                        <section className="selected-node-panel">
                          <h3>Nó selecionado</h3>

                          <p>
                            <strong>
                              {rotuloDoNo(noSelecionado)}
                            </strong>
                          </p>

                          <p>
                            Posição:{" "}
                            {linhaSelecionada
                              ? `linha ${linhaSelecionada}, coluna ${colunaSelecionada}`
                              : "não informada"}
                          </p>

                          <p>
                            Regra gramatical relacionada:
                          </p>

                          <code>
                            {REGRAS_GRAMATICAIS[
                              noSelecionado.tipo
                            ] || "Regra não especificada para este nó."}
                          </code>

                          {linhaSelecionada && (
                            <>
                              <h4>Trecho correspondente no código</h4>
                              <VisualizacaoCodigo
                                codigo={code}
                                linhaSelecionada={linhaSelecionada}
                              />
                            </>
                          )}
                        </section>
                      )}
                    </section>
                  ) : (
                    <p className="empty-result">
                      A AST não foi gerada porque a análise
                      sintática não foi concluída com sucesso.
                      Consulte a aba Erros.
                    </p>
                  )
                )}

                {aba === "tokens" && (
                  <div className="table-wrap">
                    <p className="muted">
                      Sequência completa produzida pelo scanner
                      e consumida pelo parser, incluindo tokens
                      estruturais de linha e indentação.
                    </p>

                    {tokensExibidos.length === 0 ? (
                      <p>Nenhum token disponível.</p>
                    ) : (
                      <table className="tokens-table">
                        <thead>
                          <tr>
                            <th>Tipo</th>
                            <th>Lexema</th>
                            <th>Linha</th>
                            <th>Coluna</th>
                          </tr>
                        </thead>

                        <tbody>
                          {tokensExibidos.map((token, indice) => (
                            <tr key={`${token.linha}-${token.coluna}-${indice}`}>
                              <td>
                                <span className="token-type">
                                  {token.tipo}
                                </span>
                              </td>
                              <td>
                                <code>
                                  {token.lexema === "\n"
                                    ? "↵"
                                    : token.lexema || "∅"}
                                </code>
                              </td>
                              <td>{token.linha}</td>
                              <td>{token.coluna}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    )}
                  </div>
                )}

                {aba === "errors" && (
                  <section>
                    <h3>Erros léxicos</h3>

                    {errosLexicos.length === 0 ? (
                      <p>Nenhum erro léxico encontrado.</p>
                    ) : (
                      errosLexicos.map((erro, indice) => (
                        <div
                          className="error-item"
                          key={`lexico-${indice}`}
                        >
                          <strong>{erro.mensagem}</strong>
                          <p>
                            Linha {erro.linha},
                            coluna {erro.coluna}
                          </p>
                          {erro.lexema && (
                            <p>Lexema: {erro.lexema}</p>
                          )}
                        </div>
                      ))
                    )}

                    <h3>Erros sintáticos</h3>

                    {errosSintaticos.length === 0 ? (
                      <p>Nenhum erro sintático encontrado.</p>
                    ) : (
                      errosSintaticos.map((erro, indice) => (
                        <div
                          className="error-item"
                          key={`sintatico-${indice}`}
                        >
                          <strong>{erro.mensagem}</strong>

                          <p>
                            Linha {erro.linha},
                            coluna {erro.coluna}
                          </p>

                          {erro.encontrado !== undefined && (
                            <p>
                              Encontrado: {String(erro.encontrado)}
                            </p>
                          )}

                          {erro.esperado !== undefined && (
                            <p>
                              Esperado: {
                                Array.isArray(erro.esperado)
                                  ? erro.esperado.join(", ")
                                  : String(erro.esperado)
                              }
                            </p>
                          )}
                        </div>
                      ))
                    )}
                  </section>
                )}

                {aba === "grammar" && (
                  <section className="grammar-panel">
                    <h3>Regras principais da gramática</h3>

                    <pre>
{`programa = { nova_linha | declaracao }

declaracao = atribuicao
           | comando_print
           | condicional

atribuicao = IDENTIFICADOR "=" expressao

comando_print = "print" "(" expressao ")"

condicional = "if" expressao ":" bloco
              [ "else" ":" bloco ]

expressao = soma { operador_comparacao soma }

soma = multiplicacao
       { ("+" | "-") multiplicacao }

multiplicacao = fator
                { ("*" | "/" | "%") fator }

fator = literal
      | IDENTIFICADOR
      | "-" fator
      | "(" expressao ")"`}
                    </pre>

                    <h3>Precedência</h3>
                    <ol>
                      <li>Parênteses e valores.</li>
                      <li>Negação unária.</li>
                      <li>Multiplicação, divisão e módulo.</li>
                      <li>Adição e subtração.</li>
                      <li>Comparações.</li>
                    </ol>

                    <p>
                      O projeto implementa um subconjunto didático
                      de Python. Laços, funções, declarações tipadas
                      e análise semântica ainda não fazem parte
                      desta versão.
                    </p>
                  </section>
                )}

                {aba === "json" && (
                  <section>
                    <div className="tree-toolbar">
                      <button
                        type="button"
                        onClick={copiarJSON}
                        disabled={!resultado.ast}
                      >
                        Copiar AST JSON
                      </button>

                      <button
                        type="button"
                        onClick={exportarAST}
                        disabled={!resultado.ast}
                      >
                        Exportar AST JSON
                      </button>
                    </div>

                    <pre className="json-preview">
                      {JSON.stringify(resultado, null, 2)}
                    </pre>
                  </section>
                )}
              </div>
            </>
          )}
        </div>
      </section>

      <footer>
        Compiler Edu Tool — Análise léxica e sintática educacional.
        A análise semântica será desenvolvida na Etapa 5.
      </footer>
    </main>
  );
}

export default App;
