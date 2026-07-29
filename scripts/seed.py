"""Seed the database with 10 rows per domain table."""

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.config import Settings
from app.db.base import Base
from app.db.models import (
    AnalyticsReport,
    CaseManagerCase,
    CaseStatus,
    EntityType,
    InvestigatorEntity,
)

SAMPLE_ENTITIES = [
    {
        "type": EntityType.person,
        "name": "João Silva",
        "data": {"age": 42, "city": "São Paulo"},
    },
    {
        "type": EntityType.person,
        "name": "Maria Souza",
        "data": {"age": 35, "city": "Rio de Janeiro"},
    },
    {
        "type": EntityType.company,
        "name": "TechBiz Ltda",
        "data": {"cnpj": "12.345.678/0001-90", "employees": 200},
    },
    {
        "type": EntityType.company,
        "name": "DataCorp S.A.",
        "data": {"cnpj": "98.765.432/0001-10", "employees": 50},
    },
    {
        "type": EntityType.transaction,
        "name": "Transferência #001",
        "data": {"amount": 150000, "currency": "BRL"},
    },
    {
        "type": EntityType.transaction,
        "name": "Transferência #002",
        "data": {"amount": 25000, "currency": "USD"},
    },
    {
        "type": EntityType.document,
        "name": "Contrato Social",
        "data": {"pages": 15, "notary": "1º Ofício"},
    },
    {
        "type": EntityType.document,
        "name": "Declaração IRPF",
        "data": {"year": 2025, "income": 350000},
    },
    {
        "type": EntityType.person,
        "name": "Carlos Pereira",
        "data": {"age": 28, "city": "Belo Horizonte"},
    },
    {
        "type": EntityType.company,
        "name": "Alpha Serviços",
        "data": {"cnpj": "11.222.333/0001-44", "employees": 15},
    },
]

SAMPLE_REPORTS = [
    {
        "title": "Análise de Fraude Q1",
        "content": "Relatório detalhado sobre tentativas de fraude no Q1.",
    },
    {
        "title": "Panorama de Compliance",
        "content": "Avaliação de conformidade regulatória dos departamentos.",
    },
    {
        "title": "Relatório de Due Diligence",
        "content": "Investigação de antecedentes de parceiros comerciais.",
    },
    {
        "title": "Mapeamento de Riscos",
        "content": "Identificação de riscos operacionais e financeiros.",
    },
    {
        "title": "Análise de Fluxo Financeiro",
        "content": "Rastreamento de transações suspeitas entre contas.",
    },
    {
        "title": "Relatório de Inteligência",
        "content": "Compilado de informações de fontes abertas.",
    },
    {
        "title": "Auditoria de Contratos",
        "content": "Revisão de contratos com fornecedores críticos.",
    },
    {
        "title": "Investigação Interna",
        "content": "Apuração de denúncia recebida pelo canal de ética.",
    },
    {
        "title": "Análise de Redes",
        "content": "Mapeamento de relacionamentos entre entidades.",
    },
    {
        "title": "Relatório Executivo",
        "content": "Sumário executivo das investigações em andamento.",
    },
]

SAMPLE_CASES = [
    {
        "title": "Caso Operação Lavagem",
        "assigned_to": "agent-001",
        "status": CaseStatus.open,
    },
    {
        "title": "Investigação Contrato X",
        "assigned_to": "agent-001",
        "status": CaseStatus.in_progress,
    },
    {
        "title": "Due Diligence Parceiro Y",
        "assigned_to": "agent-002",
        "status": CaseStatus.open,
    },
    {
        "title": "Apuração Denúncia Z",
        "assigned_to": "agent-002",
        "status": CaseStatus.closed,
    },
    {
        "title": "Monitoramento Fornecedor W",
        "assigned_to": "agent-003",
        "status": CaseStatus.in_progress,
    },
    {
        "title": "Análise Concorrência",
        "assigned_to": "agent-001",
        "status": CaseStatus.open,
    },
    {
        "title": "Investigação Patrimonial",
        "assigned_to": "agent-003",
        "status": CaseStatus.open,
    },
    {
        "title": "Revisão de Licitações",
        "assigned_to": "agent-002",
        "status": CaseStatus.in_progress,
    },
    {
        "title": "Caso de Integridade",
        "assigned_to": "agent-001",
        "status": CaseStatus.closed,
    },
    {
        "title": "Auditoria Contratos TI",
        "assigned_to": "agent-003",
        "status": CaseStatus.open,
    },
]


def seed() -> None:
    engine = create_engine(Settings().database_url)
    Base.metadata.create_all(bind=engine)
    with Session(bind=engine) as session:
        for data in SAMPLE_ENTITIES:
            session.add(InvestigatorEntity(**data))
        for data in SAMPLE_REPORTS:
            session.add(AnalyticsReport(**data))
        for data in SAMPLE_CASES:
            session.add(CaseManagerCase(**data))
        session.commit()
    print("Seed complete: 10 entities, 10 reports, 10 cases inserted.")


if __name__ == "__main__":
    seed()
