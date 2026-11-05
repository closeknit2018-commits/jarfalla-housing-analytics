SELECT
    table_name,
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_schema = 'raw'
  AND table_name IN (
      'scb_municipality_population',
      'scb_deso_population'
  )
ORDER BY table_name, ordinal_position;


-- check constraint
SELECT
    conrelid::regclass AS table_name,
    conname AS constraint_name,
    contype AS constraint_type,
    pg_get_constraintdef(oid) AS definition
FROM pg_constraint
WHERE connamespace = 'raw'::regnamespace
  AND conrelid IN (
      'raw.scb_municipality_population'::regclass,
      'raw.scb_deso_population'::regclass
  )
ORDER BY table_name, conname;
