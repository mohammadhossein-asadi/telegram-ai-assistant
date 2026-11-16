-- =====================================================================
-- DEV ONLY — optional demo rows for local exploration.
-- Never run this against a production database.
-- No secrets, no real Telegram ids (900000001 is reserved for demos),
-- no personal data. Idempotent: safe to run repeatedly.
--
--   sqlite3 ./data/bot.db < artifacts/database/seed.sql
-- =====================================================================

INSERT OR IGNORE INTO users
    (id, telegram_id, username, first_name, language, is_blocked, last_seen_at, created_at, updated_at)
VALUES
    (1, 900000001, 'demo_user', 'Demo', 'en', 0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

INSERT OR IGNORE INTO user_settings
    (id, user_id, personality, style, tone, creativity, memory_enabled, response_language,
     emoji_enabled, custom_instructions, model, provider, current_conversation_id,
     default_persona_id, auto_routing, created_at, updated_at)
VALUES
    (1, 1, 'helpful', 'concise', 'neutral', 'balanced', 1, 'auto',
     1, NULL, NULL, NULL, NULL, NULL, 0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

INSERT OR IGNORE INTO conversations
    (id, user_id, title, is_archived, is_pinned, summary, persona_id, model, created_at, updated_at)
VALUES
    (1, 1, 'Demo conversation', 0, 1, NULL, NULL, NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    (2, 1, 'Second demo chat', 0, 0, NULL, NULL, NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

INSERT OR IGNORE INTO messages (id, conversation_id, role, content, created_at, updated_at)
VALUES
    (1, 1, 'user', 'What can you do?', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    (2, 1, 'assistant', 'I can chat, summarise, translate, write and explain code. Try /menu.', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

INSERT OR IGNORE INTO personas
    (id, user_id, name, instructions, emoji, is_default, created_at, updated_at)
VALUES
    (1, 1, 'Code Reviewer',
     'You review code. Point out bugs first, then style. Be concise and specific.',
     '🧑‍💻', 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

INSERT OR IGNORE INTO prompts
    (id, user_id, title, body, category, created_at, updated_at)
VALUES
    (1, 1, 'Explain simply',
     'Explain {topic} as if I were a beginner. Use one short example.',
     'learning', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

INSERT OR IGNORE INTO user_memory
    (id, user_id, "key", value, created_at, updated_at)
VALUES
    (1, 1, 'name', 'Demo', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    (2, 1, 'preferred_language', 'English', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

UPDATE user_settings SET default_persona_id = 1, current_conversation_id = 1 WHERE user_id = 1;
