 # Manual Supabase Schema Update Instructions for Lead Model Changes

The following fields have been added to the Lead model in `lead.py`:

- `risk_score` (Float): Represents the lead’s risk level (0.0 = no risk, 1.0 = max risk)
- `projected_ltv` (Float): Predicted lifetime value of the lead in USD
- `relationship_map` (JSON or Text): JSON structure, e.g., `{ "connections": ["lead_id1", "lead_id2", ...] }`

## To update your Supabase table schema:

1. **Navigate to your Supabase project dashboard.**
2. **Go to the "Table Editor" and select the `leads` table.**
3. **Add the following columns:**

| Column Name       | Type   | Nullable | Description                                                      |
|-------------------|--------|----------|------------------------------------------------------------------|
| risk_score        | float8 | Yes      | Represents the lead’s risk level (0.0 = no risk, 1.0 = max risk) |
| projected_ltv     | float8 | Yes      | Predicted lifetime value of the lead in USD                      |
| relationship_map  | jsonb  | Yes      | JSON structure: {"connections": ["lead_id1", ...]}               |

4. **Save the changes.**

- If your Supabase instance does not support `jsonb`, use a `text` column and store JSON as a string.

## Notes

- No data migration is needed for existing rows; new fields will be NULL by default.
- If you later add Alembic or another migration tool, generate a migration to match these changes.
