
import React from 'react';
import {
  render,
  screen,
  fireEvent
} from '@testing-library/react';

import App from './App';

beforeEach(() => {
  global.fetch = jest.fn();
});

test('exibe o editor e o botão de análise', () => {
  render(<App />);

  expect(
    screen.getByLabelText(/Código-fonte/i)
  ).toBeInTheDocument();

  expect(
    screen.getByLabelText(/Selecionar exemplo/i)
  ).toBeInTheDocument();

  expect(
    screen.getByRole('button', {
      name: /Analisar código/i
    })
  ).toBeInTheDocument();
});

test('selecionar exemplo preenche o editor', () => {
  render(<App />);

  fireEvent.change(
    screen.getByLabelText(/Selecionar exemplo/i),
    { target: { value: '2' } }
  );

  expect(
    screen.getByLabelText(/Código-fonte/i).value
  ).toContain('resultado = a + b * 2');
});

test('entrada vazia mostra mensagem de validação', async () => {
  render(<App />);

  fireEvent.change(
    screen.getByLabelText(/Código-fonte/i),
    { target: { value: '   ' } }
  );

  fireEvent.click(
    screen.getByRole('button', {
      name: /Analisar código/i
    })
  );

  expect(
    await screen.findByText(/Informe um código-fonte/i)
  ).toBeInTheDocument();

  expect(global.fetch).not.toHaveBeenCalled();
});

test('exibe tokens retornados pelo backend', async () => {
  global.fetch.mockResolvedValue({
    ok: true,
    json: async () => ({
      sucesso: true,
      mensagem: 'Análise léxica concluída.',
      observacao: 'Somente léxica.',
      tokens: [
        {
          tipo: 'IDENTIFICADOR',
          lexema: 'x',
          linha: 1,
          coluna: 1
        }
      ],
      erros: [],
      resumo: {
        total_tokens: 1,
        total_erros: 0
      }
    })
  });

  render(<App />);

  fireEvent.click(
    screen.getByRole('button', {
      name: /Analisar código/i
    })
  );

  expect(
    await screen.findByText('IDENTIFICADOR')
  ).toBeInTheDocument();

  expect(screen.getByText('x')).toBeInTheDocument();
});
