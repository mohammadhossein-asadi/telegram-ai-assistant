-- =====================================================================
-- Telegram AI Assistant — SQLite schema (reference artifact)
-- Produced from the SQLAlchemy metadata in src/database/models/__init__.py
-- (sqlite dialect). SCHEMA_VERSION = 2.
--
-- The application creates this schema automatically at boot via
-- database.create_all() + database.migrations.run_migrations().
-- This file exists for review, manual provisioning and DBAs; it is NOT
-- executed by the app and contains no DROP statements.
-- Keep it in sync with the models when they change.
-- =====================================================================

-- ---------------------------------------------------------------------
-- users: one row per Telegram account
-- ---------------------------------------------------------------------
CREATE TABLE users (
    id            INTEGER NOT NULL,
    telegram_id   INTEGER NOT NULL,
    username      VARCHAR(64),
    first_name    VARCHAR(128),
    language      VARCHAR(5) NOT NULL,
    is_blocked    BOOLEAN NOT NULL,
    last_seen_at  DATETIME,
    created_at    DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at    DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    PRIMARY KEY (id)
);
CREATE UNIQUE INDEX ix_users_telegram_id ON users (telegram_id);

-- ---------------------------------------------------------------------
-- user_settings: one row per user (personality, tone, reply language)
-- ---------------------------------------------------------------------
CREATE TABLE user_settings (
    id                      INTEGER NOT NULL,
    user_id                 INTEGER NOT NULL,
    personality             VARCHAR(32) NOT NULL,
    style                   VARCHAR(32) NOT NULL,
    tone                    VARCHAR(32) NOT NULL,
    creativity              VARCHAR(16) NOT NULL,
    memory_enabled          BOOLEAN NOT NULL,
    response_language       VARCHAR(8) NOT NULL,
    emoji_enabled           BOOLEAN NOT NULL,
    custom_instructions     TEXT,
    model                   VARCHAR(128),
    provider                VARCHAR(64),
    current_conversation_id INTEGER,
    default_persona_id      INTEGER,
    auto_routing            BOOLEAN NOT NULL,
    created_at              DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at              DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);
CREATE UNIQUE INDEX ix_user_settings_user_id ON user_settings (user_id);

-- ---------------------------------------------------------------------
-- personas: user-authored system instructions
-- ---------------------------------------------------------------------
CREATE TABLE personas (
    id           INTEGER NOT NULL,
    user_id      INTEGER NOT NULL,
    name         VARCHAR(80) NOT NULL,
    instructions TEXT NOT NULL,
    emoji        VARCHAR(8) NOT NULL,
    is_default   BOOLEAN NOT NULL,
    created_at   DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at   DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    PRIMARY KEY (id),
    CONSTRAINT uq_persona_name UNIQUE (user_id, name),
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);
CREATE INDEX ix_personas_user_id ON personas (user_id);

-- ---------------------------------------------------------------------
-- conversations: chat threads owned by a user
-- ---------------------------------------------------------------------
CREATE TABLE conversations (
    id          INTEGER NOT NULL,
    user_id     INTEGER NOT NULL,
    title       VARCHAR(120) NOT NULL,
    is_archived BOOLEAN NOT NULL,
    is_pinned   BOOLEAN NOT NULL,
    summary     TEXT,
    persona_id  INTEGER,
    model       VARCHAR(128),
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);
CREATE INDEX ix_conversations_user_id ON conversations (user_id);

-- ---------------------------------------------------------------------
-- messages: role-tagged turns inside a conversation
-- ---------------------------------------------------------------------
CREATE TABLE messages (
    id              INTEGER NOT NULL,
    conversation_id INTEGER NOT NULL,
    role            VARCHAR(16) NOT NULL,          -- system | user | assistant
    content         TEXT NOT NULL,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (conversation_id) REFERENCES conversations (id) ON DELETE CASCADE
);
CREATE INDEX ix_messages_conversation_id ON messages (conversation_id);

-- ---------------------------------------------------------------------
-- prompts: saved reusable prompts (Prompt Studio)
-- ---------------------------------------------------------------------
CREATE TABLE prompts (
    id         INTEGER NOT NULL,
    user_id    INTEGER NOT NULL,
    title      VARCHAR(100) NOT NULL,
    body       TEXT NOT NULL,
    category   VARCHAR(50) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);
CREATE INDEX ix_prompts_user_id ON prompts (user_id);

-- ---------------------------------------------------------------------
-- user_memory: long-term facts injected into the system prompt
-- ---------------------------------------------------------------------
CREATE TABLE user_memory (
    id         INTEGER NOT NULL,
    user_id    INTEGER NOT NULL,
    "key"      VARCHAR(120) NOT NULL,
    value      TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    PRIMARY KEY (id),
    CONSTRAINT uq_user_memory_key UNIQUE (user_id, "key"),
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);
CREATE INDEX ix_user_memory_user_id ON user_memory (user_id);

-- ---------------------------------------------------------------------
-- ai_providers: runtime-added OpenAI-compatible endpoints (admin only).
-- api_key is stored as entered — see ADR-005 (plaintext at rest).
-- ---------------------------------------------------------------------
CREATE TABLE ai_providers (
    id           INTEGER NOT NULL,
    name         VARCHAR(64) NOT NULL,
    base_url     VARCHAR(255) NOT NULL,
    model        VARCHAR(128) NOT NULL,
    api_key      TEXT NOT NULL,
    is_active    BOOLEAN NOT NULL,
    capabilities VARCHAR(255) NOT NULL,            -- comma-separated task classes
    created_at   DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at   DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    PRIMARY KEY (id),
    UNIQUE (name)
);

-- ---------------------------------------------------------------------
-- usage_logs: audit of every AI attempt (also the daily-quota source)
-- ---------------------------------------------------------------------
CREATE TABLE usage_logs (
    id                INTEGER NOT NULL,
    user_id           INTEGER,
    action            VARCHAR(32) NOT NULL,        -- chat | summarize | translate | ...
    provider          VARCHAR(64),
    model             VARCHAR(128),
    success           BOOLEAN NOT NULL,
    error             TEXT,
    latency_ms        INTEGER,
    prompt_tokens     INTEGER NOT NULL,
    completion_tokens INTEGER NOT NULL,
    created_at        DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at        DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL
);
CREATE INDEX ix_usage_logs_user_id ON usage_logs (user_id);

-- ---------------------------------------------------------------------
-- schema_version: migration bookkeeping (managed by run_migrations)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS schema_version (
    version     INTEGER PRIMARY KEY,
    description TEXT,
    applied_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT OR IGNORE INTO schema_version (version, description) VALUES (1, 'initial schema');
INSERT OR IGNORE INTO schema_version (version, description) VALUES (2, 'personas, prompts, tokens, pinning');
