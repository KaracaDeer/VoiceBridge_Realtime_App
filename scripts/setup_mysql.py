#!/usr/bin/env python3
"""
MySQL Database Setup Script
"""
import mysql.connector
from mysql.connector import Error

from config import settings


def setup_mysql_database():
    """Setup MySQL database for VoiceBridge"""
    print("🔧 Setting up MySQL database...")

    try:
        # Try to connect using password from .env first
        connection = mysql.connector.connect(host="localhost", user="root", password=settings.mysql_password)

        if connection.is_connected():
            print("✅ Connected to MySQL server")

            # Create database
            connection.execute("CREATE DATABASE IF NOT EXISTS voicebridge")
            print("✅ Database 'voicebridge' created")

            # Use the database
            connection.execute("USE voicebridge")

            # Create users table
            create_users_table = """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                first_name VARCHAR(50),
                last_name VARCHAR(50),
                language_preference VARCHAR(10) DEFAULT 'en',
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
            """

            connection.execute(create_users_table)
            print("✅ Users table created")

            # Create conversations table
            create_conversations_table = """
            CREATE TABLE IF NOT EXISTS conversations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                session_id VARCHAR(100) UNIQUE NOT NULL,
                title VARCHAR(200),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """

            connection.execute(create_conversations_table)
            print("✅ Conversations table created")

            # Create transcriptions table
            create_transcriptions_table = """
            CREATE TABLE IF NOT EXISTS transcriptions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                session_id VARCHAR(100),
                audio_duration FLOAT,
                audio_size_bytes INT,
                sample_rate INT,
                original_text TEXT,
                processed_text TEXT,
                confidence_score FLOAT,
                language_detected VARCHAR(10),
                model_used VARCHAR(100),
                preprocessing_used BOOLEAN DEFAULT FALSE,
                processing_time FLOAT,
                features JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """

            connection.execute(create_transcriptions_table)
            print("✅ Transcriptions table created")

            print("🎉 MySQL database setup completed successfully!")
            return True

    except Error as e:
        print(f"❌ MySQL Error: {e}")

        # Try without password
        try:
            connection = mysql.connector.connect(host="localhost", user="root")

            if connection.is_connected():
                print("✅ Connected to MySQL server (no password)")
                # Update config to use no password
                print(
                    "💡 Update your .env file with: MYSQL_CONNECTION_STRING=mysql+mysqlconnector://root:@localhost:3306/voicebridge"
                )
                return True

        except Error as e2:
            print(f"❌ MySQL Error (no password): {e2}")
            print("💡 Please check your MySQL installation and password")
            return False

    finally:
        if "connection" in locals() and connection.is_connected():
            connection.close()
            print("🔌 MySQL connection closed")


if __name__ == "__main__":
    setup_mysql_database()
