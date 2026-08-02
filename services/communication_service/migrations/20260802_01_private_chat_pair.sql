-- Safe, reversible schema preparation for canonical private-chat pairs.
-- Existing duplicate chats are intentionally untouched: legacy rows remain
-- nullable and available for manual archival.
ALTER TABLE chats ADD COLUMN IF NOT EXISTS participant_one_id INTEGER;
ALTER TABLE chats ADD COLUMN IF NOT EXISTS participant_two_id INTEGER;

CREATE UNIQUE INDEX IF NOT EXISTS uq_private_chat_canonical_pair
    ON chats (participant_one_id, participant_two_id)
    WHERE chat_type = 'PRIVATE'
      AND participant_one_id IS NOT NULL
      AND participant_two_id IS NOT NULL;

-- Down migration (manual/offline):
-- DROP INDEX IF EXISTS uq_private_chat_canonical_pair;
-- ALTER TABLE chats DROP COLUMN IF EXISTS participant_one_id;
-- ALTER TABLE chats DROP COLUMN IF EXISTS participant_two_id;
