"""Testes de fumaca do ambiente.

Um teste de fumaca ("smoke test") responde a uma pergunta basica:
"o ambiente minimo esta de pe?". Ele nao valida regras do projeto;
serve para nao comecarmos a implementar algoritmos em um ambiente quebrado.
"""

import sys

import pytest

import ordenador


def test_versao_minima_do_python():
    assert sys.version_info >= (3, 10), (
        f"Python 3.10+ e necessario; versao atual: {sys.version}"
    )


def test_pytest_disponivel():
    assert pytest.__version__


def test_pacote_ordenador_importavel():
    assert ordenador.__version__ == "0.1.0"
