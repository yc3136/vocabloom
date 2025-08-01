#!/usr/bin/env python3
"""
Migration script to add target_language column to existing flashcards.
Run this script to update existing flashcards with a default target language.
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/vocabloom")

def run_migration():
    """Add target_language column to flashcards table"""
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # Check if column already exists
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'flashcards' AND column_name = 'target_language'
        """))
        
        if result.fetchone():
            print("target_language column already exists. Skipping migration.")
            return
        
        # Add the column
        print("Adding target_language column to flashcards table...")
        conn.execute(text("""
            ALTER TABLE flashcards 
            ADD COLUMN target_language VARCHAR(50) DEFAULT 'English'
        """))
        
        # Update existing records with a default value
        print("Updating existing flashcards with default target language...")
        conn.execute(text("""
            UPDATE flashcards 
            SET target_language = 'English' 
            WHERE target_language IS NULL
        """))
        
        # Make the column NOT NULL
        print("Making target_language column NOT NULL...")
        conn.execute(text("""
            ALTER TABLE flashcards 
            ALTER COLUMN target_language SET NOT NULL
        """))
        
        conn.commit()
        print("Migration completed successfully!")

if __name__ == "__main__":
    run_migration() 