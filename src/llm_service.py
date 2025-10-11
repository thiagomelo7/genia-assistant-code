import requests
import json
import re
import os

class LLMService:
    def __init__(self, api_endpoint, api_key):
        self.api_endpoint = api_endpoint
        self.api_key = api_key

    def _make_api_request(self, prompt: str) -> str:
        """Função privada para encapsular a comunicação com a LLM."""
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 4096
            }
        }

        if not self.api_key:
            raise ValueError("Chave de API não configurada. Verifique o arquivo .env.")

        try:
            response = requests.post(
                self.api_endpoint,
                headers=headers,
                data=json.dumps(payload),
                params={'key': self.api_key}
            )
            response.raise_for_status()
            analise_json = response.json()

            # Verificação de segurança: checa se há conteúdo válido
            if (analise_json.get('candidates') and
                analise_json['candidates'][0].get('content') and
                analise_json['candidates'][0]['content'].get('parts')):

                return analise_json['candidates'][0]['content']['parts'][0]['text']

            elif analise_json['candidates'][0].get('finishReason') == 'MAX_TOKENS':
                 raise RuntimeError("Geração interrompida: Limite de tokens atingido. O código refatorado é muito extenso. Tente um código de entrada menor.")

            elif analise_json.get('promptFeedback') or analise_json['candidates'][0].get('finishReason') == 'SAFETY':
                 feedback = analise_json['promptFeedback'].get('blockReason', 'N/A')
                 raise RuntimeError(f"Resposta bloqueada. Motivo: {feedback}")

            else:
                 raise RuntimeError(f"A API retornou uma resposta inesperada. JSON: {json.dumps(analise_json)}")

        except requests.exceptions.RequestException as e:
            status_code = response.status_code if 'response' in locals() else 'N/A'
            raise RuntimeError(f"Erro na requisição à API ({status_code}). {e}")
        except (KeyError, IndexError) as e:
            raise RuntimeError(f"Erro ao extrair texto da resposta da API (Estrutura incorreta após HTTP 200): {e}")

    def get_refactored_code(self, codigo_original: str, linguagem: str) -> str:
        """Gera APENAS o código refatorado (Primeira chamada)"""
        prompt = f"""
        Você é um assistente de código. Sua única tarefa é refatorar o seguinte código na linguagem {linguagem} para reduzir a complexidade e corrigir os Code Smells.
        Retorne APENAS o código refatorado completo, envolto em um bloco de código Markdown.
        ---
        {codigo_original}
        ---
        """
        return self._make_api_request(prompt).strip()

    def get_analysis_json(self, codigo_original: str, codigo_refatorado: str, linguagem: str) -> dict:
        """
        Gera o JSON de análise e justificativa, INCLUINDO o cálculo de CC.
        """
        analysis_prompt = f"""
        Analise o Código Original e o Código Refatorado, ambos na linguagem {linguagem}. 
        Para cada código, calcule a Complexidade Ciclomática (CC) contando os pontos de decisão (if, while, for, case, ?, &&, ||) e adicionando 1.

        Retorne APENAS um objeto JSON VÁLIDO e LIMPO.

        Código Original: ---{codigo_original}---
        Código Refatorado: ---{codigo_refatorado}---

        O JSON deve ter as chaves: 
        1. "code_smells" (string): Liste os 3 principais Code Smells do Código Original.
        2. "justificativa_refatoracao" (string): Explique como a refatoração reduz a CC.
        3. "cc_original_llm" (integer): O valor da Complexidade Ciclomática calculada para o Código Original.
        4. "cc_refatorado_llm" (integer): O valor da Complexidade Ciclomática calculada para o Código Refatorado.
        """
        json_string = self._make_api_request(analysis_prompt)
        
        try:
            # Tenta limpar blocos de código markdown e converter o JSON
            match = re.search(r"\{.*\}", json_string, re.DOTALL)
            if match:
                json_string = match.group(0).strip()
            
            return json.loads(json_string)
        
        except json.JSONDecodeError:
            raise RuntimeError("A LLM não retornou JSON válido na SEGUNDA CHAMADA (Análise).")
