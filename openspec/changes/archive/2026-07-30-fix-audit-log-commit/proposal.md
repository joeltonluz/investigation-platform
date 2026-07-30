## Why

O registro de auditoria (`search_audit_log`) nunca é persistido no banco porque a função `get_db()` em `session.py` não chama `db.commit()` antes de fechar a sessão. Toda auditoria de busca é perdida silenciosamente — o sistema não gera trilha de auditoria, violando um requisito central da plataforma.

## What Changes

- Adicionar `db.commit()` no `try` block de `get_db()` em `session.py`
- Adicionar `db.rollback()` no `except` para tratar falhas
- Garantir que testes existentes ainda passem (nenhuma API nova, apenas correção de comportamento)
- Nenhuma mudança de API, banco, ou dependências

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

Nenhuma. A correção é puramente de infraestrutura (session lifecycle), não altera requisitos de domínio.

## Impact

- **`src/app/db/session.py`**: único arquivo modificado
- Nenhuma mudança em API, banco, modelos, dependências ou testes