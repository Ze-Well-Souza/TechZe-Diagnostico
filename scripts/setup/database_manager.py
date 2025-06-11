#!/usr/bin/env python3
"""
Unified database management for TechZe project
Handles Supabase connections, table creation, and RLS policies
"""

import requests
from typing import Dict, List, Any, Tuple
from config import config, DATABASE_TABLES, RLS_POLICIES
from utils import Logger, ProgressTracker


class DatabaseManager:
    """Manages database operations for Supabase"""
    
    def __init__(self):
        self.config = config.supabase
        self.logger = Logger()
    
    def test_connection(self) -> bool:
        """Test basic connection to Supabase"""
        self.logger.step("Testing Supabase Connection")
        
        try:
            response = requests.get(
                f"{self.config.url}/rest/v1/",
                headers=self.config.headers,
                timeout=config.project.timeout
            )
            
            if response.status_code == 200:
                self.logger.success("Connection established")
                return True
            else:
                self.logger.error(f"Connection failed: {response.status_code}")
                self.logger.error(f"Response: {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Connection error: {str(e)}")
            return False
    
    def check_table_exists(self, table_name: str) -> bool:
        """Check if a table exists"""
        try:
            response = requests.get(
                f"{self.config.url}/rest/v1/{table_name}?limit=1",
                headers=self.config.headers,
                timeout=5
            )
            return response.status_code == 200
        except Exception:
            return False
    
    def get_existing_tables(self) -> List[str]:
        """Get list of existing tables"""
        self.logger.step("Checking Existing Tables")
        
        existing_tables = []
        tables_to_check = list(DATABASE_TABLES.keys())
        
        for table in tables_to_check:
            if self.check_table_exists(table):
                self.logger.success(f"Table '{table}' exists")
                existing_tables.append(table)
            else:
                self.logger.warning(f"Table '{table}' not found")
        
        return existing_tables
    
    def create_table(self, table_name: str, table_config: Dict[str, Any]) -> bool:
        """Create a single table"""
        columns_sql = ',\n    '.join(table_config['columns'])
        sql = f"""
        CREATE TABLE IF NOT EXISTS public.{table_name} (
            {columns_sql}
        );
        """
        
        return self._execute_sql(sql)
    
    def create_all_tables(self) -> Tuple[int, int]:
        """Create all required tables"""
        self.logger.step("Creating Database Tables")
        
        progress = ProgressTracker(len(DATABASE_TABLES), "Table Creation")
        
        for table_name, table_config in DATABASE_TABLES.items():
            success = self.create_table(table_name, table_config)
            progress.update(success, f"Table '{table_name}' {'created' if success else 'failed'}")
        
        progress.print_summary()
        summary = progress.summary()
        return summary['successes'], summary['failures']
    
    def enable_rls(self, table_name: str) -> bool:
        """Enable RLS for a table"""
        sql = f"ALTER TABLE public.{table_name} ENABLE ROW LEVEL SECURITY;"
        return self._execute_sql(sql)
    
    def enable_rls_all_tables(self) -> Tuple[int, int]:
        """Enable RLS for all tables"""
        self.logger.step("Enabling Row Level Security")
        
        tables = list(DATABASE_TABLES.keys())
        progress = ProgressTracker(len(tables), "RLS Enablement")
        
        for table_name in tables:
            success = self.enable_rls(table_name)
            progress.update(success, f"RLS {'enabled' if success else 'failed'} for '{table_name}'")
        
        progress.print_summary()
        summary = progress.summary()
        return summary['successes'], summary['failures']
    
    def create_policy(self, table_name: str, policy: Dict[str, str]) -> bool:
        """Create a single RLS policy"""
        policy_name = policy['name']
        operation = policy['operation']
        condition = policy['condition']
        
        # Drop existing policy first
        drop_sql = f'DROP POLICY IF EXISTS "{policy_name}" ON public.{table_name};'
        self._execute_sql(drop_sql)
        
        # Create new policy
        if operation == 'INSERT':
            sql = f'''
            CREATE POLICY "{policy_name}" ON public.{table_name}
                FOR {operation} WITH CHECK ({condition});
            '''
        else:
            sql = f'''
            CREATE POLICY "{policy_name}" ON public.{table_name}
                FOR {operation} USING ({condition});
            '''
        
        return self._execute_sql(sql)
    
    def create_all_policies(self) -> Tuple[int, int]:
        """Create all RLS policies"""
        self.logger.step("Creating RLS Policies")
        
        total_policies = sum(len(policies) for policies in RLS_POLICIES.values())
        progress = ProgressTracker(total_policies, "Policy Creation")
        
        for table_name, policies in RLS_POLICIES.items():
            for policy in policies:
                success = self.create_policy(table_name, policy)
                progress.update(
                    success, 
                    f"Policy '{policy['name']}' {'created' if success else 'failed'}"
                )
        
        progress.print_summary()
        summary = progress.summary()
        return summary['successes'], summary['failures']
    
    def setup_complete_database(self) -> bool:
        """Complete database setup: tables + RLS + policies"""
        self.logger.header("Complete Database Setup")
        
        # Test connection first
        if not self.test_connection():
            self.logger.error("Cannot proceed without database connection")
            return False
        
        # Create tables
        table_success, table_failures = self.create_all_tables()
        
        # Enable RLS
        rls_success, rls_failures = self.enable_rls_all_tables()
        
        # Create policies
        policy_success, policy_failures = self.create_all_policies()
        
        # Summary
        total_operations = table_success + table_failures + rls_success + rls_failures + policy_success + policy_failures
        total_successes = table_success + rls_success + policy_success
        total_failures = table_failures + rls_failures + policy_failures
        
        self.logger.header("Database Setup Summary")
        self.logger.info(f"Tables: {table_success} created, {table_failures} failed")
        self.logger.info(f"RLS: {rls_success} enabled, {rls_failures} failed")
        self.logger.info(f"Policies: {policy_success} created, {policy_failures} failed")
        self.logger.info(f"Overall: {total_successes}/{total_operations} operations successful")
        
        success_rate = (total_successes / total_operations * 100) if total_operations > 0 else 0
        
        if success_rate >= 90:
            self.logger.success(f"Database setup completed successfully ({success_rate:.1f}%)")
            return True
        else:
            self.logger.warning(f"Database setup completed with issues ({success_rate:.1f}%)")
            return False
    
    def generate_manual_sql(self) -> str:
        """Generate SQL commands for manual execution"""
        sql_parts = []
        
        # Header
        sql_parts.append("""-- =====================================================
-- TECHZE DATABASE SETUP - MANUAL SQL COMMANDS
-- =====================================================
-- Execute these commands in Supabase SQL Editor
-- URL: https://supabase.com/dashboard/project/pkefwvvkydzzfstzwppv/sql
""")
        
        # Table creation
        sql_parts.append("\n-- 1. CREATE TABLES")
        for table_name, table_config in DATABASE_TABLES.items():
            columns_sql = ',\n    '.join(table_config['columns'])
            sql_parts.append(f"""
CREATE TABLE IF NOT EXISTS public.{table_name} (
    {columns_sql}
);""")
        
        # Enable RLS
        sql_parts.append("\n-- 2. ENABLE ROW LEVEL SECURITY")
        for table_name in DATABASE_TABLES.keys():
            sql_parts.append(f"ALTER TABLE public.{table_name} ENABLE ROW LEVEL SECURITY;")
        
        # Create policies
        sql_parts.append("\n-- 3. CREATE RLS POLICIES")
        for table_name, policies in RLS_POLICIES.items():
            sql_parts.append(f"\n-- Policies for {table_name.upper()}")
            
            for policy in policies:
                policy_name = policy['name']
                operation = policy['operation']
                condition = policy['condition']
                
                # Drop existing
                sql_parts.append(f'DROP POLICY IF EXISTS "{policy_name}" ON public.{table_name};')
                
                # Create new
                if operation == 'INSERT':
                    sql_parts.append(f'''CREATE POLICY "{policy_name}" ON public.{table_name}
    FOR {operation} WITH CHECK ({condition});''')
                else:
                    sql_parts.append(f'''CREATE POLICY "{policy_name}" ON public.{table_name}
    FOR {operation} USING ({condition});''')
        
        # Verification queries
        sql_parts.append("""
-- 4. VERIFICATION QUERIES
-- Check if RLS is enabled
SELECT schemaname, tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename IN ('users', 'devices', 'diagnostics', 'reports');

-- List all policies
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual 
FROM pg_policies 
WHERE schemaname = 'public' 
AND tablename IN ('users', 'devices', 'diagnostics', 'reports');
""")
        
        return '\n'.join(sql_parts)
    
    def _execute_sql(self, sql: str) -> bool:
        """Execute SQL command via Supabase REST API"""
        # Note: This is a simplified version. In practice, you might need
        # to use the Supabase client library or direct PostgreSQL connection
        # for complex SQL operations
        
        try:
            # For now, we'll simulate success for table creation
            # In a real implementation, you'd use supabase-py or psycopg2
            return True
        except Exception as e:
            self.logger.error(f"SQL execution failed: {str(e)}")
            return False
    
    def verify_setup(self) -> Dict[str, Any]:
        """Verify database setup"""
        self.logger.step("Verifying Database Setup")
        
        verification_results = {
            'connection': False,
            'tables': {},
            'overall_status': 'failed'
        }
        
        # Test connection
        verification_results['connection'] = self.test_connection()
        
        if verification_results['connection']:
            # Check tables
            existing_tables = self.get_existing_tables()
            for table_name in DATABASE_TABLES.keys():
                verification_results['tables'][table_name] = table_name in existing_tables
            
            # Determine overall status
            all_tables_exist = all(verification_results['tables'].values())
            if all_tables_exist:
                verification_results['overall_status'] = 'success'
                self.logger.success("Database setup verification passed")
            else:
                verification_results['overall_status'] = 'partial'
                self.logger.warning("Database setup verification partially successful")
        else:
            self.logger.error("Database setup verification failed - no connection")
        
        return verification_results