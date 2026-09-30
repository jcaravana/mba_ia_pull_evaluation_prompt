# Pull, Otimização e Avaliação de Prompts com LangChain e LangSmith

Desafio técnico do MBA em Engenharia de Software com IA da Full Cycle.

## Objetivo

O projeto tem como missão:

- Fazer pull de um prompt de baixa qualidade (`bug_to_user_story_v1`) do LangSmith Prompt Hub
- Refatorar e otimizar esse prompt usando técnicas avançadas de Prompt Engineering
- Fazer push do prompt otimizado (`bug_to_user_story_v2`) de volta ao LangSmith
- Avaliar a qualidade com as métricas Helpfulness, Correctness, F1-Score, Clarity e Precision
- Atingir nota mínima de **0.8** em todas as métricas

O prompt recebe um relato de bug e devolve uma user story no formato "Como um..., eu quero..., para que...", com critérios de aceitação em Dado/Quando/Então.

## Sumário

- [A) Técnicas Aplicadas](#a-técnicas-aplicadas)
- [B) Resultados Finais](#b-resultados-finais)
- [C) Evidências no LangSmith](#c-evidências-no-langsmith)
- [D) Como Executar](#d-como-executar)

---

## A) Técnicas Aplicadas

Para refatorar o prompt escolhi quatro técnicas: **Role Prompting**, **Chain of Thought**, **Skeleton of Thought** e **Few-shot Learning** (obrigatória). Elas estão listadas também no campo `techniques_applied` do `prompts/bug_to_user_story_v2.yml`.

Resumo rápido do papel de cada uma:

| Técnica | Papel no prompt |
|---|---|
| Role Prompting | Define **quem** responde: um PO sênior com visão técnica |
| Chain of Thought | Faz o modelo **analisar e classificar** o bug antes de escrever |
| Skeleton of Thought | Define **como** a resposta deve ser montada para cada nível de complexidade |
| Few-shot Learning | **Mostra** o resultado esperado com exemplos completos |

### A.1. Role Prompting

#### Por que escolhi

Achei que essa era a base de tudo. Na v1 o modelo era "um assistente", e isso é genérico demais. Uma user story boa precisa de alguém que pense no **valor para o usuário**, não só em descrever o erro. Ao mesmo tempo, as respostas esperadas no dataset trazem causa provável, sugestão de solução e até tasks técnicas, coisa que um PO "de negócio" puro não faria.

Então defini uma persona que junta as duas coisas: um PO sênior com bagagem técnica.

#### Como apliquei

Logo no início do system prompt:

```
# PAPEL
Você é um Product Owner sênior, especialista em transformar relatos de bugs
de usuários em user stories claras, testáveis e prontas para o backlog. Você
domina o formato INVEST, escrita de critérios de aceitação em BDD
(Dado/Quando/Então) e tem conhecimento técnico suficiente para identificar
impacto, causa provável e requisitos não funcionais sem inventar informações.
```

Citei INVEST e BDD de propósito, porque puxam o vocabulário certo. Depois disso as respostas começaram a vir no formato "Como um..., eu quero..., para que...", mesmo antes de eu colocar os exemplos.

### A.2. Chain of Thought (CoT)

#### Por que escolhi

O maior problema que eu enxerguei é que **o formato da resposta depende da complexidade do bug**. Olhando o dataset, um bug simples ("campo de email aceita texto sem @") tem uma resposta curta, enquanto um bug com quatro problemas numerados tem uma resposta enorme, com várias seções. Se o modelo classificar errado, a resposta inteira sai no formato errado.

Por isso quis que o modelo "pensasse antes de escrever", seguindo uma ordem fixa de análise.

#### Como apliquei

Criei a seção `PROCESSO DE RACIOCÍNIO` com 7 passos: persona, comportamento atual × esperado, valor de negócio, extração dos dados concretos, classificação da complexidade, definição dos critérios e revisão final.

O passo 5 foi o que mais mexi. Na primeira versão ele era subjetivo ("vários problemas relacionados, impacto crítico..."), e nos testes o modelo às vezes respondia um bug com vários problemas usando só o formato simples. Então transformei em uma **regra mecânica**:

```
5. Classificar a complexidade — regra mecânica, aplique sempre:
   - COMPLEXO: o relato tem 2 OU MAIS problemas numerados/marcados OU cita
     impacto de negócio com números OU é falha de segurança/vazamento de dados.
   - MÉDIO: só um problema, mas com detalhe técnico real (endpoint, log,
     código HTTP, causa, ambiente).
   - SIMPLES: só um problema, sem detalhe técnico.
   Essa classificação decide qual item da ESTRUTURA DA RESPOSTA usar.
```

Uma decisão importante: o raciocínio é **interno**. Pedi explicitamente para não exibir, porque a avaliação compara a resposta com uma referência que só tem a user story. Se o modelo mostrasse o passo a passo, a resposta ficaria poluída e perderia pontos em clareza.

O passo 7 ("Revisar: a story está no formato correto? Todos os critérios são testáveis? Nada foi inventado?") funciona como uma autochecagem no final.

### A.3. Skeleton of Thought

#### Por que escolhi

Mesmo sabendo a complexidade, o modelo ainda precisava saber **exatamente quais seções montar e em que ordem**. Sem isso, ele inventava títulos (numa das execuções apareceu até uma seção "Resposta Esperada") ou repetia a user story em lugares diferentes.

A ideia do Skeleton of Thought é definir primeiro a estrutura e depois preencher cada parte, e isso encaixou bem aqui.

#### Como apliquei

Na seção `ESTRUTURA DA RESPOSTA` montei um esqueleto para cada nível:

- **Simples:** frase da user story + "Critérios de Aceitação" (Dado que / Quando / Então / E).
- **Médio:** o mesmo bloco + seções extras escolhidas conforme o conteúdo do relato: "Contexto Técnico", "Exemplo de Cálculo", "Critérios Adicionais para [perfil]", "Critérios de Prevenção" etc.
- **Complexo:** um esqueleto fixo com marcadores `===`:

```
=== USER STORY PRINCIPAL ===
=== CRITÉRIOS DE ACEITAÇÃO ===   (A., B., C... um grupo por problema)
=== CRITÉRIOS TÉCNICOS ===
=== CONTEXTO DO BUG ===
=== TASKS TÉCNICAS SUGERIDAS ===
=== MÉTRICAS DE SUCESSO ===
```

Coloquei algumas travas porque vi o modelo "economizando" nos bugs complexos: "NUNCA omita um problema numerado no relato", "no mínimo 2 decisões técnicas concretas por problema" e "no mínimo 2 tarefas por problema". Também deixei claro que a "Descrição" deve reformular a user story, e não copiar, porque a repetição estava derrubando a nota de clareza.

Complementei o esqueleto com um **checklist de gatilhos técnicos**. Percebi que certos tipos de bug sempre pedem os mesmos critérios, e o modelo esquecia alguns. Por exemplo:

```
- Validação de campo/formulário: adicione um critério "E" exigindo que a
  mensagem de erro explique o formato esperado, não apenas "exibir erro".
- O relato descreve comportamento diferente para dois perfis de usuário:
  crie OBRIGATORIAMENTE um segundo bloco "Critérios Adicionais para [perfil]:".
- Endpoint retornando um código HTTP de erro: declare explicitamente o código
  HTTP esperado no caminho de sucesso (ex.: HTTP 200).
```

Na prática, isso funciona como uma extensão do esqueleto: além de dizer quais seções montar, diz o que não pode faltar dentro delas.

### A.4. Few-shot Learning

#### Por que escolhi

Essa era obrigatória, mas mesmo que não fosse eu usaria. Descrever um formato em texto só ajuda até certo ponto; mostrar um exemplo pronto é bem mais eficiente. Principalmente aqui, onde a diferença entre uma resposta simples e uma complexa é grande.

#### Como apliquei

Coloquei 4 exemplos completos de entrada e saída, cada um cobrindo um cenário:

| Exemplo | Cenário | O que ele ensina |
|---|---|---|
| 1 | Contador do carrinho não atualiza | Resposta curta, só story + critérios |
| 2 | CSV exportado com acentos quebrados | Uso de endpoint, navegador e causa provável em "Contexto Técnico" |
| 3 | Timeout no pagamento + cartão gravado em log | Formato completo com `===`, dois problemas viram grupos A, B e C |
| 4 | "o app ta travando toda hora, arrumem isso!!!" | Relato vago: gera o possível e lista "Informações Pendentes" |

Tomei o cuidado de **não copiar nenhum caso do dataset de avaliação** para os exemplos. Criei bugs parecidos em estilo, mas diferentes. Se eu usasse os próprios casos do dataset, a nota ia subir de forma artificial, porque o modelo já teria a resposta pronta no prompt, e isso não mostraria que o prompt funciona de verdade.

O exemplo 4 também serve para mostrar um edge case, algo que só com regra escrita o modelo não pegava tão bem.

---

## B) Resultados Finais

### B.1. Link público do dataset de avaliação, com os experimentos

https://smith.langchain.com/public/b73a8eb8-f12c-407e-87c7-905cb5dbb5b1/d

### B.2. Screenshots das avaliações com as notas mínimas de 0.8 atingidas

Notas finais do `bug_to_user_story_v2`:

| Métrica | Nota | Status |
|---|---|---|
| Helpfulness | 0.94 | ✓ |
| Correctness | 0.93 | ✓ |
| F1-Score | 0.90 | ✓ |
| Clarity | 0.91 | ✓ |
| Precision | 0.96 | ✓ |

![Resultado da avaliação](<Captura de tela 2026-09-30 052723.png>)

![Experimento no LangSmith](<Captura de tela 2026-09-30 052754.png>)

![Detalhe das notas](<Captura de tela 2026-09-30 052809.png>)

### B.3. Comparação entre o prompt original (v1) e o otimizado (v2): o que mudou e por quê

#### B.3.1. Como era a v1

A v1 era bem enxuta. O system prompt tinha basicamente isto:

```
Você é um assistente que ajuda a transformar relatos de bugs de usuários em tarefas para desenvolvedores.

Analise o relato de bug abaixo e crie uma user story a partir dele.

Relato de Bug:
---
{bug_report}
---

User Story gerada:
```

E o user prompt era só `{bug_report}`.

Olhando com calma, identifiquei alguns problemas:

- **Persona genérica:** "um assistente" não dá contexto nenhum para o modelo sobre como uma user story deve ser escrita.
- **Nenhum formato definido:** o prompt pede "uma user story", mas não diz qual estrutura usar. Não fala em "Como um..., eu quero..., para que...", nem em critérios de aceitação.
- **Nenhum exemplo:** era zero-shot puro.
- **Nenhuma regra:** nada sobre idioma, tamanho, o que fazer com relato vazio etc.
- **Relato duplicado:** o `{bug_report}` aparecia no system **e** no user prompt, então o modelo recebia o mesmo texto duas vezes, e a instrução ficava misturada com o dado.

O resultado disso é que cada execução podia sair de um jeito diferente, e não tinha como garantir que a resposta ficasse parecida com o que o dataset espera.

#### B.3.2. O que mudou na v2 e por quê

##### B.3.2.1. Separação entre system e user prompt

**Antes:** o relato estava no system e no user.
**Agora:** o system prompt tem só o conteúdo fixo (papel, regras, estrutura, exemplos) e nenhuma variável. O user prompt tem só a instrução curta e o relato entre `<bug_report>`.

**Por quê:** o system prompt ficou sendo a "configuração" do comportamento, e o user prompt o "dado" de cada execução. Isso tirou a duplicação e, com a regra 9, ajuda a evitar que alguém escreva uma instrução dentro do relato para mudar o comportamento do modelo.

##### B.3.2.2. Persona: de "assistente" para Product Owner sênior

**Antes:** "Você é um assistente que ajuda a transformar relatos de bugs..."
**Agora:** um Product Owner sênior que domina INVEST e BDD e tem conhecimento técnico para identificar impacto e causa provável.

**Por quê:** as respostas de referência do dataset não descrevem só o comportamento correto. Elas trazem contexto técnico, causa e tasks. Um PO com visão técnica é quem naturalmente escreveria desse jeito.

##### B.3.2.3. Raciocínio antes de responder

**Antes:** nenhum.
**Agora:** 7 passos internos (persona, comportamento atual × esperado, valor, dados concretos, complexidade, critérios e revisão), sem exibir o raciocínio na resposta.

**Por quê:** o formato da resposta muda muito dependendo da complexidade do bug, então o modelo precisa classificar antes de escrever. Deixei a classificação como uma regra objetiva (quantidade de problemas, impacto com números, segurança) porque, quando ela era mais subjetiva, o modelo às vezes respondia um bug grande no formato curto.

##### B.3.2.4. Estrutura de resposta definida

**Antes:** só "User Story gerada:".
**Agora:** um esqueleto para cada nível:

- **Simples:** story + critérios de aceitação em Dado que / Quando / Então / E.
- **Médio:** o mesmo, mais seções extras quando o relato tiver a informação (Contexto Técnico, Exemplo de Cálculo, Critérios Adicionais para [perfil] etc.).
- **Complexo:** seções com `===` (user story principal, critérios agrupados em A, B, C, critérios técnicos, contexto do bug, tasks e métricas).

**Por quê:** foi o padrão que encontrei nas respostas de referência do dataset. Com o esqueleto, a resposta fica previsível e fácil de ler.

##### B.3.2.5. Regras explícitas de comportamento

**Antes:** nenhuma.
**Agora:** 13 regras. As principais:

- sempre em português do Brasil;
- critérios objetivos e testáveis, sem termos vagos como "funcionar corretamente";
- reaproveitar literalmente os números, endpoints e códigos HTTP do relato;
- não inventar títulos de seção nem repetir a mesma informação em lugares diferentes;
- não mostrar saudação, explicação nem o raciocínio.

**Por quê:** várias dessas regras vieram de problemas que vi nos testes, como respostas repetindo a user story na descrição, seções com nomes inventados e dados do relato que ficavam de fora.

##### B.3.2.6. Checklist de gatilhos técnicos

**Antes:** não existia.
**Agora:** uma lista do tipo "se aparecer X no relato, o critério Y é obrigatório". Por exemplo: validação de formulário exige mensagem explicando o formato; dois perfis de usuário exigem "Critérios Adicionais para [perfil]"; endpoint com erro HTTP exige o código esperado no caminho de sucesso.

**Por quê:** o modelo acertava a estrutura mas esquecia critérios que as referências sempre incluem. O checklist deixa isso mais mecânico.

##### B.3.2.7. Tratamento de edge cases

**Antes:** nada.
**Agora:** relato vazio, relato vago, vários problemas relacionados ou sem relação, pedido de funcionalidade, falha de segurança, dados sensíveis (senha, token, CPF) e tom agressivo.

**Por quê:** sem isso o comportamento nesses casos fica imprevisível. No caso de dados sensíveis, também é uma questão de não reproduzir informação que não deveria aparecer.

##### B.3.2.8. Few-shot

**Antes:** zero exemplos.
**Agora:** 4 exemplos completos: um simples (contador do carrinho), um médio (CSV com acentos quebrados), um complexo (timeout no pagamento + cartão no log) e um de relato vago.

**Por quê:** mostrar a resposta pronta é bem mais eficiente do que só descrever o formato. Criei exemplos novos em vez de usar os casos do dataset, para não "entregar a resposta" ao modelo e mascarar a avaliação.

##### B.3.2.9. Formato do arquivo

**Antes:** o YAML era a serialização dos objetos do LangChain (`SystemMessagePromptTemplate`, `HumanMessagePromptTemplate` etc.).
**Agora:** um YAML simples com `system_prompt` e `user_prompt`, mais `description` e `techniques_applied` documentando o que foi usado.

**Por quê:** fica muito mais fácil de ler, revisar e versionar.

#### B.3.3. Resumo da comparação

| Aspecto | v1 | v2 |
|---|---|---|
| Persona | Assistente genérico | PO sênior com visão técnica |
| Formato de saída | Não definido | Esqueleto por nível de complexidade |
| Raciocínio | Nenhum | 7 passos internos |
| Regras | Nenhuma | 13 regras + checklist de gatilhos |
| Exemplos | 0 | 4 |
| Edge cases | Nenhum | 8 cenários |
| `{bug_report}` | No system e no user | Só no user, entre tags |
| Arquivo | Objetos serializados do LangChain | YAML simples e documentado |

Em resumo, a v1 dizia **o que** fazer ("crie uma user story"), e a v2 diz **quem** faz, **como** pensar, **em que formato** responder e **o que não pode faltar**, com exemplos mostrando o resultado esperado.

---

## C) Evidências no LangSmith

Link público: https://smith.langchain.com/public/b73a8eb8-f12c-407e-87c7-905cb5dbb5b1/d

O que pode ser conferido no LangSmith:

### C.1. Dataset de avaliação com 15 exemplos

Dataset criado pelo `src/evaluate.py` a partir de `datasets/bug_to_user_story.jsonl`, com 5 bugs simples, 7 médios e 3 complexos.

![Dataset com 15 exemplos](<Captura de tela 2026-09-30 061023.png>)

### C.2. Execuções do prompt v2 com notas ≥ 0.8

Experimento do `bug_to_user_story_v2`, com as notas das 5 métricas gravadas como feedback.

![Experimento v2 com notas](<Captura de tela 2026-09-30 052754.png>)

### C.3. Tracing detalhado de pelo menos 3 exemplos

Tracing detalhado dos exemplos selecionados:

![Trace detalhado 1](<Captura de tela 2026-09-30 061609.png>)

![Trace detalhado 2](<Captura de tela 2026-09-30 061649.png>)

![Trace detalhado 3](<Captura de tela 2026-09-30 061657.png>)

---

## D) Como Executar

### D.1. Estrutura do projeto

```
mba-ia-pull-evaluation-prompt/
├── .env.example                  # Template das variáveis de ambiente
├── requirements.txt              # Dependências Python
├── README.md                     # Esta documentação
├── prompts/
│   ├── bug_to_user_story_v1.yml  # Prompt original (pull)
│   └── bug_to_user_story_v2.yml  # Prompt otimizado
├── datasets/
│   └── bug_to_user_story.jsonl   # 15 bugs para avaliação
├── src/
│   ├── pull_prompts.py           # Pull do LangSmith Hub
│   ├── push_prompts.py           # Push ao LangSmith Hub
│   ├── evaluate.py               # Avaliação automática
│   ├── metrics.py                # Métricas de avaliação
│   └── utils.py                  # Funções auxiliares
└── tests/
    └── test_prompts.py           # Testes de validação do prompt
```

### D.2. Pré-requisitos

- **Python 3.10+**
- **Git**
- **Conta no LangSmith** com uma API Key: https://smith.langchain.com
- **Handle público no LangSmith Hub** (usado no nome do prompt, ex.: `meu-handle/bug_to_user_story_v2`). Ele é criado quando você torna um prompt público pela primeira vez:
  1. Abra o LangSmith e vá em **Prompts**
  2. Crie ou abra um prompt qualquer
  3. Clique nos **três pontinhos** ao lado do botão **Playground**
  4. Escolha **Make Public**
  5. Em **Choose your public handle**, defina o handle (ele é definitivo depois de confirmado)
- **API Key de um provedor de LLM**, uma das duas:
  - OpenAI: https://platform.openai.com/api-keys
  - Google Gemini: https://aistudio.google.com/app/apikey

### D.3. Dependências

Todas estão no `requirements.txt`:

| Pacote | Uso |
|---|---|
| `langchain-core` | `ChatPromptTemplate` e composição das chains |
| `langsmith` | Pull/push de prompts, datasets, tracing e avaliação |
| `langchain-openai` | Provider OpenAI |
| `langchain-google-genai` | Provider Gemini |
| `python-dotenv` | Leitura do `.env` |
| `pyyaml` | Leitura e escrita dos prompts em YAML |
| `pydantic` | Validação de dados |
| `pytest` | Testes de validação do prompt |

### D.4. Instalação

```bash
# 1. Clonar o repositório
git clone [URL do seu fork]
cd mba-ia-pull-evaluation-prompt

# 2. Criar e ativar o ambiente virtual
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Instalar as dependências
pip install -r requirements.txt
```

### D.5. Configuração do `.env`

Copie o template e preencha as variáveis:

```bash
cp .env.example .env            # Windows: copy .env.example .env
```

| Variável | Descrição |
|---|---|
| `LANGSMITH_TRACING` | `true` para gravar os traces no LangSmith |
| `LANGSMITH_ENDPOINT` | `https://api.smith.langchain.com` |
| `LANGSMITH_API_KEY` | Sua API Key do LangSmith |
| `LANGSMITH_PROJECT` | Nome do projeto; também é usado para montar o nome do dataset (`<projeto>-eval`) |
| `USERNAME_LANGSMITH_HUB` | Seu handle público do LangSmith Hub |
| `LLM_PROVIDER` | `openai` ou `google` |
| `OPENAI_API_KEY` | Obrigatória se o provider for `openai` |
| `GOOGLE_API_KEY` | Obrigatória se o provider for `google` |
| `LLM_MODEL` | Modelo que gera as user stories |
| `EVAL_MODEL` | Modelo que avalia as respostas (pode ser o mesmo ou um mais capaz) |

Configuração que usei: [preencher: provider, LLM_MODEL e EVAL_MODEL].

### D.6. Execução por fase

**Fase 1: pull do prompt original (v1)**

```bash
python src/pull_prompts.py
```

Baixa o prompt `bug_to_user_story_v1` do LangSmith Hub e salva em `prompts/bug_to_user_story_v1.yml`.

**Fase 2: refatoração do prompt**

Não tem comando: é a edição do arquivo `prompts/bug_to_user_story_v2.yml`, aplicando as técnicas descritas na seção A. O arquivo tem os campos `system_prompt`, `user_prompt`, `description` e `techniques_applied`.

**Fase 3: validação automatizada do prompt**

```bash
pytest tests/test_prompts.py -v
```

Antes de publicar, essa fase valida localmente (sem chamar o LangSmith nem nenhum LLM) se o prompt refatorado está estruturalmente correto. O `tests/test_prompts.py` varre todo `.yml` de `prompts/` que siga o schema `system_prompt`/`user_prompt` — hoje só o `bug_to_user_story_v2.yml` se encaixa, mas um `v3.yml` futuro entraria automaticamente — e roda 6 checagens em cada um:

1. `system_prompt` existe e não está vazio
2. Define uma persona (ex.: "Você é um...")
3. Exige o formato de user story ("Como um..." + "Critérios de Aceitação")
4. Tem pelo menos 2 exemplos few-shot (pares `<bug_report>`/`<resposta>`)
5. Não ficou nenhum `[TODO]` esquecido no texto
6. Lista pelo menos 2 técnicas em `techniques_applied`

Só siga para o push se todos os testes passarem.

**Fase 4: push do prompt otimizado (v2)**

```bash
python src/push_prompts.py
```

Lê o `prompts/bug_to_user_story_v2.yml`, valida o conteúdo e publica como `<USERNAME_LANGSMITH_HUB>/bug_to_user_story_v2` (público) no LangSmith Hub.

**Fase 5: avaliação**

```bash
python src/evaluate.py
```

O script:

1. Cria (ou reutiliza) o dataset `<LANGSMITH_PROJECT>-eval` com os 15 exemplos de `datasets/bug_to_user_story.jsonl`
2. Faz pull do `bug_to_user_story_v2` do Hub
3. Gera a user story de cada exemplo com o `LLM_MODEL`
4. Avalia cada resposta com o `EVAL_MODEL` nas 5 métricas
5. Grava as notas como feedback no experimento do LangSmith e mostra no terminal se o prompt foi **APROVADO** (todas as métricas ≥ 0.8)
