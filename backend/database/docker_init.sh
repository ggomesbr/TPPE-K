#!/bin/bash
# Docker entrypoint script for database initialization
# Ensures database tables are created and populated

echo "🐳 Starting Database Initialization Container..."

# Wait for MySQL to be fully ready (additional safety check)
echo "⏳ Waiting for MySQL to be fully ready..."
sleep 10

# Create tables first (using standalone script)
echo "🔧 Creating database tables..."
python /app/database/create_tables_standalone.py

# Check if table creation was successful
if [ $? -eq 0 ]; then
    echo "✅ Database tables created successfully!"
    
    # Now populate the database
    echo "🌱 Populating database with sample data..."
    python /app/database/populate_db.py --auto
    
    if [ $? -eq 0 ]; then
        echo "🎉 Database initialization completed successfully!"
        exit 0
    else
        echo "❌ Database population failed!"
        exit 1
    fi
else
    echo "❌ Database table creation failed!"
    exit 1
fi
