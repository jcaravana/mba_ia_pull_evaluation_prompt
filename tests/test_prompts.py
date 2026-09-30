"""
Testes automatizados para validação de prompts.
"""
import pytest
import yaml
import re
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def load_prompts(file_path: str):
    """Carrega prompts do arquivo YAML."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


def discover_prompt_files():
    """
    Lista os .yml de prompts/ que seguem o schema dict (system_prompt/user_prompt).

    Arquivos em outro formato — como um prompt puxado bruto do Hub, serializado
    como objetos do LangChain — não são carregáveis por yaml.safe_load ou não têm
    'system_prompt', e são ignorados aqui em vez de quebrar a coleta dos testes.
    """
    valid = []
    for path in sorted(PROMPTS_DIR.glob("*.yml")):
        try:
            data = load_prompts(str(path))
        except yaml.YAMLError:
            continue
        if isinstance(data, dict) and "system_prompt" in data:
            valid.append(path)
    return valid


PROMPT_FILES = discover_prompt_files()
PROMPT_IDS = [p.name for p in PROMPT_FILES]


@pytest.fixture(params=PROMPT_FILES, ids=PROMPT_IDS)
def prompt(request):
    return load_prompts(str(request.param))


class TestPrompts:
    def test_prompt_has_system_prompt(self, prompt):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""
        assert "system_prompt" in prompt
        assert prompt["system_prompt"].strip() != ""

    def test_prompt_has_role_definition(self, prompt):
        """Verifica se o prompt define uma persona (ex: "Você é um Product Manager")."""
        assert re.search(r"voc[eê] é um[a]?", prompt.get("system_prompt", ""), re.IGNORECASE)

    def test_prompt_mentions_format(self, prompt):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        text = prompt.get("system_prompt", "").lower()
        assert "como um" in text and "critérios de aceitação" in text

    def test_prompt_has_few_shot_examples(self, prompt):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        text = prompt.get("system_prompt", "").lower()
        assert text.count("<bug_report>") >= 2
        assert text.count("<resposta>") >= 2

    def test_prompt_no_todos(self, prompt):
        """Garante que você não esqueceu nenhum `[TODO]` no texto."""
        assert "[TODO]" not in prompt.get("system_prompt", "")
        assert "[TODO]" not in prompt.get("user_prompt", "")

    def test_minimum_techniques(self, prompt):
        """Verifica (através dos metadados do yaml) se pelo menos 2 técnicas foram listadas."""
        techniques = prompt.get("techniques_applied", [])
        assert len(techniques) >= 2

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])