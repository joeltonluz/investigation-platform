# Registro de Decisões Arquiteturais (ADR)

Este documento reúne as principais decisões técnicas do projeto, com o contexto que as
motivou, a decisão tomada e suas consequências (incluindo o que se abriu mão). O objetivo é
tornar explícito o *raciocínio* por trás da implementação — não apenas o resultado.

Formato: cada decisão segue a estrutura Contexto → Decisão → Consequências → Alternativas
consideradas. As decisões estão numeradas na ordem em que foram tomadas.

---

## ADR-001 — Realm único do Keycloak, com um client por aplicação

**Contexto.** A plataforma reúne três aplicações (Analytics, Investigator, Case Manager) que
compartilham os mesmos usuários. O requisito central de autenticação é SSO: o usuário faz
login uma vez e acessa todas as aplicações às quais tem permissão. Ao mesmo tempo, cada
aplicação precisa controlar suas permissões de forma independente, e remover o acesso a uma
aplicação não pode afetar as demais. A decisão era entre um realm único com múltiplos
clients, ou múltiplos realms (um por aplicação).

**Decisão.** Realm único (`plataforma`), com um *client* do Keycloak por aplicação. As
permissões independentes por aplicação são modeladas como *client roles* — cada client
define suas próprias roles (ex.: `analytics:viewer`, `investigator:senior-investigator`).

**Consequências.**
- SSO funciona nativamente: como a identidade e a sessão do usuário são únicas dentro do
  realm, o login em uma aplicação vale para as demais.
- Remover acesso a uma aplicação = remover a client role correspondente, sem tocar nas
  outras.
- A identificação de qual aplicação originou a requisição sai do claim `azp` (authorized
  party) do token, que aponta o client.
- Administração centralizada dos usuários (um só lugar para gerenciar identidades).

**Alternativas consideradas.** Múltiplos realms foram descartados porque um realm é uma
fronteira de isolamento total no Keycloak: usuários e sessões não são compartilhados entre
realms. Isso **quebraria o SSO** — o usuário precisaria logar separadamente em cada
aplicação —, violando o requisito principal. Múltiplos realms fazem sentido para
multi-tenancy (clientes distintos que nunca se cruzam), que não é o caso aqui. O isolamento
extra que eles ofereceriam é isolamento de *identidade*, que neste projeto é um anti-requisito.

---

## ADR-002 — PostgreSQL desde o início, sem SQLite (nem em testes)

**Contexto.** É comum usar SQLite em desenvolvimento e testes pela conveniência (sem setup,
em memória) e reservar o Postgres para produção. Precisávamos decidir se adotaríamos esse
atalho ou usaríamos Postgres em todos os ambientes.

**Decisão.** PostgreSQL em todos os ambientes, incluindo os testes, que rodam contra um
Postgres descartável em container Docker. Nenhum caminho com SQLite é introduzido.

**Consequências.**
- Elimina uma classe inteira de bugs do tipo "funciona na minha máquina": o campo
  `investigator_entities.data` depende de semântica **JSONB** do Postgres, e a migration
  cria índices cujo comportamento difere entre bancos. Testar no mesmo motor que a produção
  remove esse risco.
- Custo assumido: os testes exigem um Postgres de teste no ar, o que adiciona alguns
  segundos e um passo de setup em relação ao SQLite em memória. Consideramos o custo pequeno
  diante do risco evitado, especialmente por haver uma demo ao vivo.

**Alternativas consideradas.** SQLite para testes foi descartado justamente porque a
divergência de tipos e de comportamento de índices poderia fazer um teste passar localmente
e o mesmo código falhar em produção — o pior momento para descobrir uma incompatibilidade.

---

## ADR-003 — Camadas finas (Repository + Strategy), sem Clean/Hexagonal completa

**Contexto.** O projeto pede boas práticas de arquitetura, mas também pragmatismo e
simplicidade. Havia a tentação de aplicar uma arquitetura em camadas completa (Clean ou
Hexagonal, com ports/adapters, casos de uso, entidades de domínio isoladas etc.).

**Decisão.** Adotar camadas finas com dois padrões bem definidos: **Repository** (todo
acesso a banco passa por uma classe repositório; rotas e serviços nunca executam query crua
nem tocam a Session diretamente) e **Strategy** (cada aplicação implementa uma
`SearchStrategy` com a mesma interface, e o endpoint apenas seleciona e orquestra). O fluxo é
rota → dependência de autenticação → dependência de autorização → SearchService → Strategy →
Repository → AuditService.

**Consequências.**
- O endpoint de busca não contém ramificações específicas por aplicação além de escolher a
  strategy. Adicionar uma quarta aplicação não exige editar o núcleo do endpoint.
- Cada camada é testável isoladamente (a strategy sem o endpoint, o repositório sem a rota).
- Assume-se conscientemente não ter a separação máxima de uma Clean Architecture. Para o
  escopo deste projeto, essa separação seria over-engineering e, num contexto que valoriza
  pragmatismo, poderia ser lida como falta dele.

**Alternativas consideradas.** Clean/Hexagonal completa foi descartada pelo custo de
cerimônia (mais camadas, mais indireção) desproporcional ao tamanho do problema.

---

## ADR-004 — Estratégias de busca centralizadas no módulo `search` (Visão A)

**Contexto.** Com o padrão Strategy definido, restava decidir *onde* as estratégias de cada
aplicação moram: centralizadas no módulo `search`, ou distribuídas — cada aplicação dona da
sua própria estratégia dentro do seu próprio módulo (mais fiel ao estilo de módulos do
NestJS).

**Decisão.** Centralizar as estratégias em `app/search/strategies/`
(`analytics.py`, `investigator.py`, `case_manager.py`). Cada strategy chama o repositório do
domínio correspondente.

**Consequências.**
- A lógica avaliada pelo enunciado (o comportamento de busca por aplicação) fica concentrada
  em um único módulo, fácil de revisar e testar em conjunto.
- Cada fatia de trabalho (proposta OpenSpec) que mexe em busca toca um módulo só, o que
  mantém o escopo pequeno — relevante por usarmos assistência de IA, que se beneficia de
  contexto reduzido.
- Os módulos de domínio ficam finos (essencialmente model + repositório).

**Alternativas consideradas.** Distribuir a busca por domínio (cada aplicação dona da sua
strategy) é arquiteturalmente mais coeso e mais próximo do NestJS, e seria a evolução natural
caso o número de aplicações cresça. Foi descartado agora pelo custo de espalhar a lógica por
vários pacotes e exigir um mecanismo de registro/descoberta de strategies, sem retorno
proporcional no escopo atual.

---

## ADR-005 — Models SQLAlchemy centralizados

**Contexto.** Decorrente da ADR-004: com as estratégias centralizadas, os módulos de domínio
ficaram finos. Restava decidir se cada domínio teria seu próprio arquivo de models ou se os
models ficariam centralizados.

**Decisão.** Centralizar os models em `app/db/` sobre uma `Base` declarativa compartilhada,
em vez de criar um pacote por domínio só para abrigar um model cada.

**Consequências.**
- O Alembic enxerga todos os models a partir de um único ponto de importação, o que evita o
  erro clássico de esquecer de importar um model e gerar uma migration incompleta.
- Menos pontos de falha e contexto menor para trabalhar cada fatia.
- Coerente com a prática de um módulo de dados/infra compartilhado (análogo a um módulo core
  compartilhado no NestJS).

**Alternativas consideradas.** Um `models.py` por domínio foi descartado por criar pacotes
quase vazios (um model cada) e multiplicar os pontos que o Alembic precisa importar.

---

## ADR-006 — Fluxo trunk-based (commits direto na main), sem feature branches

**Contexto.** É um projeto solo, de curta duração, com um único autor. Precisávamos decidir
a estratégia de versionamento: trunk-based (direto na main) ou feature branches com PRs.

**Decisão.** Trabalhar diretamente na branch `main`, com commits pequenos e ordenados que
contam a narrativa de TDD (o commit do teste que falha precede o da implementação).

**Consequências.**
- Menos cerimônia, adequado a um repositório de autor único onde não há revisão de terceiros
  nem risco de conflito com outra pessoa.
- O histórico de commits pequenos e sequenciais serve como registro do processo de
  desenvolvimento.

**Alternativas consideradas.** Feature branches + PR + CI seriam a escolha correta num time
com múltiplos desenvolvedores e revisão de código. Foram descartadas aqui por serem cerimônia
sem benefício num contexto solo e de curta duração. Num ambiente real de equipe, esta decisão
seria revista.

---

## ADR-007 — Autenticação com JWT desacoplada do Keycloak (mock via chave RSA em testes)

**Contexto.** O ambiente real usa Keycloak, mas configurá-lo é caro em tempo e não deveria
ser pré-requisito para desenvolver e testar a lógica de autenticação e autorização.

**Decisão.** A validação do JWT é uma dependência do FastAPI que valida tokens RS256 contra
uma chave pública. Em testes, o Keycloak é mockado: um par de chaves RSA local assina os
tokens de teste, e a dependência valida contra a chave pública correspondente. O caminho de
código é o mesmo de produção — muda apenas a origem da chave (chave local em testes, JWKS do
Keycloak na stack em execução).

**Consequências.**
- Os testes de autenticação e autorização rodam sem subir o Keycloak, mantendo a suíte
  rápida e independente de infra externa.
- A troca para o Keycloak real é uma questão de configuração (origem da chave), sem alterar a
  lógica da aplicação.
- A estrutura exata do claim de permissões só será fixada quando os mappers do Keycloak forem
  configurados; até lá, o formato esperado do JWT é documentado junto ao código de auth.

**Alternativas consideradas.** Exigir Keycloak real para todos os testes foi descartado por
acoplar a suíte a uma infraestrutura pesada e lenta, contrariando a agilidade que o TDD exige.

---

## ADR-008 — Chave primária UUID, manipulada como string na aplicação

**Contexto.** As tabelas do enunciado têm `id`, sem tipo especificado. As opções realistas
eram inteiro auto-incremento ou UUID. O projeto é descrito como uma plataforma distribuída
on-premises, o que favorece identificadores únicos globalmente.

**Decisão.** Chave primária UUID em todas as tabelas. A coluna usa o tipo UUID nativo do
Postgres, com o valor gerado no **banco** via `server_default gen_random_uuid()` (função
nativa do Postgres 16). Na aplicação, o id é manipulado como **string** (`Mapped[str]` com
`UUID(as_uuid=False)` no SQLAlchemy), não como objeto `uuid.UUID` do Python.

**Consequências.**
- IDs únicos sem coordenação central — adequado a um sistema distribuído — e sem expor o
  volume de registros, como um inteiro sequencial exporia.
- Gerar o UUID no banco (e não na aplicação) garante que registros criados fora da aplicação
  — como o seed via SQL — também recebam id automaticamente.
- Trade-off assumido: manipular o id como string, e não como objeto `uuid.UUID`, simplifica a
  camada de aplicação (evita conversões em models e repositórios) ao custo de não ter as
  operações tipadas do objeto UUID. A coluna no banco continua sendo UUID nativo (indexação,
  armazenamento e validação de formato são os do tipo nativo); apenas a representação em
  Python é string. Caso operações sobre UUID passem a ser necessárias, a mudança para
  `as_uuid=True` é localizada.

**Alternativas consideradas.** Inteiro auto-incremento foi descartado por ser menos coerente
com o contexto distribuído e por expor volume/ordem de criação. Manipular como objeto
`uuid.UUID` (`as_uuid=True`) foi preterido em favor da simplicidade da string, já que o
projeto não precisa das operações do objeto.

---

## ADR-009 — Campos de valores fixos como ENUM nativo do Postgres

**Contexto.** Dois campos têm um conjunto fixo de valores válidos: `investigator_entities.type`
∈ {person, company, transaction, document} e `case_manager_cases.status` ∈ {open, in_progress,
closed}. A escolha era entre string com validação na aplicação, ou tipo ENUM nativo do banco.

**Decisão.** ENUM nativo do Postgres para ambos os campos. A integridade é garantida na
camada de dados: o banco recusa qualquer valor fora do conjunto, independentemente da
aplicação. Na migration, o ciclo de vida dos tipos enum é controlado explicitamente — criados
com `checkfirst=True` antes das tabelas e removidos no downgrade —, tornando a migration
segura para ciclos repetidos de upgrade/downgrade.

**Consequências.**
- Integridade garantida no nível mais baixo (o banco), não apenas na aplicação. É impossível
  inserir um `type` ou `status` inválido, mesmo por acesso direto ao banco.
- Custo assumido conscientemente: alterar um enum do Postgres depois é trabalhoso — adicionar
  um valor exige `ALTER TYPE ... ADD VALUE`, e remover um valor praticamente exige recriar o
  tipo. Para este projeto os conjuntos são fixos e conhecidos, então o custo é baixo. Se o
  domínio exigisse valores frequentemente mutáveis, uma string validada na aplicação seria
  preferível.
- A migration exigiu tratamento explícito da criação/remoção dos tipos (não confiar na
  criação implícita do `create_table`) para não quebrar em ciclos downgrade→upgrade.

**Alternativas consideradas.** String com validação na aplicação seria mais flexível e
tornaria as migrations triviais, mas moveria a garantia de integridade para fora do banco —
um valor inválido inserido por qualquer via que não passe pela aplicação não seria barrado.
Priorizou-se integridade sobre flexibilidade, dado que os conjuntos de valores são estáveis.
O campo `search_audit_log.app`, por outro lado, foi mantido como string simples, justamente
porque seu conjunto de valores tende a crescer conforme novas aplicações sejam integradas.

---

## Decisões ainda em aberto

- **Formato exato do claim de permissões no JWT.** Depende da configuração dos mappers do
  Keycloak. Será fixado e documentado quando a stack de autenticação for montada (ver
  ADR-007).