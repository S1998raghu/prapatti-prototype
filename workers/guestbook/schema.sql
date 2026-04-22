CREATE TABLE IF NOT EXISTS entries (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author TEXT NOT NULL,
  email TEXT,
  location TEXT,
  message TEXT NOT NULL,
  timestamp TEXT NOT NULL,
  approved INTEGER DEFAULT 0,
  reply TEXT
);

CREATE INDEX IF NOT EXISTS idx_approved ON entries(approved);
CREATE INDEX IF NOT EXISTS idx_timestamp ON entries(timestamp);
