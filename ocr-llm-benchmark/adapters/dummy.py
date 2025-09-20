import time, json, random
from typing import Dict, Any
from adapters.base import BaseAdapter

class DummyAdapter(BaseAdapter):
    name = "Dummy"
    supports_images = False

    def infer(self, doc_bytes: bytes, prompt: str, **kwargs) -> Dict[str, Any]:
        start = time.perf_counter()
        # Simulate TTFT and generation
        ttft = random.uniform(0.05, 0.2)
        time.sleep(ttft)
        # Simulate token generation
        out_tokens = random.randint(60, 140)
        tpot = random.uniform(0.08, 0.2)  # sec per token (slow on purpose)
        gen_time = out_tokens * tpot
        time.sleep(min(gen_time, 2.0))  # don't actually wait full time

        total = (time.perf_counter() - start) * 1000.0
        return {
            "success": True,
            "output_json": {"tables": []},
            "output_text": None,
            "timings": {
                "ttft_ms": int(ttft*1000),
                "tpot_ms": int(tpot*1000),
                "gen_time_ms": int(gen_time*1000),
                "e2el_ms": int(total),
            },
            "tokens": {"input_tokens": 800, "output_tokens": out_tokens, "estimated": True},
            "image_input": None,
            "notes": "Dummy response for wiring & metrics."
        }
