import re

from openfermion import FermionOperator


def get_operator_pool(system: str) -> list[FermionOperator]:
    with open(f'DISCO_data/{system}/operator_pool.txt') as file:
        raw_text = file.read()

    # extract slice of text containing operators
    pattern = r"Generating operator matrices\.\.\.(.*?)Operator matrices saved to 'opmat'"
    match = re.search(pattern, raw_text, re.DOTALL)
    extracted_text = '\n'.join(match.group(1).strip().splitlines()[:-1])

    # extract operator strings
    extracted_operators = re.split(r'Operator\s+\d+:', extracted_text)[1:]
    return [FermionOperator(op.strip()) for op in extracted_operators]
