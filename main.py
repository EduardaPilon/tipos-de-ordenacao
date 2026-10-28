from ordenador.selecao import analisar, escolher
from ordenador.ordenar import ordenar
import re


# Nomes mais bonitos para mostrar pro usuário
NOMES_PT = {
    "insercao": "Inserção (Insertion Sort)",
    "intercalacao": "Intercalação (Merge Sort)",
    "rapida": "Rápida (Quick Sort com pivô aleatório)",
    "contagem": "Contagem (Counting Sort)",
    "base": "Base (Radix Sort - LSD)",
    "hibrido": "Híbrido (Merge + Inserção)",
}


def converter_numeros(texto: str) -> list:
    """Converte texto digitado pelo usuário em lista de números."""
    if not texto.strip():
        return []

    # Substitui vírgulas por espaços
    texto = texto.replace(",", " ")
    texto = texto.replace(";", " ")

    # Pega todos os números (inteiros ou negativos)
    encontrados = re.findall(r"[-+]?\d+(?:\.\d+)?", texto)

    if not encontrados:
        # Tenta separar por espaços mesmo sem regex
        encontrados = texto.split()

    lista = []
    for s in encontrados:
        s = s.strip()
        if s == "":
            continue
        try:
            # Se não tiver ponto, converte pra int
            if "." not in s:
                lista.append(int(s))
            else:
                val = float(s)
                # Mantém como inteiro se for valor exato
                if val.is_integer():
                    lista.append(int(val))
                else:
                    lista.append(val)
        except ValueError:
            pass

    return lista


def main():
    print("=" * 50)
    print("           ORDENADOR INTELIGENTE")
    print("=" * 50)
    print()
    print("Digite uma sequência de números separados por espaço ou vírgula.")
    print("Exemplo: 10 5 20 3 15 ou 10, 5, 20, 3, 15")
    print()

    try:
        entrada = input("Sua sequência: ").strip()

        if not entrada:
            print("\n[ERRO] Você não digitou nada.")
            return

        dados = converter_numeros(entrada)

        if len(dados) == 0:
            print("\n[ERRO] Não consegui identificar nenhum número válido.")
            print("Tente novamente usando apenas números, espaços ou vírgulas.")
            return

        # Faz uma cópia para exibir a original
        dados_originais = list(dados)

        print("\n" + "-" * 50)
        print("ANÁLISE DA SEQUÊNCIA")
        print("-" * 50)
        print(f"Lista digitada: {dados_originais}")
        print(f"Quantidade de elementos: {len(dados_originais)}")

        # Análise feita pelo programa
        perfil = analisar(dados_originais)
        print(f"\nDescidas adjacentes: {perfil.descidas}")
        print(f"Todos os elementos são inteiros: {perfil.todos_inteiros}")
        if perfil.amplitude is not None:
            print(f"Amplitude (máx - mín + 1): {perfil.amplitude}")
        print(f"Mínimo: {perfil.minimo} | Máximo: {perfil.maximo}")

        # Escolha do algoritmo
        algoritmo = escolher(dados_originais)
        print("\n" + "-" * 50)
        print("DECISÃO DO PROGRAMA")
        print("-" * 50)
        print(f"Algoritmo mais adequado: {algoritmo}")
        print(f"Nome completo: {NOMES_PT.get(algoritmo, algoritmo)}")

        # Ordenação
        ordenada = ordenar(dados_originais)
        print("\n" + "-" * 50)
        print("RESULTADO")
        print("-" * 50)
        print(f"Lista original:  {dados_originais}")
        print(f"Lista ordenada:  {ordenada}")
        print("\n" + "=" * 50)
        print("Execução finalizada com sucesso!")
        print("=" * 50)

    except EOFError:
        print("\nPrograma encerrado.")
    except KeyboardInterrupt:
        print("\n\nPrograma interrompido pelo usuário.")
    except Exception as e:
        print(f"\n[ERRO] Ocorreu um problema: {e}")
        print("Verifique se digitou a sequência corretamente.")


if __name__ == "__main__":
    main()
