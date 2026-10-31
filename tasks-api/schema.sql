-- The two tables. "IF NOT EXISTS" makes this safe to run on every startup:
-- tables that already exist are left as they are.

CREATE TABLE IF NOT EXISTS problems (
    id         INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    title      VARCHAR(120) NOT NULL CHECK (title <> ''),
    platform   TEXT NOT NULL
               CHECK (platform IN ('leetcode', 'codesignal', 'hackerrank', 'other')),
    topic      VARCHAR(40) NOT NULL CHECK (topic <> ''),
    difficulty TEXT NOT NULL CHECK (difficulty IN ('easy', 'medium', 'hard')),
    -- the same title can't exist twice on the same platform
    UNIQUE (title, platform)
);

CREATE TABLE IF NOT EXISTS attempts (
    id         INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    -- ON DELETE CASCADE: deleting a problem deletes its attempts too
    problem_id INTEGER NOT NULL REFERENCES problems (id) ON DELETE CASCADE,
    minutes    INTEGER NOT NULL CHECK (minutes > 0 AND minutes <= 600),
    confidence INTEGER NOT NULL CHECK (confidence BETWEEN 1 AND 5),
    solved     BOOLEAN NOT NULL,
    notes      VARCHAR(500) NOT NULL DEFAULT '',
    created_at DATE NOT NULL DEFAULT CURRENT_DATE
);
