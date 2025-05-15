from functools import partial
from collections import OrderedDict
from pathlib import Path

from diagrams import Diagram, Cluster, Node, Edge

PWD = Path(__file__).parent
FILE_NAME = PWD / '_static' / 'config_composition'

configuration_dict = OrderedDict(
    {
        'CLI': {'opt1': 'cli-opt-1'},
        'ENVIRONMENT': {'ENV_OPT1': 'env-opt-1', 'ENV_OPT2': 'env-opt-2'},
        'config_file.ini': {
            'opt1': 'file-opt-1',
            'opt2': 'file-opt-2',
            'opt3': 'file-opt-3',
        },
    }
)

nodes = {src: dict() for src in configuration_dict.keys()}

color_map = {
    'CLI': '#FF7F7F',
    'ENVIRONMENT': '#DFDF7F',
    'config_file.ini': '#7F7FFF',
}


def create_config_diagram():
    # Graph attributes
    graph_attr = {
        'pad': '0.75',
        'splines': 'ortho',
        'nodesep': '0.60',
        'ranksep': '0.75',
        'fontname': 'Sans-Serif',
        'fontsize': '13',
        'rankdir': 'LR',
    }

    opt_node = partial(
        Node,
        fontsize='12',
        height='1',
        style='filled',
    )

    value_node = partial(
        Node,
        fontsize='10',
        height='.25',
        style='filled',
        fillcolor='#FF7F7F',
    )

    # Create diagram with specified attributes
    with Diagram(
        'Runtime Configuration Composition',
        show=False,
        direction='LR',
        graph_attr=graph_attr,
        filename=FILE_NAME,
    ):
        # Create nodes for each configuration level
        with Cluster(
            'Configuration Sources',
            direction='LR',
        ):
            for source, config in configuration_dict.items():
                with Cluster(
                    source,
                    direction='TB',
                    graph_attr={
                        'style': 'filled',
                        'fillcolor': color_map[source],
                        'rank': 'same',  # Keep items in the same cluster at same level
                        'labeljust': 'l',
                        'rankdir': 'TB',
                    },
                ):
                    for k, v in config.items():
                        with Cluster(k, direction='LR'):
                            nodes[source][k] = value_node(
                                v, fillcolor=color_map[source]
                            )

        for source, nds in nodes.items():
            previous_node = None
            for k, v in nds.items():
                if previous_node:
                    previous_node - Edge(style='invis') - v
                previous_node = v

        with Cluster(
            'Runtime Configuration',
            direction='LR',
            graph_attr={
                'fillcolor': color_map[source],
                'rank': 'same',  # Keep items in the same cluster at same level
                'labeljust': 'l',
                'rankdir': 'LR',
            },
        ):
            with Cluster('opt1', direction='LR'):
                o1 = value_node(
                    configuration_dict['CLI']['opt1'],
                    fillcolor=color_map['CLI'],
                )
            with Cluster('opt2', direction='LR'):
                o2 = value_node(
                    configuration_dict['ENVIRONMENT']['ENV_OPT2'],
                    fillcolor=color_map['ENVIRONMENT'],
                )
            with Cluster('opt3', direction='LR'):
                o3 = value_node(
                    configuration_dict['config_file.ini']['opt3'],
                    fillcolor=color_map['config_file.ini'],
                )

        o1 - Edge(style='invis') - o2 - Edge(style='invis') - o3
