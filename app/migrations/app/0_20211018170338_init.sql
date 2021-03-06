-- upgrade --
CREATE TABLE IF NOT EXISTS "epoch" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "start_datetime" TIMESTAMPTZ NOT NULL,
    "end_datetime" TIMESTAMPTZ NOT NULL,
    "apy" DECIMAL(15,4) NOT NULL  DEFAULT 0.025000000000000001387778780781445675529539585113525390625,
    "portfolio_percentage" DECIMAL(15,4) NOT NULL  DEFAULT 0.200000000000000011102230246251565404236316680908203125,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE "epoch" IS 'Staking Epoch table';
CREATE TABLE IF NOT EXISTS "user" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "balance" DECIMAL(15,4) NOT NULL  DEFAULT 0,
    "is_staking" BOOL NOT NULL  DEFAULT False,
    "staking_started_date" TIMESTAMPTZ,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE "user" IS 'User table';
CREATE TABLE IF NOT EXISTS "user_epoch" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "epoch_lowest_balance" DECIMAL(15,4) NOT NULL  DEFAULT 0,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "epoch_id" INT NOT NULL REFERENCES "epoch" ("id") ON DELETE CASCADE,
    "user_id" BIGINT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
COMMENT ON TABLE "user_epoch" IS 'Many to many relationship between user and epoch';
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(20) NOT NULL,
    "content" JSONB NOT NULL
);
CREATE TABLE IF NOT EXISTS "user_epoch" (
    "epoch_id" INT NOT NULL REFERENCES "epoch" ("id") ON DELETE CASCADE,
    "user_id" BIGINT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
