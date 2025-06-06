# -*- coding: utf-8 -*-

#Importando as bibliotecas

import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import re
from datetime import datetime
import plotly.express as px

# Analise do ativo individualmente#

# Solicitando o ticker do ativo e verificando se está correto:

while True:

  ativo_ind = (input('Qual ativo você deseja verificar? ')).upper()
  ativo_nome = ativo_ind

  if not re.fullmatch(r'[A-Z]{1,4}([0-9]{1,2})?', ativo_ind):
    print('Digite um ativo válido (ex: PETR4, VALE3, AAPL)')
    continue

  if ativo_ind[-1].isdigit():
    ativo_ind += ".SA"

  print(f'\nAnalisando o ativo {ativo_ind}')

  try:

      ticker = yf.Ticker(ativo_ind)
      dados_ticker = ticker.history(period="5d")

      if not dados_ticker.empty:
          print(f"\nTicker '{ativo_ind}' encontrado com sucesso!")
          break
      else:
          print(f"\nO ticker '{ativo_ind}' não foi encontrado ou não possui dados recentes.")

  except Exception as e:
        print(f"Erro ao consultar o ativo: {e}")

# Solicitando o período desejado:

def ler_data(nome_periodo):
    hoje = datetime.today()

    while True:
        print(f"\nInforme a data {nome_periodo}:")
        try:
            ano = int(input("Ano (ex: 2025): "))
            if ano < 1000 or ano > 9999:
                raise ValueError("Ano inválido.")

            mes = int(input("Mês (1 a 12): "))
            if mes < 1 or mes > 12:
                raise ValueError("Mês deve estar entre 1 e 12.")

            dia = int(input("Dia (1 a 31): "))
            if dia < 1 or dia > 31:
                raise ValueError("Dia deve estar entre 1 e 31.")

            data = datetime(ano, mes, dia)  # Valida se a data existe (ex: 30/02 dá erro)

            if data > hoje:
              print("Data inválida. Revise a data e insira uma possível.")
              continue

            return data

        except ValueError as e:
            print(f"Erro: {e}. Tente novamente.")

# Leitura dos períodos

while True:
  data_inicial = ler_data("inicial")
  data_final = ler_data("final")

  if data_final <= data_inicial:
    print("\nA data final deve ser posterior à data inicial. Tente novamente.")
  else:
    break

# Pegando os dados do ticker:

ticker_data = pd.DataFrame()
ticker_data = yf.download(ativo_ind, start=data_inicial, end=data_final, auto_adjust=False)

#print(ticker_data)

# Gerando gráfico dos preços:

# Junta os níveis do MultiIndex em strings únicas
ticker_data.columns = [' - '.join(col) if isinstance(col, tuple) else col for col in ticker_data.columns]
ticker_data.columns = [col.replace(f" - {ativo_ind}", "") for col in ticker_data.columns]

# Gerando o gráfico interativo:

print('\n')
grafico_ativo = px.line(title=f"Histórico do Preço da Ação {ativo_nome}")
grafico_ativo.add_scatter(x=ticker_data.index, y=ticker_data["Adj Close"], name=ativo_nome)
grafico_ativo.show()

# Calcular a Taxa de retorno esperado de um ativo

print(f"\nPeríodo analisado: de {data_inicial.strftime('%d-%m-%Y')} até {data_final.strftime('%d-%m-%Y')}.")

ticker_data["Retorno Esperado"] = np.log(ticker_data["Adj Close"] / ticker_data["Adj Close"].shift(1))
retorno_esperado = ticker_data["Retorno Esperado"].mean() * 250
retorno_esperado_100 = (round(retorno_esperado * 100, 2))
print(f"\nTaxa média de retorno anual esperada da ação {ativo_nome}: {retorno_esperado_100}%")

# Calcular o desvio padrão de um ativo

desvio_padrao = ticker_data["Retorno Esperado"].std() * 250 ** 0.5
desvio_padrao_100 = (round(desvio_padrao * 100, 2))
print(f"Volatilidade (desvio padrão dos retornos) da {ativo_nome}: {desvio_padrao_100}%")

# Análise da volatilidade e classificação

print(f"\nCom base na volatilidade conseguimos classificar o ativo {ativo_nome} como:")

if desvio_padrao_100 <= 10:
  print(f"\n{ativo_nome} = Baixa volatilidade.")
elif desvio_padrao_100 > 10 and desvio_padrao_100 <= 30:
  print(f"\n{ativo_nome} = Média volatilidade.")
else:
  print(f"\n{ativo_nome} = Alta volatilidade.")

print(f"\nExplicação: A taxa média de retorno ({retorno_esperado_100}%) representa o quanto o ativo rendeu, em média, por ano no período analisado.\nJá o desvio padrão ({desvio_padrao_100}%), mede a variação dos retornos em torno dessa média, ou seja, o quanto os retornos oscilaram.")
print(f"O desvio padrão pode ser usado para estimar um intervalo de retornos possíveis. obtemos duas variações, normalmente a variação de valorização e a de desvalorização.\nEm alguns casos pode ocorrer em ambas as variações uma desvalorização.")

valorizacao = round(retorno_esperado_100 + desvio_padrao_100, 2)
desvalorizacao = round(retorno_esperado_100 - desvio_padrao_100, 2)

if valorizacao < 0:
  resultado_1 = "Menor Desvalorização possível"
else:
  resultado_1 = "Maior Valorização possível"

if desvalorizacao < 0:
  resultado_2 = "Maior Desvalorização possível"
else:
  resultado_2 = "Menor Valorização possível"

print(f"\n1° Possibilidade {resultado_1}:\n   {retorno_esperado_100}% + {desvio_padrao_100}% = {valorizacao}%")
print(f"\n2° Possibilidade {resultado_2}:\n   {retorno_esperado_100}% - {desvio_padrao_100}% = {desvalorizacao}%")

print(f"\nIsso significa que, com base no histórico, os retornos anuais do ativo tendem a variar entre {desvalorizacao}% e {valorizacao}% na maioria dos anos.")

if valorizacao < 0 and desvalorizacao < 0:
  print(f"\nEsse ativo teve uma forte perda de valor, e uma volatilidade extremamente alta, a ponto que até a melhor projeção não representa uma valorização.")
else:
  print(f"\nEsse ativo tem uma volatilidade coerente, portanto temos os dois dados: valorização e desvalorização.")

#Gráfico dos cenários possíveis

print('\n')
plt.figure(figsize=(15, 2))
plt.axvline(desvalorizacao, color='red', linestyle='--', label="Pior cenário")
plt.axvline(retorno_esperado_100, color='black', linestyle='-', label="Retorno esperado")
plt.axvline(valorizacao, color='green', linestyle='--', label="Melhor cenário")

plt.title(f"Intervalo de Retorno Esperado da Ação {ativo_nome}")
plt.xlabel("Retorno anual (%)")
plt.legend()
plt.grid(True)
plt.show()
