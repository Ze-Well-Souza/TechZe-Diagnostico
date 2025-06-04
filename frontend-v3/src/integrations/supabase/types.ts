export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export type Database = {
  public: {
    Tables: {
      companies: {
        Row: {
          code: string
          created_at: string | null
          id: string
          logo_url: string | null
          name: string
          primary_color: string | null
          subdomain: string
          updated_at: string | null
        }
        Insert: {
          code: string
          created_at?: string | null
          id?: string
          logo_url?: string | null
          name: string
          primary_color?: string | null
          subdomain: string
          updated_at?: string | null
        }
        Update: {
          code?: string
          created_at?: string | null
          id?: string
          logo_url?: string | null
          name?: string
          primary_color?: string | null
          subdomain?: string
          updated_at?: string | null
        }
        Relationships: []
      }
      company_users: {
        Row: {
          company_id: string | null
          created_at: string | null
          id: string
          is_active: boolean | null
          role: string | null
          updated_at: string | null
          user_id: string | null
        }
        Insert: {
          company_id?: string | null
          created_at?: string | null
          id?: string
          is_active?: boolean | null
          role?: string | null
          updated_at?: string | null
          user_id?: string | null
        }
        Update: {
          company_id?: string | null
          created_at?: string | null
          id?: string
          is_active?: boolean | null
          role?: string | null
          updated_at?: string | null
          user_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "company_users_company_id_fkey"
            columns: ["company_id"]
            isOneToOne: false
            referencedRelation: "companies"
            referencedColumns: ["id"]
          },
        ]
      }
      devices: {
        Row: {
          created_at: string | null
          id: string
          last_diagnostic_id: string | null
          name: string
          os: string | null
          os_version: string | null
          processor: string | null
          ram: string | null
          storage: string | null
          type: string
          updated_at: string | null
          user_id: string
        }
        Insert: {
          created_at?: string | null
          id?: string
          last_diagnostic_id?: string | null
          name: string
          os?: string | null
          os_version?: string | null
          processor?: string | null
          ram?: string | null
          storage?: string | null
          type: string
          updated_at?: string | null
          user_id: string
        }
        Update: {
          created_at?: string | null
          id?: string
          last_diagnostic_id?: string | null
          name?: string
          os?: string | null
          os_version?: string | null
          processor?: string | null
          ram?: string | null
          storage?: string | null
          type?: string
          updated_at?: string | null
          user_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "devices_last_diagnostic_id_fkey"
            columns: ["last_diagnostic_id"]
            isOneToOne: false
            referencedRelation: "diagnostics"
            referencedColumns: ["id"]
          },
        ]
      }
      diagnostics: {
        Row: {
          created_at: string | null
          device_id: string
          id: string
          issues_found: Json | null
          performance_score: number | null
          recommendations: Json | null
          status: string
          system_info: Json | null
          updated_at: string | null
        }
        Insert: {
          created_at?: string | null
          device_id: string
          id?: string
          issues_found?: Json | null
          performance_score?: number | null
          recommendations?: Json | null
          status: string
          system_info?: Json | null
          updated_at?: string | null
        }
        Update: {
          created_at?: string | null
          device_id?: string
          id?: string
          issues_found?: Json | null
          performance_score?: number | null
          recommendations?: Json | null
          status?: string
          system_info?: Json | null
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "diagnostics_device_id_fkey"
            columns: ["device_id"]
            isOneToOne: false
            referencedRelation: "devices"
            referencedColumns: ["id"]
          },
        ]
      }
      reports: {
        Row: {
          created_at: string | null
          diagnostic_id: string
          file_path: string | null
          file_size: number | null
          format: string
          id: string
          status: string
          updated_at: string | null
        }
        Insert: {
          created_at?: string | null
          diagnostic_id: string
          file_path?: string | null
          file_size?: number | null
          format: string
          id?: string
          status: string
          updated_at?: string | null
        }
        Update: {
          created_at?: string | null
          diagnostic_id?: string
          file_path?: string | null
          file_size?: number | null
          format?: string
          id?: string
          status?: string
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "reports_diagnostic_id_fkey"
            columns: ["diagnostic_id"]
            isOneToOne: false
            referencedRelation: "diagnostics"
            referencedColumns: ["id"]
          },
        ]
      }
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      [_ in never]: never
    }
    Enums: {
      [_ in never]: never
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
}