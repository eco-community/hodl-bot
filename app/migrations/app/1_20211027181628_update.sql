-- upgrade --
ALTER TABLE "epoch" ALTER COLUMN "apy" SET DEFAULT 0.05;
-- downgrade --
ALTER TABLE "epoch" ALTER COLUMN "apy" SET DEFAULT 0.025;
