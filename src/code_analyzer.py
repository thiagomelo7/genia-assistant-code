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
    
    # OBSERVAÇÃO: As funções de cálculo de CC local (radon) foram removidas,
    # pois a LLM está realizando o cálculo.

    def refatorar_e_analisar(self, codigo_original: str, linguagem: str) -> dict:
        """Coordena o pipeline de refatoração, análise e métricas."""

        # 1. Geração do Código Refatorado (Primeira chamada LLM)
        codigo_refatorado = self.llm_service.get_refactored_code(codigo_original, linguagem)
        
        # 2. Análise, Justificativa e CÁLCULO DE CC (Segunda chamada LLM)
        analysis_data = self.llm_service.get_analysis_json(codigo_original, codigo_refatorado, linguagem)

        # 3. Leitura e Validação das Métricas Calculadas pela LLM
        cc_original = 1
        cc_refatorado = 1
        
        try:
            # AQUI: Lemos os valores diretamente do JSON, convertendo para int
            cc_original = int(analysis_data.get('cc_original_llm', 1))
            cc_refatorado = int(analysis_data.get('cc_refatorado_llm', 1))
        except (TypeError, ValueError):
            # Se a LLM falhar em dar um número (ex: retorna "oito" ou null), usamos fallback.
            analysis_data['justificativa_refatoracao'] += " [AVISO: A LLM falhou ao retornar valores numéricos de CC e usou o fallback CC=1.]"
            cc_original = 1 
            cc_refatorado = 1
            
        # 4. Cálculo da Melhora (Fórmula Matemática)
        melhora_percentual = self._calcular_melhora_cc(cc_original, cc_refatorado)

        # 5. Consolidação do Relatório
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