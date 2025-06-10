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
  CheckCircle2,
  Cpu,
  HardDrive,
  Smartphone,
  Laptop,
  Star,
  TrendingUp,
  Clock,
  Award
} from 'lucide-react';

export default function Index() {
  const { user } = useAuth();

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 relative overflow-hidden">
      {/* Background Effects */}
      <div className="absolute inset-0 opacity-30">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-cyan-500/20 rounded-full filter blur-3xl animate-pulse"></div>
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-blue-500/20 rounded-full filter blur-3xl animate-pulse delay-1000"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-purple-500/10 rounded-full filter blur-3xl animate-pulse delay-500"></div>
      </div>

      {/* Grid Pattern Overlay */}
      <div className="absolute inset-0 opacity-5">
        <div className="w-full h-full" style={{
          backgroundImage: `radial-gradient(circle at 1px 1px, rgba(255,255,255,0.3) 1px, transparent 0)`,
          backgroundSize: '50px 50px'
        }}></div>
      </div>

      {/* Header */}
      <header className="relative z-50 border-b border-slate-800/50 backdrop-blur-xl bg-slate-950/80">
        <div className="container mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="relative">
                <div className="p-3 rounded-2xl bg-gradient-to-br from-cyan-500/20 to-blue-600/20 border border-cyan-500/30 shadow-lg shadow-cyan-500/20">
                  <MonitorSpeaker className="h-8 w-8 text-cyan-400" />
                </div>
                <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">
                  TechZe Diagnóstico
                </h1>
                <p className="text-sm text-slate-400 font-medium">Sistema Profissional v3.0</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              {user ? (
                <Link to="/dashboard">
                  <Button className="bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white font-semibold px-6 py-2 rounded-xl shadow-lg shadow-cyan-500/25 transition-all duration-300 hover:shadow-cyan-500/40 hover:scale-105">
                    <Zap className="mr-2 h-4 w-4" />
                    Acessar Sistema
                  </Button>
                </Link>
              ) : (
                <Link to="/auth">
                  <Button className="bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white font-semibold px-6 py-2 rounded-xl shadow-lg shadow-cyan-500/25 transition-all duration-300 hover:shadow-cyan-500/40 hover:scale-105">
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
      <section className="relative z-10 py-24 lg:py-32">
        <div className="container mx-auto px-6">
          <div className="text-center max-w-5xl mx-auto">
            <div className="mb-8">
              <span className="inline-block px-4 py-2 rounded-full bg-gradient-to-r from-cyan-500/10 to-blue-600/10 border border-cyan-500/20 text-cyan-400 text-sm font-medium mb-6">
                🚀 Tecnologia de Ponta para Assistências Técnicas
              </span>
            </div>
            
            <h1 className="text-5xl lg:text-7xl font-bold mb-8 leading-tight">
              <span className="bg-gradient-to-r from-white via-slate-200 to-slate-300 bg-clip-text text-transparent">
                Diagnóstico de
              </span>
              <br />
              <span className="bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-600 bg-clip-text text-transparent">
                Hardware Profissional
              </span>
            </h1>
            
            <p className="text-xl lg:text-2xl text-slate-300 mb-12 max-w-3xl mx-auto leading-relaxed">
              Revolucione sua assistência técnica com nossa plataforma completa de diagnóstico. 
              <span className="text-cyan-400 font-semibold"> Tecnologia avançada</span>, 
              <span className="text-blue-400 font-semibold"> interface moderna</span> e 
              <span className="text-purple-400 font-semibold"> resultados precisos</span>.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-6 justify-center items-center mb-16">
              {user ? (
                <>
                  <Link to="/diagnostic">
                    <Button size="lg" className="bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white font-bold px-8 py-4 rounded-2xl shadow-xl shadow-cyan-500/25 transition-all duration-300 hover:shadow-cyan-500/40 hover:scale-105 text-lg">
                      <Zap className="mr-3 h-6 w-6" />
                      Novo Diagnóstico
                    </Button>
                  </Link>
                  <Link to="/dashboard">
                    <Button size="lg" variant="outline" className="border-2 border-slate-600 hover:border-cyan-500 text-slate-300 hover:text-cyan-400 font-semibold px-8 py-4 rounded-2xl transition-all duration-300 hover:bg-cyan-500/5 text-lg">
                      <BarChart3 className="mr-3 h-6 w-6" />
                      Ver Dashboard
                    </Button>
                  </Link>
                </>
              ) : (
                <Link to="/auth">
                  <Button size="lg" className="bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white font-bold px-8 py-4 rounded-2xl shadow-xl shadow-cyan-500/25 transition-all duration-300 hover:shadow-cyan-500/40 hover:scale-105 text-lg group">
                    <Zap className="mr-3 h-6 w-6" />
                    Começar Agora
                    <ArrowRight className="ml-3 h-6 w-6 group-hover:translate-x-1 transition-transform" />
                  </Button>
                </Link>
              )}
            </div>

            {/* Stats */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-8 max-w-4xl mx-auto">
              <div className="text-center">
                <div className="text-3xl lg:text-4xl font-bold text-cyan-400 mb-2">99.9%</div>
                <div className="text-slate-400 text-sm lg:text-base">Precisão</div>
              </div>
              <div className="text-center">
                <div className="text-3xl lg:text-4xl font-bold text-blue-400 mb-2">50+</div>
                <div className="text-slate-400 text-sm lg:text-base">Testes</div>
              </div>
              <div className="text-center">
                <div className="text-3xl lg:text-4xl font-bold text-purple-400 mb-2">24/7</div>
                <div className="text-slate-400 text-sm lg:text-base">Disponível</div>
              </div>
              <div className="text-center">
                <div className="text-3xl lg:text-4xl font-bold text-green-400 mb-2">1000+</div>
                <div className="text-slate-400 text-sm lg:text-base">Lojas</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="relative z-10 py-24 bg-gradient-to-b from-transparent to-slate-900/50">
        <div className="container mx-auto px-6">
          <div className="text-center mb-20">
            <h2 className="text-4xl lg:text-5xl font-bold mb-6">
              <span className="bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
                Recursos Avançados
              </span>
            </h2>
            <p className="text-xl text-slate-300 max-w-3xl mx-auto">
              Tudo que você precisa para diagnósticos profissionais de hardware em uma única plataforma
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-7xl mx-auto">
            {/* Feature Cards */}
            <Card className="bg-gradient-to-br from-slate-900/80 to-slate-800/80 border border-slate-700/50 backdrop-blur-xl hover:border-cyan-500/50 transition-all duration-300 hover:shadow-xl hover:shadow-cyan-500/10 group">
              <CardHeader className="pb-4">
                <div className="p-4 rounded-2xl bg-gradient-to-br from-cyan-500/20 to-blue-600/20 border border-cyan-500/30 w-fit mb-4 group-hover:scale-110 transition-transform duration-300">
                  <Cpu className="h-8 w-8 text-cyan-400" />
                </div>
                <CardTitle className="text-xl font-bold text-white">Diagnóstico Real</CardTitle>
                <CardDescription className="text-slate-300">
                  Coleta dados reais do hardware via APIs avançadas do navegador
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3 text-sm">
                  <li className="flex items-center"><CheckCircle2 className="h-5 w-5 text-green-400 mr-3 flex-shrink-0" /><span className="text-slate-300">Análise completa de CPU e Memória</span></li>
                  <li className="flex items-center"><CheckCircle2 className="h-5 w-5 text-green-400 mr-3 flex-shrink-0" /><span className="text-slate-300">Monitoramento de Rede e Bateria</span></li>
                  <li className="flex items-center"><CheckCircle2 className="h-5 w-5 text-green-400 mr-3 flex-shrink-0" /><span className="text-slate-300">Detecção do Sistema Operacional</span></li>
                </ul>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-slate-900/80 to-slate-800/80 border border-slate-700/50 backdrop-blur-xl hover:border-blue-500/50 transition-all duration-300 hover:shadow-xl hover:shadow-blue-500/10 group">
              <CardHeader className="pb-4">
                <div className="p-4 rounded-2xl bg-gradient-to-br from-blue-500/20 to-purple-600/20 border border-blue-500/30 w-fit mb-4 group-hover:scale-110 transition-transform duration-300">
                  <BarChart3 className="h-8 w-8 text-blue-400" />
                </div>
                <CardTitle className="text-xl font-bold text-white">Dashboard Inteligente</CardTitle>
                <CardDescription className="text-slate-300">
                  Relatórios e métricas em tempo real com visualizações avançadas
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3 text-sm">
                  <li className="flex items-center"><CheckCircle2 className="h-5 w-5 text-green-400 mr-3 flex-shrink-0" /><span className="text-slate-300">Histórico completo de diagnósticos</span></li>
                  <li className="flex items-center"><CheckCircle2 className="h-5 w-5 text-green-400 mr-3 flex-shrink-0" /><span className="text-slate-300">Gráficos interativos e dinâmicos</span></li>
                  <li className="flex items-center"><CheckCircle2 className="h-5 w-5 text-green-400 mr-3 flex-shrink-0" /><span className="text-slate-300">Relatórios PDF profissionais</span></li>
                </ul>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-slate-900/80 to-slate-800/80 border border-slate-700/50 backdrop-blur-xl hover:border-purple-500/50 transition-all duration-300 hover:shadow-xl hover:shadow-purple-500/10 group">
              <CardHeader className="pb-4">
                <div className="p-4 rounded-2xl bg-gradient-to-br from-purple-500/20 to-pink-600/20 border border-purple-500/30 w-fit mb-4 group-hover:scale-110 transition-transform duration-300">
                  <Wifi className="h-8 w-8 text-purple-400" />
                </div>
                <CardTitle className="text-xl font-bold text-white">Modo Offline</CardTitle>
                <CardDescription className="text-slate-300">
                  Funciona perfeitamente mesmo sem conexão com internet
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3 text-sm">
                  <li className="flex items-center"><CheckCircle2 className="h-5 w-5 text-green-400 mr-3 flex-shrink-0" /><span className="text-slate-300">Cache inteligente e otimizado</span></li>
                  <li className="flex items-center"><CheckCircle2 className="h-5 w-5 text-green-400 mr-3 flex-shrink-0" /><span className="text-slate-300">Sincronização automática</span></li>
                  <li className="flex items-center"><CheckCircle2 className="h-5 w-5 text-green-400 mr-3 flex-shrink-0" /><span className="text-slate-300">PWA nativo multiplataforma</span></li>
                </ul>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-slate-900/80 to-slate-800/80 border border-slate-700/50 backdrop-blur-xl hover:border-green-500/50 transition-all duration-300 hover:shadow-xl hover:shadow-green-500/10 group">
              <CardHeader className="pb-4">
                <div className="p-4 rounded-2xl bg-gradient-to-br from-green-500/20 to-emerald-600/20 border border-green-500/30 w-fit mb-4 group-hover:scale-110 transition-transform duration-300">
                  <Users className="h-8 w-8 text-green-400" />
                </div>
                <CardTitle className="text-xl font-bold text-white">Multi-Loja</CardTitle>
                <CardDescription className="text-slate-300">
                  Suporte completo para múltiplas lojas e franquias
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3 text-sm">
                  <li className="flex items-center"><CheckCircle2 className="h-5 w-5 text-green-400 mr-3 flex-shrink-0" /><span className="text-slate-300">Branding personalizado por loja</span></li>
                  <li className="flex items-center"><CheckCircle2 className="h-5 w-5 text-green-400 mr-3 flex-shrink-0" /><span className="text-slate-300">Gestão de usuários e permissões</span></li>
                  <li className="flex items-center"><CheckCircle2 className="h-5 w-5 text-green-400 mr-3 flex-shrink-0" /><span className="text-slate-300">Dados isolados e seguros</span></li>
                </ul>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-slate-900/80 to-slate-800/80 border border-slate-700/50 backdrop-blur-xl hover:border-red-500/50 transition-all duration-300 hover:shadow-xl hover:shadow-red-500/10 group">
              <CardHeader className="pb-4">
                <div className="p-4 rounded-2xl bg-gradient-to-br from-red-500/20 to-orange-600/20 border border-red-500/30 w-fit mb-4 group-hover:scale-110 transition-transform duration-300">
                  <Shield className="h-8 w-8 text-red-400" />
                </div>
                <CardTitle className="text-xl font-bold text-white">Segurança Total</CardTitle>
                <CardDescription className="text-slate-300">
                  Proteção completa dos dados com criptografia avançada
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3 text-sm">
                  <li className="flex items-center"><CheckCircle2 className="h-5 w-5 text-green-400 mr-3 flex-shrink-0" /><span className="text-slate-300">Criptografia end-to-end</span></li>
                  <li className="flex items-center"><CheckCircle2 className="h-5 w-5 text-green-400 mr-3 flex-shrink-0" /><span className="text-slate-300">Backup automático em nuvem</span></li>
                  <li className="flex items-center"><CheckCircle2 className="h-5 w-5 text-green-400 mr-3 flex-shrink-0" /><span className="text-slate-300">Auditoria completa de ações</span></li>
                </ul>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-slate-900/80 to-slate-800/80 border border-slate-700/50 backdrop-blur-xl hover:border-yellow-500/50 transition-all duration-300 hover:shadow-xl hover:shadow-yellow-500/10 group">
              <CardHeader className="pb-4">
                <div className="p-4 rounded-2xl bg-gradient-to-br from-yellow-500/20 to-orange-600/20 border border-yellow-500/30 w-fit mb-4 group-hover:scale-110 transition-transform duration-300">
                  <MonitorSpeaker className="h-8 w-8 text-yellow-400" />
                </div>
                <CardTitle className="text-xl font-bold text-white">Interface Moderna</CardTitle>
                <CardDescription className="text-slate-300">
                  Design profissional, responsivo e acessível
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3 text-sm">
                  <li className="flex items-center"><CheckCircle2 className="h-5 w-5 text-green-400 mr-3 flex-shrink-0" /><span className="text-slate-300">Design mobile-first responsivo</span></li>
                  <li className="flex items-center"><CheckCircle2 className="h-5 w-5 text-green-400 mr-3 flex-shrink-0" /><span className="text-slate-300">Tema escuro profissional</span></li>
                  <li className="flex items-center"><CheckCircle2 className="h-5 w-5 text-green-400 mr-3 flex-shrink-0" /><span className="text-slate-300">Acessibilidade WCAG 2.1</span></li>
                </ul>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="relative z-10 py-24">
        <div className="container mx-auto px-6">
          <div className="max-w-4xl mx-auto text-center">
            <div className="bg-gradient-to-br from-slate-900/80 to-slate-800/80 border border-slate-700/50 backdrop-blur-xl rounded-3xl p-12 shadow-2xl">
              <h2 className="text-4xl lg:text-5xl font-bold mb-6">
                <span className="bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
                  Pronto para Revolucionar
                </span>
                <br />
                <span className="text-white">Sua Assistência Técnica?</span>
              </h2>
              <p className="text-xl text-slate-300 mb-8 max-w-2xl mx-auto">
                Junte-se a milhares de profissionais que já transformaram seus negócios com nossa plataforma
              </p>
              {!user && (
                <Link to="/auth">
                  <Button size="lg" className="bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white font-bold px-12 py-4 rounded-2xl shadow-xl shadow-cyan-500/25 transition-all duration-300 hover:shadow-cyan-500/40 hover:scale-105 text-lg">
                    <Zap className="mr-3 h-6 w-6" />
                    Começar Gratuitamente
                  </Button>
                </Link>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative z-10 border-t border-slate-800/50 bg-slate-950/80 backdrop-blur-xl">
        <div className="container mx-auto px-6 py-12">
          <div className="text-center">
            <div className="flex items-center justify-center space-x-4 mb-6">
              <div className="p-3 rounded-2xl bg-gradient-to-br from-cyan-500/20 to-blue-600/20 border border-cyan-500/30">
                <MonitorSpeaker className="h-6 w-6 text-cyan-400" />
              </div>
              <h3 className="text-xl font-bold bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">
                TechZe Diagnóstico
              </h3>
            </div>
            <p className="text-slate-400 mb-4">
              © 2024 TechZe Diagnóstico. Sistema Profissional de Hardware.
            </p>
            <p className="text-sm text-slate-500">
              Desenvolvido com ❤️ para assistências técnicas profissionais
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
