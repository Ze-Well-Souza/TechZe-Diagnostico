
import React, { createContext, useContext, useState, ReactNode } from 'react';

export interface Company {
  id: string;
  name: string;
  displayName: string;
  theme: {
    primary: string;
    secondary: string;
    accent: string;
    logo?: string;
    favicon?: string;
  };
  features: string[];
}

const companies: Company[] = [
  {
    id: 'ulytech',
    name: 'UlyTech',
    displayName: 'UlyTech Informática',
    theme: {
      primary: '#00f5ff', // electric
      secondary: '#8b5cf6', // tech purple
      accent: '#10b981', // emerald
    },
    features: ['diagnostics', 'reports', 'marketplace', 'whatsapp']
  },
  {
    id: 'utilimix',
    name: 'Utilimix',
    displayName: 'Utilimix Soluções',
    theme: {
      primary: '#ef4444', // red
      secondary: '#f97316', // orange
      accent: '#eab308', // yellow
    },
    features: ['diagnostics', 'reports', 'whatsapp']
  },
  {
    id: 'useprint',
    name: 'Useprint',
    displayName: 'Useprint Gráfica',
    theme: {
      primary: '#3b82f6', // blue
      secondary: '#6366f1', // indigo
      accent: '#8b5cf6', // purple
    },
    features: ['diagnostics', 'reports', 'file-conversion']
  }
];

interface CompanyContextType {
  selectedCompany: Company | null;
  setSelectedCompany: (company: Company) => void;
  companies: Company[];
  getCompanyById: (id: string) => Company | undefined;
}

const CompanyContext = createContext<CompanyContextType | undefined>(undefined);

export const useCompany = () => {
  const context = useContext(CompanyContext);
  if (context === undefined) {
    throw new Error('useCompany must be used within a CompanyProvider');
  }
  return context;
};

interface CompanyProviderProps {
  children: ReactNode;
}

export const CompanyProvider: React.FC<CompanyProviderProps> = ({ children }) => {
  const [selectedCompany, setSelectedCompany] = useState<Company | null>(
    companies.find(c => c.id === 'ulytech') || null
  );

  const getCompanyById = (id: string) => {
    return companies.find(company => company.id === id);
  };

  return (
    <CompanyContext.Provider value={{
      selectedCompany,
      setSelectedCompany,
      companies,
      getCompanyById
    }}>
      {children}
    </CompanyContext.Provider>
  );
};
