# Ordenador Inteligente

Projeto academico da disciplina de Estrutura de Dados.

O objetivo e implementar seis algoritmos de ordenacao e investigar, por meio de
experimentos reproduziveis, quando uma escolha automatica de algoritmo compensa
em relacao a usar um unico metodo fixo.

## Requisitos

- Python 3.10 ou superior (desenvolvido e testado com Python 3.12.10)
- Git (opcional, para versionamento)

## Preparando o ambiente

Criar o ambiente virtual:

```powershell
python -m venv .venv
```

Ativar o ambiente:

```powershell
.\.venv\Scripts\Activate.ps1
```

Instalar as dependencias:

```powershell
python -m pip install -r requirements.txt
```

> Alternativa sem ativar o ambiente: use `.\.venv\Scripts\python` no lugar de `python`.

## Executando os testes

```powershell
python -m pytest -v
```

## Estrutura

```
ordenador/        codigo-fonte do projeto
  algoritmos/     um modulo por metodo de ordenacao
testes/           testes automatizados (pytest)
```

As pastas de experimentos e os arquivos de relatorio serao criados quando
chegarem as etapas correspondentes.
