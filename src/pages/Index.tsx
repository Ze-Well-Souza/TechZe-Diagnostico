
import React from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { OfflineIndicator } from '@/components/ui/OfflineIndicator';
import { InstallPWABanner } from '@/components/ui/InstallPWABanner';
import { 
  Monitor, 
  Shield, 
  Zap, 
  TrendingUp,
  Settings,
  BarChart3
} from 'lucide-react';

const Index = () => {
  const features = [
    {
      icon: Monitor,
      title: 'Diagnóstico Avançado',
      description: 'Sistema completo de diagnóstico para dispositivos TechZe com relatórios detalhados'
    },
    {
      icon: Shield,
      title: 'Segurança Multi-Tenant',
      description: 'Isolamento completo de dados entre lojas com políticas RLS do Supabase'
    },
    {
      icon: Zap,
      title: 'Performance Otimizada',
      description: 'Cache distribuído, lazy loading e monitoramento em tempo real'
    },
    {
      icon: TrendingUp,
      title: 'Analytics Integrado',
      description: 'Dashboard unificado com métricas de performance e alertas inteligentes'
    },
    {
      icon: Settings,
      title: 'CI/CD Automatizado',
      description: 'Deploy canário com GitHub Actions e rollback automático'
    },
    {
      icon: BarChart3,
      title: 'Monitoramento 24/7',
      description: 'Prometheus + Grafana com alertas por SMS/Email'
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <OfflineIndicator />
      <InstallPWABanner />
      
      <div className="container-responsive py-12">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
            TechZe <span className="text-blue-600">Diagnóstico</span>
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            Plataforma profissional de diagnóstico para dispositivos TechZe com 
            arquitetura multi-tenant, segurança avançada e monitoramento em tempo real
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/dashboard">
              <Button size="lg" className="w-full sm:w-auto">
                Acessar Dashboard
              </Button>
            </Link>
            <Button variant="outline" size="lg" className="w-full sm:w-auto">
              Documentação
            </Button>
          </div>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-16">
          {features.map((feature, index) => (
            <Card key={index} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-center space-x-3">
                  <div className="p-2 bg-blue-100 rounded-lg">
                    <feature.icon className="h-6 w-6 text-blue-600" />
                  </div>
                  <CardTitle className="text-lg">{feature.title}</CardTitle>
                </div>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-base">
                  {feature.description}
                </CardDescription>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Architecture Highlights */}
        <div className="bg-white rounded-2xl p-8 shadow-lg">
          <h2 className="text-3xl font-bold text-center mb-8">Arquitetura Profissional</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="bg-green-100 p-3 rounded-full w-16 h-16 mx-auto mb-4 flex items-center justify-center">
                <Shield className="h-8 w-8 text-green-600" />
              </div>
              <h3 className="font-semibold mb-2">Segurança</h3>
              <p className="text-sm text-gray-600">JWT + RLS + OWASP</p>
            </div>
            <div className="text-center">
              <div className="bg-blue-100 p-3 rounded-full w-16 h-16 mx-auto mb-4 flex items-center justify-center">
                <Zap className="h-8 w-8 text-blue-600" />
              </div>
              <h3 className="font-semibold mb-2">Performance</h3>
              <p className="text-sm text-gray-600">Redis + CDN + Lazy Loading</p>
            </div>
            <div className="text-center">
              <div className="bg-purple-100 p-3 rounded-full w-16 h-16 mx-auto mb-4 flex items-center justify-center">
                <Settings className="h-8 w-8 text-purple-600" />
              </div>
              <h3 className="font-semibold mb-2">DevOps</h3>
              <p className="text-sm text-gray-600">GitHub Actions + Canary</p>
            </div>
            <div className="text-center">
              <div className="bg-orange-100 p-3 rounded-full w-16 h-16 mx-auto mb-4 flex items-center justify-center">
                <BarChart3 className="h-8 w-8 text-orange-600" />
              </div>
              <h3 className="font-semibold mb-2">Observabilidade</h3>
              <p className="text-sm text-gray-600">Prometheus + Grafana</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Index;
