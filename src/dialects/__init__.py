from .msa import MSAProcessor
from .egyptian import EgyptianProcessor
from .gulf import GulfProcessor
from .levantine import LevantineProcessor
from .maghreb import MaghrebProcessor

def get_dialect_processor(dialect: str):
    processors = {
        "MSA": MSAProcessor,
        "EG": EgyptianProcessor,
        "Gulf": GulfProcessor,
        "Levantine": LevantineProcessor,
        "Maghreb": MaghrebProcessor
    }
    return processors.get(dialect, MSAProcessor)()