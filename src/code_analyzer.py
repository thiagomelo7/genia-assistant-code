from .llm_service import LLMService

class CodeAnalyzer:
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def _calcular_melhora_cc(self, cc_original: int, cc_refatorado: int) -> float:
        """Calcula a melhora percentual na Complexidade Ciclomática (CC)."""
        if cc_original <= 0:
            return 0.0
        melhora = (1 - (cc_refatorado / cc_original)) * 100
        return max(0.0, melhora) 
    
    def _calcular_cc_simulado(self, codigo: str) -> int:
        """
        Calcula a Complexidade Ciclomática SIMULADA (count lines).
        
        PARA O PROJETO FINAL: Substituir esta função pelo uso de uma biblioteca
        como 'radon' ou 'Lizard' para cálculo real.
        """
        return len(codigo.splitlines())

    def refatorar_e_analisar(self, codigo_original: str, linguagem: str) -> dict:
        """Coordena o pipeline de refatoração, análise e métricas."""

        # 1. Geração do Código Refatorado (Primeira chamada LLM)
        codigo_refatorado = self.llm_service.get_refactored_code(codigo_original, linguagem)
        
        # 2. Análise e Justificativa (Segunda chamada LLM)
        analysis_data = self.llm_service.get_analysis_json(codigo_original, codigo_refatorado, linguagem)

        # 3. Cálculo de Métricas
        cc_original = self._calcular_cc_simulado(codigo_original)
        cc_refatorado = self._calcular_cc_simulado(codigo_refatorado)
        melhora_percentual = self._calcular_melhora_cc(cc_original, cc_refatorado)

        # 4. Consolidação do Relatório
        relatorio = {
            "linguagem": linguagem,
            "code_smells": analysis_data.get('code_smells', 'N/A'),
            "codigo_refatorado": codigo_refatorado,
            "justificativa_refatoracao": analysis_data.get('justificativa_refatoracao', 'N/A'),
            "complexidade": {
                "original": cc_original,
                "refatorada": cc_refatorado,
                "melhora_percentual": f"{melhora_percentual:.2f}%"
            }
        }
        return relatorio