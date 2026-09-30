# Pull, Otimização e Avaliação de Prompts com LangChain e LangSmith
Desafio técnico do MBA em Engenharia de Software com IA da FullCycle. O projeto entrega um software capaz de:

## Objetivo

Desafio técnico do MBA em Engenharia de Software com IA da FullCycle. O projeto entrega um software e a missão de:

- Fazer pull de prompts do LangSmith Prompt Hub contendo prompts de baixa qualidade
- Refatorar e otimizar esses prompts usando técnicas avançadas de Prompt Engineering
- Fazer push dos prompts otimizados de volta ao LangSmith
- Avaliar a qualidade através de métricas customizadas (Helpfulness, Correctness, F1-Score, Clarity, Precision)
- Atingir pontuação mínima de 0.8 (80%) em todas as métricas de avaliação

## Exemplo no CLI

Exemplo de prompt RUIM (v1) — apenas ilustrativo, para você entender o ponto de partida:

```
==================================================
Prompt: {seu_username}/bug_to_user_story_v1
==================================================

Métricas Derivadas:
  - Helpfulness: 0.45 ✗
  - Correctness: 0.52 ✗

Métricas Base:
  - F1-Score: 0.48 ✗
  - Clarity: 0.50 ✗
  - Precision: 0.46 ✗

❌ STATUS: REPROVADO
⚠️  Métricas abaixo de 0.8: helpfulness, correctness, f1_score, clarity, precision
```

Exemplo de prompt OTIMIZADO (v2) — seu objetivo é chegar aqui:

```
# Após refatorar os prompts e fazer push
python src/push_prompts.py

# Executar avaliação
python src/evaluate.py

Executando avaliação dos prompts...
==================================================
Prompt: {seu_username}/bug_to_user_story_v2
==================================================

Métricas Derivadas:
  - Helpfulness: 0.94 ✓
  - Correctness: 0.96 ✓

Métricas Base:
  - F1-Score: 0.93 ✓
  - Clarity: 0.95 ✓
  - Precision: 0.92 ✓

✅ STATUS: APROVADO - Todas as métricas >= 0.8

Resultados no LangSmith (notas gravadas como feedback no experimento):
  {seu_username}/bug_to_user_story_v2
    https://smith.langchain.com/o/.../datasets/.../compare?selectedSessions=...
```

## Tecnologias obrigatórias

- Linguagem: Python 3.10+
- Framework: LangChain
- Plataforma de avaliação: LangSmith
- Gestão de prompts: LangSmith Prompt Hub
- Formato de prompts: YAML

## Pacotes recomendados

```python
from langsmith import Client  # Pull/push de prompts, datasets e avaliação
from langchain_core.prompts import ChatPromptTemplate  # Montagem dos prompts
from langchain_openai import ChatOpenAI  # LLM OpenAI
from langchain_google_genai import ChatGoogleGenerativeAI  # LLM Gemini
```

## OpenAI

- Crie uma API Key da OpenAI: https://platform.openai.com/api-keys
- Você vai precisar de um modelo de LLM para responder e de um modelo de LLM para avaliação. Consulte a documentação oficial da OpenAI para ver os modelos disponíveis.
- Custo estimado: ~$1-5 para completar o desafio

## Gemini (modelo free)

- Crie uma API Key da Google: https://aistudio.google.com/app/apikey
- Você vai precisar de um modelo de LLM para responder e de um modelo de LLM para avaliação. Consulte a documentação oficial do Google para ver os modelos disponíveis.
- Os limites de requisições gratuitas mudam com frequência. Consulte os limites atuais na documentação oficial do Google.

## Escolha dos modelos

Este desafio não fixa modelos. Nomes e versões mudam com frequência e alguns são descontinuados, então faz parte do desafio consultar a documentação oficial do provedor que você escolher, ver quais modelos estão disponíveis no momento e selecionar os que atendem ao objetivo. Você pode usar o mesmo modelo para responder e para avaliar, ou um modelo mais capaz na avaliação.

## Handle do LangSmith Hub (seu username)

O LangSmith identifica os prompts que você publica por um **handle público**, no
formato `handle/nome_do_prompt`. Esse handle é o valor que vai em
`USERNAME_LANGSMITH_HUB` no `.env`.

Ele **não existe por padrão**: é criado no momento em que você torna um prompt
público pela primeira vez. Por isso, faça esta etapa antes de tentar o push:

1. Abra o LangSmith e vá em **Prompts**
2. Crie um prompt qualquer (pode ser de teste) ou abra um que você já tenha
3. Clique nos **três pontinhos** no canto superior direito, ao lado do botão **Playground**
4. Escolha **Make Public**
5. Na tela **Choose your public handle**, defina o seu handle

O handle é **definitivo** depois de confirmado, então escolha com calma. Feito
isso, ele aparece no endereço do prompt (`handle/nome_do_prompt`) e é esse valor
que você coloca no `.env`.


## Estrutura obrigatória do projeto

Faça um fork do repositório base: https://github.com/devfullcycle/mba-ia-pull-evaluation-prompt

```
mba-ia-pull-evaluation-prompt/
├── .env.example              # Template das variáveis de ambiente
├── requirements.txt          # Dependências Python
├── README.md                 # Sua documentação do processo
│
├── prompts/
│   ├── bug_to_user_story_v1.yml  # Prompt inicial (já incluso)
│   └── bug_to_user_story_v2.yml  # Seu prompt otimizado (criar)
│
├── datasets/
│   └── bug_to_user_story.jsonl   # 15 exemplos de bugs (já incluso)
│
├── src/
│   ├── pull_prompts.py       # Pull do LangSmith (implementar)
│   ├── push_prompts.py       # Push ao LangSmith (implementar)
│   ├── evaluate.py           # Avaliação automática (pronto)
│   ├── metrics.py            # 5 métricas implementadas (pronto)
│   └── utils.py              # Funções auxiliares (pronto)
│
├── tests/
│   └── test_prompts.py       # Testes de validação (implementar)
```

O que você deve implementar:

- prompts/bug_to_user_story_v2.yml — Criar do zero com seu prompt otimizado
- src/pull_prompts.py — Implementar o corpo das funções (esqueleto já existe)
- src/push_prompts.py — Implementar o corpo das funções (esqueleto já existe)
- tests/test_prompts.py — Implementar os 6 testes de validação (esqueleto já existe)
- README.md — Documentar seu processo de otimização

O que já vem pronto (não alterar):

- src/evaluate.py — Script de avaliação completo (cria o experimento no LangSmith e grava as notas como feedback)
- src/metrics.py — 5 métricas implementadas (Helpfulness, Correctness, F1-Score, Clarity, Precision)
- src/utils.py — Funções auxiliares
- datasets/bug_to_user_story.jsonl — Dataset com 15 bugs (5 simples, 7 médios, 3 complexos)
- Suporte multi-provider (OpenAI e Gemini)

## VirtualEnv para Python

Crie e ative um ambiente virtual antes de instalar dependências:

```
python3 -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Ordem de execução

1. Executar pull dos prompts ruins

```
python src/pull_prompts.py
```

2. Refatorar prompts

Edite manualmente o arquivo prompts/bug_to_user_story_v2.yml aplicando as técnicas aprendidas no curso.

3. Fazer push dos prompts otimizados

```
python src/push_prompts.py
```

4. Executar avaliação

```
python src/evaluate.py
```

## Entregável


## A) Seção "Técnicas Aplicadas (Fase 2)":


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

---

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

---

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

---

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

## B) Seção "Resultados Finais":

#### B.1 Link público do dataset de avaliação, com os experimentos
https://smith.langchain.com/public/b73a8eb8-f12c-407e-87c7-905cb5dbb5b1/d

#### B.2 Screenshots das avaliações com as notas mínimas de 0.8 atingidas
![alt text](<Captura de tela 2026-09-30 052723.png>)
![alt text](<Captura de tela 2026-09-30 052754.png>)
![alt text](<Captura de tela 2026-09-30 052809.png>)

#### B.3 Comparação entre o prompt original (v1) e o seu otimizado (v2): o que mudou e por quê
##### B.3.1 Como era a v1

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

##### B.3.2 O que mudou na v2 e por quê

###### B.3.2.1 Separação entre system e user prompt

**Antes:** o relato estava no system e no user.
**Agora:** o system prompt tem só o conteúdo fixo (papel, regras, estrutura, exemplos) e nenhuma variável. O user prompt tem só a instrução curta e o relato entre `<bug_report>`.

**Por quê:** o system prompt ficou sendo a "configuração" do comportamento, e o user prompt o "dado" de cada execução. Isso tirou a duplicação e, com a regra 9, ajuda a evitar que alguém escreva uma instrução dentro do relato para mudar o comportamento do modelo.

###### B.3.2.2 Persona: de "assistente" para Product Owner sênior

**Antes:** "Você é um assistente que ajuda a transformar relatos de bugs..."
**Agora:** um Product Owner sênior que domina INVEST e BDD e tem conhecimento técnico para identificar impacto e causa provável.

**Por quê:** as respostas de referência do dataset não descrevem só o comportamento correto. Elas trazem contexto técnico, causa e tasks. Um PO com visão técnica é quem naturalmente escreveria desse jeito.

###### B.3.2.3 Raciocínio antes de responder

**Antes:** nenhum.
**Agora:** 7 passos internos (persona, comportamento atual × esperado, valor, dados concretos, complexidade, critérios e revisão), sem exibir o raciocínio na resposta.

**Por quê:** o formato da resposta muda muito dependendo da complexidade do bug, então o modelo precisa classificar antes de escrever. Deixei a classificação como uma regra objetiva (quantidade de problemas, impacto com números, segurança) porque, quando ela era mais subjetiva, o modelo às vezes respondia um bug grande no formato curto.

###### B.3.2.4 Estrutura de resposta definida

**Antes:** só "User Story gerada:".
**Agora:** um esqueleto para cada nível:

- **Simples:** story + critérios de aceitação em Dado que / Quando / Então / E.
- **Médio:** o mesmo, mais seções extras quando o relato tiver a informação (Contexto Técnico, Exemplo de Cálculo, Critérios Adicionais para [perfil] etc.).
- **Complexo:** seções com `===` (user story principal, critérios agrupados em A, B, C, critérios técnicos, contexto do bug, tasks e métricas).

**Por quê:** foi o padrão que encontrei nas respostas de referência do dataset. Com o esqueleto, a resposta fica previsível e fácil de ler.

###### B.3.2.5 Regras explícitas de comportamento

**Antes:** nenhuma.
**Agora:** 13 regras. As principais:

- sempre em português do Brasil;
- critérios objetivos e testáveis, sem termos vagos como "funcionar corretamente";
- reaproveitar literalmente os números, endpoints e códigos HTTP do relato;
- não inventar títulos de seção nem repetir a mesma informação em lugares diferentes;
- não mostrar saudação, explicação nem o raciocínio.

**Por quê:** várias dessas regras vieram de problemas que vi nos testes, como respostas repetindo a user story na descrição, seções com nomes inventados e dados do relato que ficavam de fora.

###### B.3.2.6 Checklist de gatilhos técnicos

**Antes:** não existia.
**Agora:** uma lista do tipo "se aparecer X no relato, o critério Y é obrigatório". Por exemplo: validação de formulário exige mensagem explicando o formato; dois perfis de usuário exigem "Critérios Adicionais para [perfil]"; endpoint com erro HTTP exige o código esperado no caminho de sucesso.

**Por quê:** o modelo acertava a estrutura mas esquecia critérios que as referências sempre incluem. O checklist deixa isso mais mecânico.

###### B.3.2.7 Tratamento de edge cases

**Antes:** nada.
**Agora:** relato vazio, relato vago, vários problemas relacionados ou sem relação, pedido de funcionalidade, falha de segurança, dados sensíveis (senha, token, CPF) e tom agressivo.

**Por quê:** sem isso o comportamento nesses casos fica imprevisível. No caso de dados sensíveis, também é uma questão de não reproduzir informação que não deveria aparecer.

###### B.3.2.8 Few-shot

**Antes:** zero exemplos.
**Agora:** 4 exemplos completos: um simples (contador do carrinho), um médio (CSV com acentos quebrados), um complexo (timeout no pagamento + cartão no log) e um de relato vago.

**Por quê:** mostrar a resposta pronta é bem mais eficiente do que só descrever o formato. Criei exemplos novos em vez de usar os casos do dataset, para não "entregar a resposta" ao modelo e mascarar a avaliação.

###### B.3.2.9 Formato do arquivo

**Antes:** o YAML era a serialização dos objetos do LangChain (`SystemMessagePromptTemplate`, `HumanMessagePromptTemplate` etc.).
**Agora:** um YAML simples com `system_prompt` e `user_prompt`, mais `description` e `techniques_applied` documentando o que foi usado.

**Por quê:** fica muito mais fácil de ler, revisar e versionar.

#### C) Seção "Como Executar":

- Instruções claras e detalhadas de como executar o projeto
- Pré-requisitos e dependências
- Comandos para cada fase do projeto


