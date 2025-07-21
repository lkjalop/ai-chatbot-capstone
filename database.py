"""
Database manager for Neon Postgres
Handles connections, schemas, and database operations
"""

import asyncpg
import json
import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, List, Optional, Any
import os
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages Neon Postgres database connections and operations"""
    
    def __init__(self):
        self.pool = None
        self.database_url = os.getenv("NEON_DATABASE_URL")
        if not self.database_url:
            raise ValueError("NEON_DATABASE_URL environment variable is required")
    
    async def initialize(self):
        """Initialize the database connection pool and create tables"""
        try:
            # Create connection pool
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=5,
                max_size=20,
                command_timeout=60,
                server_settings={
                    'application_name': 'bootcamp_chatbot',
                    'timezone': 'UTC'
                }
            )
            
            logger.info("Database connection pool created successfully")
            await self.create_tables()
            logger.info("Database tables verified/created")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    @asynccontextmanager
    async def get_connection(self):
        """Get a database connection from the pool"""
        if not self.pool:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        
        async with self.pool.acquire() as connection:
            yield connection
    
    async def create_tables(self):
        """Create all required database tables"""
        async with self.get_connection() as conn:
            # Enable UUID extension
            await conn.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')
            
            # Users table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    session_id VARCHAR(255) UNIQUE NOT NULL,
                    phone_number VARCHAR(20),
                    email VARCHAR(255),
                    name VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata JSONB DEFAULT '{}'::jsonb,
                    preferences JSONB DEFAULT '{}'::jsonb
                );
            """)
            
            # Conversations table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
                    session_id VARCHAR(255) NOT NULL,
                    message TEXT NOT NULL,
                    response TEXT NOT NULL,
                    agent_type VARCHAR(100) NOT NULL,
                    intent VARCHAR(100),
                    confidence_score FLOAT,
                    response_time_ms INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata JSONB DEFAULT '{}'::jsonb
                );
            """)
            
            logger.info("All database tables created successfully")
    
    async def get_or_create_user(self, session_id: str, user_data: Optional[Dict] = None) -> Dict:
        """Get existing user or create new one"""
        async with self.get_connection() as conn:
            # Try to get existing user
            user = await conn.fetchrow(
                "SELECT * FROM users WHERE session_id = $1", session_id
            )
            
            if user:
                return dict(user)
            
            # Create new user
            user_metadata = user_data or {}
            user_id = await conn.fetchval("""
                INSERT INTO users (session_id, phone_number, email, name, metadata)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING id
            """, 
                session_id,
                user_metadata.get('phone'),
                user_metadata.get('email'),
                user_metadata.get('name'),
                json.dumps(user_metadata)
            )
            
            new_user = await conn.fetchrow("SELECT * FROM users WHERE id = $1", user_id)
            return dict(new_user)