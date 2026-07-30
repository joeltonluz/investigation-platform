## Context

O `get_db()` em `src/app/db/session.py` cria uma sessão SQLAlchemy com `autocommit=False, autoflush=False` e nunca chama `db.commit()`. Quando o endpoint de busca registra auditoria via `AuditService(db).record_search()`, o `SearchAuditLogRepository.add()` faz `session.add()` + `session.flush()`, que escreve no buffer da transação. Ao final da requisição, `db.close()` é chamado sem commit — a transação é descartada (rollback implícito) e o registro de auditoria se perde.

## Goals / Non-Goals

**Goals:**
- Garantir que `SearchAuditLog` seja persistido no banco após cada busca
- Seguir o padrão FastAPI + SQLAlchemy de commit/rollback no lifecycle da session

**Non-Goals:**
- Não alterar modelos, repositórios, serviços ou endpoints
- Não adicionar novas dependências
- Não mudar o schema do banco

## Decisions

**Commit no `get_db()` em vez de nos repositórios**
- Repositórios não devem saber sobre transaction boundaries
- O padrão é: a camada que gerencia o lifecycle da session (dependência FastAPI) faz o commit
- Alternativa rejeitada: chamar `db.commit()` em cada repositório — acoplamento errado e inconsistente com os demais repositórios

**Rollback automático em exceções**
- Se qualquer operação na request falhar, a transação inteira deve ser revertida (incluindo o audit log)
- O `finally` com `db.close()` garante cleanup mesmo sem rollback explícito, mas o padrão explícito é mais seguro

## Risks / Trade-offs

- Se houver outras operações de escrita junto com a auditoria na mesma request, o commit vai persistir tudo — isso é o comportamento correto (atomicidade da request)
- Nenhum risco de migration ou deploy — mudança restrita a uma função