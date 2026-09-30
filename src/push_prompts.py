"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

DICAS DE IMPLEMENTAÇÃO:

- O push é feito pelo cliente do LangSmith:

      from langsmith import Client
      from langchain_core.prompts import ChatPromptTemplate

      client = Client()
      prompt = ChatPromptTemplate.from_messages([
          ("system", system_prompt),
          ("user", user_prompt),
      ])
      url = client.push_prompt(
          f"{username}/bug_to_user_story_v2",
          object=prompt,
          is_public=True,
          description="...",
          tags=[...],
      )

- `username` vem de USERNAME_LANGSMITH_HUB no .env e precisa ser o seu handle
  do Hub. Se você ainda não tem um handle, veja as instruções no .env.example.

- A variável do template precisa ser {bug_report}, que é a chave de entrada
  usada no dataset de avaliação.

- Use `load_yaml` de utils.py para ler o arquivo .yml.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langsmith import Client
from langchain_core.prompts import ChatPromptTemplate
from utils import load_yaml, check_env_vars, print_section_header, validate_prompt_structure

load_dotenv()


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).

    Args:
        prompt_name: Nome do prompt
        prompt_data: Dados do prompt

    Returns:
        True se sucesso, False caso contrário
    """
    try:
        username = os.getenv("USERNAME_LANGSMITH_HUB")

        client = Client()
        prompt = ChatPromptTemplate.from_messages([
            ("system", prompt_data["system_prompt"]),
            ("user", prompt_data["user_prompt"]),
        ])

        url = client.push_prompt(
            f"{username}/{prompt_name}",
            object=prompt,
            is_public=True,
            description=prompt_data.get("description", "Bug to user story prompt"),
            tags=[
                f"version: {prompt_data.get('version', 'v2')}",
                f"techniques_applied: [\"Few Shot\", \"Chain of Thought\", \"Role Prompting\", \"Skeleton of Thought\"]",
            ],
        )

        print(f"   ✓ Prompt publicado com sucesso")
        print(f"   ✓ {url}")
        return True

    except Exception as e:
        print(f"❌ Erro ao fazer push do prompt: {e}")
        return False


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt (versão simplificada).

    Args:
        prompt_data: Dados do prompt

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    errors = []

    if "user_prompt" not in prompt_data or not prompt_data.get("user_prompt", "").strip():
        errors.append("Campo obrigatório faltando ou vazio: user_prompt")

    if "{bug_report}" not in prompt_data.get("user_prompt", ""):
        errors.append("user_prompt precisa conter a variável {bug_report}")

    _, structure_errors = validate_prompt_structure(prompt_data)
    errors.extend(structure_errors)

    return (len(errors) == 0, errors)


def main():
    """Função principal"""
    print_section_header("Pushing prompt to LangSmith")

    if not check_env_vars(["LANGSMITH_API_KEY", "USERNAME_LANGSMITH_HUB"]):
        return 1

    prompt_path = Path("prompts/bug_to_user_story_v2.yml")
    prompt_data = load_yaml(str(prompt_path))

    if prompt_data is None:
        return 1

    is_valid, errors = validate_prompt(prompt_data)
    if not is_valid:
        print("❌ Prompt inválido:")
        for error in errors:
            print(f"   - {error}")
        return 1

    print("✓ Prompt validado com sucesso")

    prompt_name = f"bug_to_user_story_{prompt_data.get('version', 'v2')}"
    success = push_prompt_to_langsmith(prompt_name, prompt_data)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
