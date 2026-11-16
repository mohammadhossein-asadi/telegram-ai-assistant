# Entity-Relationship Diagram

Source of truth: `src/database/models/__init__.py`. Raw Mermaid:
[`artifacts/diagrams/er.mmd`](../../artifacts/diagrams/er.mmd).

## 1. Full diagram

```mermaid
erDiagram
    users ||--|| user_settings : "has"
    users ||--o{ personas : "owns"
    users ||--o{ conversations : "owns"
    users ||--o{ prompts : "owns"
    users ||--o{ user_memory : "owns"
    users ||--o{ usage_logs : "produces"

    conversations ||--o{ messages : "contains"
    conversations }o..|| personas : "persona_id (loose)"

    users {
        int id PK
        bigint telegram_id UK "Telegram account id"
        string username "nullable"
        string first_name "nullable"
        string language "fa | en"
        bool is_blocked
        datetime last_seen_at "nullable, not updated"
        datetime created_at
        datetime updated_at
    }

    user_settings {
        int id PK
        int user_id FK
        string personality "10 presets"
        string style "6 presets"
        string tone "5 presets"
        string creativity "low | balanced | high"
        bool memory_enabled
        string response_language "auto | fa | en"
        bool emoji_enabled
        text custom_instructions "nullable"
        string model "nullable"
        string provider "nullable"
        int current_conversation_id "nullable, loose"
        int default_persona_id "nullable, loose"
        bool auto_routing
        datetime created_at
        datetime updated_at
    }

    personas {
        int id PK
        int user_id FK
        string name "unique per user"
        text instructions
        string emoji
        bool is_default
        datetime created_at
        datetime updated_at
    }

    conversations {
        int id PK
        int user_id FK
        string title
        bool is_archived
        bool is_pinned
        text summary "nullable"
        int persona_id "nullable, loose"
        string model "nullable"
        datetime created_at
        datetime updated_at
    }

    messages {
        int id PK
        int conversation_id FK
        string role "system | user | assistant"
        text content
        datetime created_at
        datetime updated_at
    }

    prompts {
        int id PK
        int user_id FK
        string title
        text body
        string category
        datetime created_at
        datetime updated_at
    }

    user_memory {
        int id PK
        int user_id FK
        string key "unique per user"
        text value
        datetime created_at
        datetime updated_at
    }

    ai_providers {
        int id PK
        string name UK
        string base_url
        string model
        text api_key "plaintext at rest"
        bool is_active
        string capabilities "csv task classes"
        datetime created_at
        datetime updated_at
    }

    usage_logs {
        int id PK
        int user_id FK "nullable, SET NULL"
        string action "chat | summarize | ..."
        string provider "nullable"
        string model "nullable"
        bool success
        text error "nullable"
        int latency_ms "nullable"
        int prompt_tokens
        int completion_tokens
        datetime created_at
        datetime updated_at
    }

    schema_version {
        int version PK
        text description
        timestamp applied_at
    }
```

> `ai_providers` and `schema_version` have no relationships and are omitted from the
> relation arrows above for readability; they are present in the entity list.

## 2. Cardinality notes

| Relation | Cardinality | Delete behaviour |
| --- | --- | --- |
| users → user_settings | 1:1 | ORM cascade; row recreated on next need |
| users → personas | 1:N | CASCADE (ORM + `ondelete`) |
| users → conversations | 1:N | CASCADE; messages follow |
| conversations → messages | 1:N | CASCADE |
| users → prompts | 1:N | CASCADE |
| users → user_memory | 1:N | CASCADE |
| users → usage_logs | 1:N | `SET NULL` — audit rows survive user deletion |
| conversations → personas | N:0..1 | **no FK**; dangling id is ignored at read time |

## 3. Ownership map (who may read what)

```mermaid
flowchart LR
    U[user] --> S[own user_settings]
    U --> P[own personas]
    U --> C[own conversations]
    C --> M[their messages]
    U --> PR[own prompts]
    U --> MM[own memory]
    A[admin] --> AGG[aggregates: counts, tokens, user list]
    A -.->|no read path| M
```

Admins can block users and see aggregates; there is **no admin path to read another
user's messages**.

## 4. Invariants

1. Every `messages.conversation_id` resolves to a conversation owned by the same user
   as the message's author (enforced by always fetching the conversation with
   `user_id`).
2. `users.telegram_id` is unique.
3. `personas (user_id, name)` is unique.
4. `user_memory (user_id, key)` is unique.
5. `ai_providers.name` is unique.
6. `usage_logs` rows are never updated except by nothing — treat them as immutable.

## 5. Index summary

| Index | Table | Purpose |
| --- | --- | --- |
| `ix_users_telegram_id` (unique) | users | identity lookup on every update |
| `ix_user_settings_user_id` (unique) | user_settings | 1:1 guarantee + lookup |
| `ix_conversations_user_id` | conversations | list/ownership |
| `ix_messages_conversation_id` | messages | history load |
| `ix_personas_user_id` | personas | list |
| `ix_prompts_user_id` | prompts | list |
| `ix_user_memory_user_id` | user_memory | prompt injection |
| `ix_usage_logs_user_id` | usage_logs | quota count, stats |
| implicit PK index | all | `id` lookups, ordering |
