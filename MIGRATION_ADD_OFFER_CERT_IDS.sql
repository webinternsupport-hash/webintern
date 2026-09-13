-- Migration: Add offer_letter_id and certificate_id to applications table
-- Purpose: Store offer letter and certificate IDs in applications for proper tracking

ALTER TABLE applications ADD COLUMN offer_letter_id TEXT;
ALTER TABLE applications ADD COLUMN certificate_id TEXT;
ALTER TABLE applications ADD COLUMN completion_status TEXT DEFAULT 'pending';

-- Add indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_applications_offer_letter ON applications(offer_letter_id);
CREATE INDEX IF NOT EXISTS idx_applications_certificate ON applications(certificate_id);

-- Optional: Set defaults for existing records
-- UPDATE applications SET offer_letter_id = 'WI-OFFER-2026-' || substr(id, 1, 6) WHERE offer_letter_id IS NULL;
-- UPDATE applications SET certificate_id = 'WI-CERT-2026-' || substr(id, 1, 6) WHERE certificate_id IS NULL;
