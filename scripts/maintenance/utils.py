#!/usr/bin/env python3
"""
Shared utility functions for TechZe project
"""

import os
import shutil
from typing import List, Dict, Any, Optional


class Logger:
    """Simple logging utility with formatted output"""
    
    @staticmethod
    def header(title: str) -> None:
        """Print formatted header"""
        print("\n" + "="*60)
        print(f"🔧 {title}")
        print("="*60)
    
    @staticmethod
    def step(step: str) -> None:
        """Print formatted step"""
        print(f"\n📋 {step}")
        print("-" * 40)
    
    @staticmethod
    def success(message: str) -> None:
        """Print success message"""
        print(f"   ✅ {message}")
    
    @staticmethod
    def warning(message: str) -> None:
        """Print warning message"""
        print(f"   ⚠️ {message}")
    
    @staticmethod
    def error(message: str) -> None:
        """Print error message"""
        print(f"   ❌ {message}")
    
    @staticmethod
    def info(message: str) -> None:
        """Print info message"""
        print(f"   📝 {message}")


class FileManager:
    """File and directory management utilities"""
    
    @staticmethod
    def safe_remove_file(file_path: str) -> bool:
        """Safely remove a file"""
        try:
            if os.path.exists(file_path) and os.path.isfile(file_path):
                os.remove(file_path)
                Logger.success(f"Removed file: {file_path}")
                return True
            else:
                Logger.warning(f"File not found: {file_path}")
                return False
        except Exception as e:
            Logger.error(f"Error removing file {file_path}: {str(e)}")
            return False
    
    @staticmethod
    def safe_remove_directory(dir_path: str) -> bool:
        """Safely remove a directory"""
        try:
            if os.path.exists(dir_path) and os.path.isdir(dir_path):
                shutil.rmtree(dir_path)
                Logger.success(f"Removed directory: {dir_path}")
                return True
            else:
                Logger.warning(f"Directory not found: {dir_path}")
                return False
        except Exception as e:
            Logger.error(f"Error removing directory {dir_path}: {str(e)}")
            return False
    
    @staticmethod
    def ensure_directory(dir_path: str) -> bool:
        """Ensure directory exists, create if not"""
        try:
            os.makedirs(dir_path, exist_ok=True)
            return True
        except Exception as e:
            Logger.error(f"Error creating directory {dir_path}: {str(e)}")
            return False
    
    @staticmethod
    def write_file(file_path: str, content: str, encoding: str = 'utf-8') -> bool:
        """Write content to file safely"""
        try:
            # Ensure parent directory exists
            parent_dir = os.path.dirname(file_path)
            if parent_dir:
                FileManager.ensure_directory(parent_dir)
            
            with open(file_path, 'w', encoding=encoding) as f:
                f.write(content)
            Logger.success(f"File written: {file_path}")
            return True
        except Exception as e:
            Logger.error(f"Error writing file {file_path}: {str(e)}")
            return False
    
    @staticmethod
    def read_file(file_path: str, encoding: str = 'utf-8') -> Optional[str]:
        """Read file content safely"""
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except Exception as e:
            Logger.error(f"Error reading file {file_path}: {str(e)}")
            return None


class ValidationHelper:
    """Validation utilities"""
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate URL format"""
        return url.startswith(('http://', 'https://'))
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Basic email validation"""
        return '@' in email and '.' in email.split('@')[1]
    
    @staticmethod
    def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> List[str]:
        """Validate required fields in data dictionary"""
        missing_fields = []
        for field in required_fields:
            if field not in data or not data[field]:
                missing_fields.append(field)
        return missing_fields


class ProgressTracker:
    """Track progress of operations"""
    
    def __init__(self, total: int, description: str = "Processing"):
        self.total = total
        self.current = 0
        self.description = description
        self.successes = 0
        self.failures = 0
    
    def update(self, success: bool = True, message: str = "") -> None:
        """Update progress"""
        self.current += 1
        if success:
            self.successes += 1
            if message:
                Logger.success(f"[{self.current}/{self.total}] {message}")
        else:
            self.failures += 1
            if message:
                Logger.error(f"[{self.current}/{self.total}] {message}")
    
    def summary(self) -> Dict[str, int]:
        """Get progress summary"""
        return {
            'total': self.total,
            'completed': self.current,
            'successes': self.successes,
            'failures': self.failures,
            'remaining': self.total - self.current
        }
    
    def print_summary(self) -> None:
        """Print progress summary"""
        summary = self.summary()
        Logger.info(f"{self.description} Summary:")
        Logger.info(f"Total: {summary['total']}")
        Logger.info(f"Completed: {summary['completed']}")
        Logger.info(f"Successes: {summary['successes']}")
        Logger.info(f"Failures: {summary['failures']}")
        
        if summary['failures'] == 0:
            Logger.success("All operations completed successfully!")
        else:
            Logger.warning(f"{summary['failures']} operations failed")


def confirm_action(message: str, default: bool = False) -> bool:
    """Ask user for confirmation"""
    suffix = " (Y/n)" if default else " (y/N)"
    response = input(f"📋 {message}{suffix}: ").lower().strip()
    
    if not response:
        return default
    
    return response in ['y', 'yes', 's', 'sim']


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"


def get_project_files(extensions: List[str] = None, exclude_dirs: List[str] = None) -> List[str]:
    """Get list of project files with optional filtering"""
    if extensions is None:
        extensions = ['.py', '.js', '.ts', '.tsx', '.sql', '.md']
    
    if exclude_dirs is None:
        exclude_dirs = ['.git', 'node_modules', '__pycache__', '.pytest_cache', 'dist', 'build']
    
    project_files = []
    
    for root, dirs, files in os.walk('.'):
        # Remove excluded directories from dirs list to prevent walking into them
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                project_files.append(os.path.join(root, file))
    
    return project_files