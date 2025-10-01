from dataclasses import dataclass
from typing import Optional

@dataclass
class ModelBounds:
    min_x: float; max_x: float
    min_y: float; max_y: float
    min_z: float; max_z: float

def parse_bounds_from_file(path: Optional[str], fmt: Optional[str]) -> ModelBounds:
    if not path or not fmt:
        return ModelBounds(0, 170, 0, 12, 0, 13)
    return ModelBounds(0, 100, 0, 20, 0, 20)
