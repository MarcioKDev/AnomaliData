PRAGMA foreign_keys = ON;

BEGIN IMMEDIATE;

ALTER TABLE alert
    RENAME COLUMN price_deviation_percent_decimal TO deviation_percent_decimal;

ALTER TABLE alert
    ADD COLUMN analyzed_column TEXT NOT NULL DEFAULT 'preco_unitario'
    CHECK (analyzed_column IN ('preco_unitario', 'quantidade'));

INSERT OR IGNORE INTO schema_version (version, applied_at)
VALUES (2, CURRENT_TIMESTAMP);

COMMIT;
