from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Tuple

class BaseAdapter(ABC):
    name: str = "Base"
    supports_images: bool = False
    max_image_res: Optional[Tuple[int, int]] = None  # (W,H) pixels if applicable

    @abstractmethod
    def infer(self, doc_bytes: bytes, prompt: str, **kwargs) -> Dict[str, Any]:
        """Return dict with keys:
        - success: bool
        - output_json: Optional[dict]
        - output_text: Optional[str]
        - timings: {ttft_ms, tpot_ms, gen_time_ms, e2el_ms}
        - tokens: {input_tokens, output_tokens, estimated: bool}
        - image_input: {pixels: (w,h)} or None
        - notes: str
        """
        raise NotImplementedError
