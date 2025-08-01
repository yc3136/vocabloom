#!/bin/bash

# Production Database Migration Script
# This script adds the target_language column to the flashcards table

set -e

echo "🚀 Starting production database migration..."

# Get database password from Secret Manager
echo "📋 Getting database password from Secret Manager..."
DB_PASSWORD=$(gcloud secrets versions access latest --secret="database-password")

if [ -z "$DB_PASSWORD" ]; then
    echo "❌ Error: Could not retrieve database password from Secret Manager"
    exit 1
fi

echo "✅ Database password retrieved successfully"

# Create SQL migration file
echo "📝 Creating migration SQL file..."
cat > /tmp/migration.sql << 'EOF'
-- Check if target_language column exists
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'flashcards' AND column_name = 'target_language'
    ) THEN
        -- Add target_language column
        ALTER TABLE flashcards ADD COLUMN target_language VARCHAR(50) DEFAULT 'English';
        
        -- Update existing records
        UPDATE flashcards SET target_language = 'English' WHERE target_language IS NULL;
        
        -- Make column NOT NULL
        ALTER TABLE flashcards ALTER COLUMN target_language SET NOT NULL;
        
        RAISE NOTICE 'target_language column added successfully';
    ELSE
        RAISE NOTICE 'target_language column already exists';
    END IF;
END $$;

-- Remove template column if it exists (no longer used)
DO $$
BEGIN
    IF EXISTS (
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'flashcards' AND column_name = 'template'
    ) THEN
        -- Remove template column
        ALTER TABLE flashcards DROP COLUMN template;
        RAISE NOTICE 'template column removed successfully';
    ELSE
        RAISE NOTICE 'template column does not exist';
    END IF;
END $$;

-- Update example_sentences to be non-nullable with default
DO $$
BEGIN
    -- Update existing NULL values to empty array
    UPDATE flashcards SET example_sentences = '[]'::jsonb WHERE example_sentences IS NULL;
    
    -- Make column NOT NULL
    ALTER TABLE flashcards ALTER COLUMN example_sentences SET NOT NULL;
    
    -- Set default value
    ALTER TABLE flashcards ALTER COLUMN example_sentences SET DEFAULT '[]'::jsonb;
    
    RAISE NOTICE 'example_sentences column updated successfully';
END $$;

-- Update colors to be non-nullable with default
DO $$
BEGIN
    -- Update existing NULL values to default colors
    UPDATE flashcards SET colors = '{"primary": "#6690ff", "secondary": "#64748b"}'::jsonb WHERE colors IS NULL;
    
    -- Make column NOT NULL
    ALTER TABLE flashcards ALTER COLUMN colors SET NOT NULL;
    
    -- Set default value
    ALTER TABLE flashcards ALTER COLUMN colors SET DEFAULT '{"primary": "#6690ff", "secondary": "#64748b"}'::jsonb;
    
    RAISE NOTICE 'colors column updated successfully';
END $$;
EOF

echo "✅ Migration SQL file created"

# Run the migration using gcloud sql connect
echo "🔧 Running database migration..."
echo "$DB_PASSWORD" | gcloud sql connect vocabloom-db --user=vocabloom-app --database=vocabloom --quiet < /tmp/migration.sql

if [ $? -eq 0 ]; then
    echo "✅ Migration completed successfully!"
else
    echo "❌ Migration failed!"
    exit 1
fi

# Clean up
rm -f /tmp/migration.sql

echo "🎉 Production database migration completed!" 