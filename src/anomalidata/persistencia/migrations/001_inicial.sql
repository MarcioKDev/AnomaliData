PRAGMA foreign_keys = ON;

BEGIN IMMEDIATE;

CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS analysis (
    id TEXT PRIMARY KEY,
    dataset_identification TEXT NOT NULL,
    numeric_column TEXT NOT NULL,
    threshold_decimal TEXT NOT NULL,
    record_count INTEGER NOT NULL CHECK (record_count >= 0),
    duplicate_count INTEGER NOT NULL DEFAULT 0 CHECK (duplicate_count >= 0),
    duration_seconds REAL NOT NULL CHECK (duration_seconds >= 0),
    executed_at TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    result_summary TEXT NOT NULL,
    CHECK (expires_at > executed_at)
);

CREATE TABLE IF NOT EXISTS analysis_grouping_column (
    analysis_id TEXT NOT NULL REFERENCES analysis(id) ON DELETE CASCADE,
    position INTEGER NOT NULL CHECK (position >= 0),
    column_name TEXT NOT NULL,
    PRIMARY KEY (analysis_id, position),
    UNIQUE (analysis_id, column_name)
);

CREATE TABLE IF NOT EXISTS alert (
    id TEXT PRIMARY KEY,
    analysis_id TEXT NOT NULL REFERENCES analysis(id) ON DELETE CASCADE,
    source_record_id TEXT NOT NULL,
    product_code TEXT NOT NULL,
    supplier TEXT NOT NULL,
    quantity_decimal TEXT NOT NULL,
    unit_price_decimal TEXT NOT NULL,
    purchase_date TEXT NOT NULL,
    reference_value_decimal TEXT NOT NULL,
    score REAL NOT NULL CHECK (score >= 0),
    price_deviation_percent_decimal TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS alert_factor (
    alert_id TEXT NOT NULL REFERENCES alert(id) ON DELETE CASCADE,
    position INTEGER NOT NULL CHECK (position >= 0),
    description TEXT NOT NULL,
    PRIMARY KEY (alert_id, position)
);

CREATE TABLE IF NOT EXISTS alert_review (
    alert_id TEXT PRIMARY KEY REFERENCES alert(id) ON DELETE CASCADE,
    classification TEXT NOT NULL CHECK (
        classification IN ('pendente', 'anomalia_confirmada', 'situacao_justificada')
    ),
    observation TEXT NOT NULL DEFAULT '',
    recorded_at TEXT NOT NULL,
    version INTEGER NOT NULL DEFAULT 1 CHECK (version >= 1)
);

CREATE INDEX IF NOT EXISTS idx_analysis_expires_at
    ON analysis (expires_at);
CREATE INDEX IF NOT EXISTS idx_analysis_executed_at
    ON analysis (executed_at DESC);
CREATE INDEX IF NOT EXISTS idx_alert_analysis_score
    ON alert (analysis_id, score DESC);
CREATE INDEX IF NOT EXISTS idx_alert_product_supplier
    ON alert (product_code, supplier);
CREATE INDEX IF NOT EXISTS idx_alert_review_classification
    ON alert_review (classification);

INSERT OR IGNORE INTO schema_version (version, applied_at)
VALUES (1, CURRENT_TIMESTAMP);

COMMIT;
