
import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { 
  MonitorSpeaker, 
  Zap, 
  Shield, 
  BarChart3, 
  Wifi, 
  Users,
  ArrowRight,
  CheckCircle2
} from 'lucide-react';

export default function Index() {
  const { user } = useAuth();

  return (
    <div className="min-h-screen bg-gradient-to-br from-tech-darker via-tech-dark to-tech-darker">
      {/* Header */}
      <header className="border-b border-primary/20 backdrop-blur-md">
        <div className="container-responsive py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className="p-2 rounded-lg bg-primary/10 electric-glow">
                <MonitorSpeaker className="h-8 w-8 text-electric" />
              </div>
              <div>
                <h1 className="tech-font text-xl font-bold neon-text">TechRepair</h1>
                <p className="text-xs text-muted-foreground">Sistema de Diagnóstico v3.0</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              {user ? (
                <Link to="/dashboard">
                  <Button className="btn-electric">
                    <Zap className="mr-2 h-4 w-4" />
                    Acessar Sistema
                  </Button>
                </Link>
              ) : (
                <Link to="/auth">
                  <Button className="btn-electric">
                    <Zap className="mr-2 h-4 w-4" />
                    Entrar
                  </Button>
                </Link>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-20 relative overflow-hidden">
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-electric rounded-full filter blur-3xl"></div>
          <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-electric rounded-full filter blur-3xl"></div>
        </div>
        
        <div className="container-responsive relative z-10">
          <div className="text-center max-w-4xl mx-auto">
            <h1 className="tech-font text-4xl md:text-6xl font-bold mb-6">
              <span className="neon-text">Diagnóstico</span> de Hardware
              <br />
              <span className="text-foreground">Profissional</span>
            </h1>
            
            <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
              Sistema completo para diagnóstico, análise e reparo de computadores. 
              Tecnologia avançada para lojas de informática.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              {user ? (
                <>
                  <Link to="/diagnostic">
                    <Button size="lg" className="btn-electric tech-font">
                      <Zap className="mr-2 h-5 w-5" />
                      Novo Diagnóstico
                    </Button>
                  </Link>
                  <Link to="/dashboard">
                    <Button size="lg" variant="outline" className="electric-border">
                      <BarChart3 className="mr-2 h-5 w-5" />
                      Ver Dashboard
                    </Button>
                  </Link>
                </>
              ) : (
                <Link to="/auth">
                  <Button size="lg" className="btn-electric tech-font">
                    <Zap className="mr-2 h-5 w-5" />
                    Começar Agora
                    <ArrowRight className="ml-2 h-5 w-5" />
                  </Button>
                </Link>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-muted/5">
        <div className="container-responsive">
          <div className="text-center mb-16">
            <h2 className="tech-font text-3xl font-bold neon-text mb-4">
              Recursos Avançados
            </h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              Tudo que você precisa para diagnósticos profissionais de hardware
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            <Card className="card-electric">
              <CardHeader>
                <div className="p-3 rounded-lg bg-primary/10 electric-glow w-fit">
                  <Zap className="h-6 w-6 text-electric" />
                </div>
                <CardTitle>Diagnóstico Real</CardTitle>
                <CardDescription>
                  Coleta dados reais do hardware via APIs do navegador
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-sm">
                  <li className="flex items-center"><CheckCircle2 className="h-4 w-4 text-green-400 mr-2" />CPU e Memória</li>
                  <li className="flex items-center"><CheckCircle2 className="h-4 w-4 text-green-400 mr-2" />Rede e Bateria</li>
                  <li className="flex items-center"><CheckCircle2 className="h-4 w-4 text-green-400 mr-2" />Sistema Operacional</li>
                </ul>
              </CardContent>
            </Card>

            <Card className="card-electric">
              <CardHeader>
                <div className="p-3 rounded-lg bg-primary/10 electric-glow w-fit">
                  <BarChart3 className="h-6 w-6 text-electric" />
                </div>
                <CardTitle>Dashboard Inteligente</CardTitle>
                <CardDescription>
                  Relatórios e métricas em tempo real
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-sm">
                  <li className="flex items-center"><CheckCircle2 className="h-4 w-4 text-green-400 mr-2" />Histórico Completo</li>
                  <li className="flex items-center"><CheckCircle2 className="h-4 w-4 text-green-400 mr-2" />Gráficos Interativos</li>
                  <li className="flex items-center"><CheckCircle2 className="h-4 w-4 text-green-400 mr-2" />Relatórios PDF</li>
                </ul>
              </CardContent>
            </Card>

            <Card className="card-electric">
              <CardHeader>
                <div className="p-3 rounded-lg bg-primary/10 electric-glow w-fit">
                  <Wifi className="h-6 w-6 text-electric" />
                </div>
                <CardTitle>Modo Offline</CardTitle>
                <CardDescription>
                  Funciona mesmo sem conexão com internet
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-sm">
                  <li className="flex items-center"><CheckCircle2 className="h-4 w-4 text-green-400 mr-2" />Cache Inteligente</li>
                  <li className="flex items-center"><CheckCircle2 className="h-4 w-4 text-green-400 mr-2" />Sincronização</li>
                  <li className="flex items-center"><CheckCircle2 className="h-4 w-4 text-green-400 mr-2" />PWA Nativo</li>
                </ul>
              </CardContent>
            </Card>

            <Card className="card-electric">
              <CardHeader>
                <div className="p-3 rounded-lg bg-primary/10 electric-glow w-fit">
                  <Users className="h-6 w-6 text-electric" />
                </div>
                <CardTitle>Multi-Loja</CardTitle>
                <CardDescription>
                  Suporte completo para múltiplas lojas
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-sm">
                  <li className="flex items-center"><CheckCircle2 className="h-4 w-4 text-green-400 mr-2" />Branding Próprio</li>
                  <li className="flex items-center"><CheckCircle2 className="h-4 w-4 text-green-400 mr-2" />Usuários e Roles</li>
                  <li className="flex items-center"><CheckCircle2 className="h-4 w-4 text-green-400 mr-2" />Dados Isolados</li>
                </ul>
              </CardContent>
            </Card>

            <Card className="card-electric">
              <CardHeader>
                <div className="p-3 rounded-lg bg-primary/10 electric-glow w-fit">
                  <Shield className="h-6 w-6 text-electric" />
                </div>
                <CardTitle>Segurança Total</CardTitle>
                <CardDescription>
                  Proteção completa dos dados
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-sm">
                  <li className="flex items-center"><CheckCircle2 className="h-4 w-4 text-green-400 mr-2" />Criptografia</li>
                  <li className="flex items-center"><CheckCircle2 className="h-4 w-4 text-green-400 mr-2" />Backup Automático</li>
                  <li className="flex items-center"><CheckCircle2 className="h-4 w-4 text-green-400 mr-2" />Auditoria</li>
                </ul>
              </CardContent>
            </Card>

            <Card className="card-electric">
              <CardHeader>
                <div className="p-3 rounded-lg bg-primary/10 electric-glow w-fit">
                  <MonitorSpeaker className="h-6 w-6 text-electric" />
                </div>
                <CardTitle>Interface Moderna</CardTitle>
                <CardDescription>
                  Design profissional e responsivo
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-sm">
                  <li className="flex items-center"><CheckCircle2 className="h-4 w-4 text-green-400 mr-2" />Mobile First</li>
                  <li className="flex items-center"><CheckCircle2 className="h-4 w-4 text-green-400 mr-2" />Dark Mode</li>
                  <li className="flex items-center"><CheckCircle2 className="h-4 w-4 text-green-400 mr-2" />Acessibilidade</li>
                </ul>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-primary/20 py-8">
        <div className="container-responsive">
          <div className="text-center text-muted-foreground">
            <p className="tech-font">
              © 2024 TechZe Diagnóstico. Sistema Profissional de Hardware.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
