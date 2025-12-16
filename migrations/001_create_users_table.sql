-- Migration: Create users table
-- Description: Creates the users table with all required fields for registration
-- Date: 2025-12-15

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'student' CHECK (role IN ('teacher', 'student')),
    teacher_id UUID REFERENCES users(id) ON DELETE SET NULL,
    age INTEGER CHECK (age >= 0 AND age <= 150),
    gender VARCHAR(20),
    organization VARCHAR(255),
    profile_image TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT check_student_teacher CHECK (
        (role = 'student' AND teacher_id IS NOT NULL) OR 
        (role = 'teacher' AND teacher_id IS NULL)
    )
);
-- Create index on email for faster lookups
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Create index on role for faster role-based queries
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

-- Create index on teacher_id for faster teacher-student queries
CREATE INDEX IF NOT EXISTS idx_users_teacher_id ON users(teacher_id);

-- Create index on created_at for sorting
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Add comment to table
COMMENT ON TABLE users IS 'Stores user registration and profile information';
