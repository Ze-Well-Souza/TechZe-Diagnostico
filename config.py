#!/usr/bin/env python3
"""
Centralized configuration management for TechZe project
"""

import os
from typing import Dict
from dataclasses import dataclass


@dataclass
class SupabaseConfig:
    """Supabase configuration"""
    url: str
    service_role_key: str
    anon_key: str = ""
    
    @property
    def headers(self) -> Dict[str, str]:
        """Get standard headers for Supabase requests"""
        return {
            "apikey": self.service_role_key,
            "Authorization": f"Bearer {self.service_role_key}",
            "Content-Type": "application/json"
        }


@dataclass
class ProjectConfig:
    """Project configuration"""
    name: str = "TechZe-Diagnostico"
    version: str = "1.0.0"
    frontend_port: int = 8081
    backend_port: int = 8000
    timeout: int = 10


class Config:
    """Main configuration class"""
    
    def __init__(self):
        self.supabase = SupabaseConfig(
            url=os.getenv("SUPABASE_URL", "https://pkefwvvkydzzfstzwppv.supabase.co"),
            service_role_key=os.getenv(
                "SUPABASE_SERVICE_ROLE_KEY", 
                "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBrZWZ3dnZreWR6emZzdHp3cHB2Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NzM0MjY3NSwiZXhwIjoyMDYyOTE4Njc1fQ.x9lc7-x9Aj0bB0WOZQ4b_buEwftPgCuGirvxjn_S6m8"
            )
        )
        self.project = ProjectConfig()
    
    @classmethod
    def from_env(cls) -> 'Config':
        """Create configuration from environment variables"""
        return cls()


# Global configuration instance
config = Config.from_env()

# Database table definitions
DATABASE_TABLES = {
    'users': {
        'columns': [
            'id UUID PRIMARY KEY DEFAULT gen_random_uuid()',
            'email VARCHAR(255) UNIQUE NOT NULL',
            'created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()',
            'updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()'
        ]
    },
    'devices': {
        'columns': [
            'id UUID PRIMARY KEY DEFAULT gen_random_uuid()',
            'user_id UUID REFERENCES public.users(id) ON DELETE CASCADE',
            'name VARCHAR(100) NOT NULL',
            'type VARCHAR(50)',
            'os VARCHAR(100)',
            'created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()',
            'updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()'
        ]
    },
    'diagnostics': {
        'columns': [
            'id UUID PRIMARY KEY DEFAULT gen_random_uuid()',
            'user_id UUID REFERENCES public.users(id) ON DELETE CASCADE',
            'device_id UUID REFERENCES public.devices(id) ON DELETE CASCADE',
            'status VARCHAR(50) NOT NULL',
            'health_score DECIMAL(5,2)',
            'execution_time DECIMAL(10,2)',
            'created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()',
            'updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()'
        ]
    },
    'reports': {
        'columns': [
            'id UUID PRIMARY KEY DEFAULT gen_random_uuid()',
            'diagnostic_id UUID REFERENCES public.diagnostics(id) ON DELETE CASCADE',
            'title VARCHAR(200) NOT NULL',
            'content TEXT',
            'file_path VARCHAR(500)',
            'created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()'
        ]
    }
}

# RLS Policies definitions
RLS_POLICIES = {
    'users': [
        {
            'name': 'Usuários podem ver seu próprio perfil',
            'operation': 'SELECT',
            'condition': 'auth.uid() = id'
        },
        {
            'name': 'Usuários podem atualizar seu próprio perfil',
            'operation': 'UPDATE',
            'condition': 'auth.uid() = id'
        }
    ],
    'devices': [
        {
            'name': 'Usuários podem ver seus próprios dispositivos',
            'operation': 'SELECT',
            'condition': 'auth.uid() = user_id'
        },
        {
            'name': 'Usuários podem criar dispositivos',
            'operation': 'INSERT',
            'condition': 'auth.uid() = user_id'
        },
        {
            'name': 'Usuários podem atualizar seus próprios dispositivos',
            'operation': 'UPDATE',
            'condition': 'auth.uid() = user_id'
        }
    ],
    'diagnostics': [
        {
            'name': 'Usuários podem ver seus próprios diagnósticos',
            'operation': 'SELECT',
            'condition': 'auth.uid() = user_id'
        },
        {
            'name': 'Usuários podem criar diagnósticos',
            'operation': 'INSERT',
            'condition': 'auth.uid() = user_id'
        },
        {
            'name': 'Usuários podem atualizar seus próprios diagnósticos',
            'operation': 'UPDATE',
            'condition': 'auth.uid() = user_id'
        }
    ],
    'reports': [
        {
            'name': 'Usuários podem ver seus próprios relatórios',
            'operation': 'SELECT',
            'condition': '''EXISTS (
                SELECT 1 FROM public.diagnostics 
                WHERE diagnostics.id = reports.diagnostic_id 
                AND diagnostics.user_id = auth.uid()
            )'''
        },
        {
            'name': 'Usuários podem criar relatórios para seus diagnósticos',
            'operation': 'INSERT',
            'condition': '''EXISTS (
                SELECT 1 FROM public.diagnostics 
                WHERE diagnostics.id = reports.diagnostic_id 
                AND diagnostics.user_id = auth.uid()
            )'''
        }
    ]
}