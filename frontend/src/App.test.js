
import React from "react";

import {
  render,
  screen,
  fireEvent
} from "@testing-library/react";

import App from "./App";

beforeEach(() => {
  global.fetch = jest.fn();
});

function respostaApi(dados) {
  return {
    ok: true,
    json: async () => dados
  };
}

const resultadoValido = {
  message: "Análise léxica e sintática concluída com sucesso.",
  recebido: true,
  success: true,
  sucesso: true,
  sucesso_lexico: true,
  sucesso_sintatico: true,
  sintatico_executado: true,

  tokens: [
    {
      tipo: "IDENTIFICADOR",
      lexema: "x",
      linha: 1,
      coluna: 1
    },
    {
      tipo: "OPERADOR",
      lexema: "=",
      linha: 1,
      coluna: 3
    },
    {
      tipo: "LITERAL_INTEIRO",
      lexema: "10",
      linha: 1,
      coluna: 5
    }
  ],

  tokens_parser: [
    {
      tipo: "IDENTIFICADOR",
      lexema: "x",
      linha: 1,
      coluna: 1
    },
    {
      tipo: "OPERADOR",
      lexema: "=",
      linha: 1,
      coluna: 3
    },
    {
      tipo: "LITERAL_INTEIRO",
      lexema: "10",
      linha: 1,
      coluna: 5
    },
    {
      tipo: "NOVA_LINHA",
      lexema: "\n",
      linha: 1,
      coluna: 7
    }
  ],

  erros: [],
  erros_lexicos: [],
  erros_sintaticos: [],

  ast: {
    tipo: "Programa",
    corpo: [
      {
        tipo: "Atribuicao",
        identificador: "x",
        valor: {
          tipo: "Literal",
          valor: "10",
          tipo_valor: "numero",
          posicao: {
            linha: 1,
            coluna: 5
          }
        },
        posicao: {
          linha: 1,
          coluna: 1
        }
      }
    ]
  }
};


test("exibe o editor e o botão de análise", () => {
  render(<App />);

  expect(
    screen.getByLabelText(/Código-fonte/i)
  ).toBeInTheDocument();

  expect(
    screen.getByLabelText(/Selecionar exemplo/i)
  ).toBeInTheDocument();

  expect(
    screen.getByRole("button", {
      name: /Analisar código/i
    })
  ).toBeInTheDocument();
});


test("selecionar exemplo preenche o editor", () => {
  render(<App />);

  fireEvent.change(
    screen.getByLabelText(/Selecionar exemplo/i),
    {
      target: {
        value: "2"
      }
    }
  );

  expect(
    screen.getByLabelText(/Código-fonte/i).value
  ).toContain("resultado = x + y * 2");
});


test("entrada vazia mostra mensagem de validação", () => {
  render(<App />);

  fireEvent.change(
    screen.getByLabelText(/Código-fonte/i),
    {
      target: {
        value: "   "
      }
    }
  );

  fireEvent.click(
    screen.getByRole("button", {
      name: /Analisar código/i
    })
  );

  expect(
    screen.getByRole("alert")
  ).toHaveTextContent(
    /Informe um código-fonte/i
  );

  expect(global.fetch).not.toHaveBeenCalled();
});


test("envia o código para o endpoint de análise", async () => {
  global.fetch.mockResolvedValue(
    respostaApi(resultadoValido)
  );

  render(<App />);

  fireEvent.click(
    screen.getByRole("button", {
      name: /Analisar código/i
    })
  );

  await screen.findByText("Atribuicao");

  expect(global.fetch).toHaveBeenCalledWith(
    "/api/parse",
    expect.objectContaining({
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      }
    })
  );
});


test("exibe tokens léxicos e tokens estruturais", async () => {
  global.fetch.mockResolvedValue(
    respostaApi(resultadoValido)
  );

  render(<App />);

  fireEvent.click(
    screen.getByRole("button", {
      name: /Analisar código/i
    })
  );

  await screen.findByText("Atribuicao");

  fireEvent.click(
    screen.getByRole("button", {
      name: /Tokens/i
    })
  );

  expect(
    screen.getByText("IDENTIFICADOR")
  ).toBeInTheDocument();

  expect(
    screen.getByText("LITERAL_INTEIRO")
  ).toBeInTheDocument();

  expect(
    screen.getByText("NOVA_LINHA")
  ).toBeInTheDocument();

  expect(
    screen.getByText("↵")
  ).toBeInTheDocument();
});


test("exibe a AST e permite selecionar um nó", async () => {
  global.fetch.mockResolvedValue(
    respostaApi(resultadoValido)
  );

  render(<App />);

  fireEvent.click(
    screen.getByRole("button", {
      name: /Analisar código/i
    })
  );

  expect(
    await screen.findByText("Atribuicao")
  ).toBeInTheDocument();

  // Seleciona especificamente o botão do nó AST,
  // evitando o botão de expandir/recolher.
  fireEvent.click(
    screen.getByRole("button", {
      name: /Atribuicao.*Variável: x/
    })
  );

  expect(
    screen.getByText("Nó selecionado")
  ).toBeInTheDocument();

  expect(
    screen.getByText("Regra gramatical relacionada:")
  ).toBeInTheDocument();

  expect(
    screen.getByText(/atribuicao.*IDENTIFICADOR/i)
  ).toBeInTheDocument();

  expect(
    screen.getByText("Linha 1, coluna 1")
  ).toBeInTheDocument();
});


test("permite expandir e recolher a árvore AST", async () => {
  global.fetch.mockResolvedValue(
    respostaApi(resultadoValido)
  );

  render(<App />);

  fireEvent.click(
    screen.getByRole("button", {
      name: /Analisar código/i
    })
  );

  await screen.findByText("Atribuicao");

  fireEvent.click(
    screen.getByRole("button", {
      name: /Recolher tudo/i
    })
  );

  expect(
    screen.getByRole("button", {
      name: /Expandir Programa/i
    })
  ).toBeInTheDocument();

  fireEvent.click(
    screen.getByRole("button", {
      name: /Expandir tudo/i
    })
  );

  expect(
    screen.getByText("Atribuicao")
  ).toBeInTheDocument();
});


test("exibe erro sintático com linha e coluna", async () => {
  const resultadoComErro = {
    ...resultadoValido,
    message: "Foram encontrados erros sintáticos.",
    success: false,
    sucesso: false,
    sucesso_sintatico: false,
    ast: null,
    erros: [
      {
        tipo: "ERRO_SINTATICO",
        mensagem: "Expressão incompleta.",
        linha: 1,
        coluna: 12,
        encontrado: "\n",
        esperado: "número ou identificador"
      }
    ],
    erros_sintaticos: [
      {
        tipo: "ERRO_SINTATICO",
        mensagem: "Expressão incompleta.",
        linha: 1,
        coluna: 12,
        encontrado: "\n",
        esperado: "número ou identificador"
      }
    ]
  };

  global.fetch.mockResolvedValue(
    respostaApi(resultadoComErro)
  );

  render(<App />);

  fireEvent.click(
    screen.getByRole("button", {
      name: /Analisar código/i
    })
  );

  expect(
    await screen.findByText("Expressão incompleta.")
  ).toBeInTheDocument();

  expect(
    screen.getByText(/Linha 1, coluna 12/i)
  ).toBeInTheDocument();

  expect(
    screen.getByText(/Esperado:/i)
  ).toBeInTheDocument();
});


test("diferencia erro léxico de erro sintático", async () => {
  const resultadoLexico = {
    message: "A análise sintática não foi executada.",
    sucesso: false,
    success: false,
    sucesso_lexico: false,
    sucesso_sintatico: false,
    sintatico_executado: false,
    tokens: [],
    tokens_parser: [],
    erros: [
      {
        tipo: "ERRO_LEXICO",
        lexema: "@",
        linha: 1,
        coluna: 5,
        mensagem: "Caractere não reconhecido: '@'."
      }
    ],
    erros_lexicos: [
      {
        tipo: "ERRO_LEXICO",
        lexema: "@",
        linha: 1,
        coluna: 5,
        mensagem: "Caractere não reconhecido: '@'."
      }
    ],
    erros_sintaticos: [],
    ast: null
  };

  global.fetch.mockResolvedValue(
    respostaApi(resultadoLexico)
  );

  render(<App />);

  fireEvent.click(
    screen.getByRole("button", {
      name: /Analisar código/i
    })
  );

  expect(
    await screen.findByText(
      "Caractere não reconhecido: '@'."
    )
  ).toBeInTheDocument();

  expect(
    screen.getByText(/Análise sintática:/i)
  ).toBeInTheDocument();

  expect(
    screen.getByText("NÃO EXECUTADA")
  ).toBeInTheDocument();
});


test("informa falha de comunicação com o backend", async () => {
  global.fetch.mockRejectedValue(
    new Error("Falha de comunicação.")
  );

  render(<App />);

  fireEvent.click(
    screen.getByRole("button", {
      name: /Analisar código/i
    })
  );

  expect(
    await screen.findByRole("alert")
  ).toHaveTextContent(
    "Falha de comunicação."
  );
});
