-- Migration: Add role column to users table
-- Description: Adds role column to support teacher and student roles
-- Date: 2025-12-16

-- Add role column to users table
ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR(20) NOT NULL DEFAULT 'student';

-- Add constraint to ensure only valid roles are used
ALTER TABLE users ADD CONSTRAINT check_user_role 
    CHECK (role IN ('teacher', 'student'));

-- Add teacher_id column for student-teacher relationship
ALTER TABLE users ADD COLUMN IF NOT EXISTS teacher_id UUID REFERENCES users(id) ON DELETE SET NULL;

-- Add constraint to ensure only students can have a teacher_id
ALTER TABLE users ADD CONSTRAINT check_student_teacher 
    CHECK (
        (role = 'student' AND teacher_id IS NOT NULL) OR 
        (role = 'teacher' AND teacher_id IS NULL)
    );

-- Create index on role for faster role-based queries
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

-- Create index on teacher_id for faster teacher-student queries
CREATE INDEX IF NOT EXISTS idx_users_teacher_id ON users(teacher_id);

-- Add comments
COMMENT ON COLUMN users.role IS 'User role: teacher or student';
COMMENT ON COLUMN users.teacher_id IS 'For students only - references the teacher user';
