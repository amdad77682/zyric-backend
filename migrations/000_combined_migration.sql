-- Combined Migration Script for Zyric Backend
-- Run this in your Supabase SQL Editor
-- Date: 2025-12-16

-- ============================================
-- Migration 001: Create users table
-- ============================================

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
-- Create index on email for faster lookups
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Create index on role for faster role-based queries
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

-- Create index on teacher_id for faster teacher-student queries
CREATE INDEX IF NOT EXISTS idx_users_teacher_id ON users(teacher_id);

-- Create index on created_at for sorting
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);
-- Create index on role for faster role-based queries
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

-- Create index on created_at for sorting
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

-- ============================================
-- Migration 002: Create password reset tokens table
-- ============================================

-- Create password_reset_tokens table
CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index on user_id for faster lookups
CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_user_id ON password_reset_tokens(user_id);

-- Create index on token for faster lookups
CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_token ON password_reset_tokens(token);

-- Create index on expires_at for cleanup queries
CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_expires_at ON password_reset_tokens(expires_at);

-- Add comment to table
COMMENT ON TABLE password_reset_tokens IS 'Stores password reset tokens for forgot password functionality';

-- ============================================
-- Migration 003: Create login history table
-- ============================================

-- Create login_history table
CREATE TABLE IF NOT EXISTS login_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    login_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    user_agent TEXT,
    success BOOLEAN DEFAULT TRUE
);

-- Create index on user_id for faster lookups
CREATE INDEX IF NOT EXISTS idx_login_history_user_id ON login_history(user_id);

-- Create index on login_at for sorting
CREATE INDEX IF NOT EXISTS idx_login_history_login_at ON login_history(login_at);

-- Add comment to table
COMMENT ON TABLE login_history IS 'Tracks user login attempts and history';

-- ============================================
-- Migration Complete
-- ============================================
