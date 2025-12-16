-- Migration: Create login history table
-- Description: Optional table to track user login history
-- Date: 2025-12-15

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
