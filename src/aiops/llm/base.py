from typing import List, Dict, Any
class LLMClient:
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        raise NotImplementedError
