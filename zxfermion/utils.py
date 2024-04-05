def pair_list(items: list[int]) -> list[tuple[int, int]]:
    return [(items[idx], items[idx + 1]) for idx in range(len(items) - 1)]


class Settings(object):
    stack = False
    labels = True
    tikz_var = r'\pi'
    tikz_scale: float = 0.5
    tikz_classes: dict[str, str] = {
        'boundary': 'black',
        'x_node': 'x_node',
        'z_node': 'z_node',
        'x_phase': 'x_phase',
        'z_phase': 'z_phase',
        'hadamard': 'hadamard',
        'hadamard_edge': 'blue_dashed',
        'edge': '',
    }


settings = Settings()
