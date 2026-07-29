from dataclasses import dataclass, field


@dataclass
class User:
    user_id: str
    app_client_id: str
    permissions: set[str] = field(default_factory=set)
