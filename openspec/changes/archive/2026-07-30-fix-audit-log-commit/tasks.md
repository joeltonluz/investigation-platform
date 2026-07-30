## 1. Teste RED

- [x] 1.1 Escrever teste que verifica que `SearchAuditLog` é persistido após uma busca bem-sucedida — esperar falha (sem commit ainda)

## 2. Corrigir `get_db()` em `session.py`

- [x] 2.1 Adicionar `db.commit()` no `try` block de `get_db()` antes do `finally`
- [x] 2.2 Adicionar `except Exception` com `db.rollback()` + `raise`
- [x] 2.3 Rodar `ruff` para garantir formatação e lint limpos

## 3. Verificar GREEN

- [x] 3.