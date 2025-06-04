
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  Cpu, 
  Zap, 
  Shield, 
  BarChart3, 
  FileText, 
  Users, 
  CheckCircle, 
  ArrowRight,
  Monitor,
  HardDrive,
  Wifi
} from 'lucide-react';

export default function Landing() {
  const features = [
    {
      icon: <Cpu className="h-8 w-8 text-electric" />,
      title: "Diagnóstico Avançado",
      description: "Análise completa de hardware, antivírus, drivers e arquivos corrompidos"
    },
    {
      icon: <BarChart3 className="h-8 w-8 text-tech" />,
      title: "Relatórios Detalhados",
      description: "Gere relatórios profissionais e orçamentos personalizados"
    },
    {
      icon: <Shield className="h-8 w-8 text-electric" />,
      title: "Monitoramento em Tempo Real",
      description: "Acompanhe a saúde dos equipamentos continuamente"
    },
    {
      icon: <Users className="h-8 w-8 text-tech" />,
      title: "Multi-Empresa",
      description: "Gerencie múltiplas empresas com isolamento completo de dados"
    }
  ];

  return (
    <div className="min-h-screen bg-black text-white pt-16">
      {/* Hero Section */}
      <section className="relative overflow-hidden py-20 lg:py-32">
        {/* Background Effects */}
        <div className="absolute inset-0">
          <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-electric/10 rounded-full blur-3xl"></div>
          <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-tech/10 rounded-full blur-3xl"></div>
        </div>
        
        <div className="container mx-auto px-4 relative">
          <div className="text-center max-w-4xl mx-auto">
            <Badge className="mb-6 bg-electric/20 text-electric border-electric/30">
              🚀 Sistema Profissional de Diagnósticos
            </Badge>
            
            <h1 className="text-4xl md:text-6xl lg:text-7xl font-bold mb-6">
              TechRepair
              <span className="gradient-text block">Pro System</span>
            </h1>
            
            <p className="text-xl md:text-2xl text-gray-300 mb-8 max-w-3xl mx-auto">
              Plataforma completa para diagnóstico, manutenção e monitoramento de computadores. 
              Sistema multi-empresa com relatórios profissionais e orçamentos automatizados.
            </p>
            
            <div className="flex justify-center">
              <Link to="/auth">
                <Button size="lg" className="bg-gradient-to-r from-electric to-tech hover:from-electric/80 hover:to-tech/80 text-black font-semibold text-lg px-12 py-6">
                  Acessar Sistema <ArrowRight className="ml-2 h-6 w-6" />
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-gradient-to-r from-dark/50 to-darker/50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Recursos <span className="gradient-text">Profissionais</span>
            </h2>
            <p className="text-xl text-gray-400">Tudo que você precisa para gerenciar sua empresa de manutenção</p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <Card key={index} className="glass-effect border-white/10 hover:border-electric/30 transition-all duration-300">
                <CardHeader>
                  <div className="w-16 h-16 bg-gradient-to-r from-electric/20 to-tech/20 rounded-full flex items-center justify-center mb-4">
                    {feature.icon}
                  </div>
                  <CardTitle className="text-white">{feature.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-gray-400">{feature.description}</CardDescription>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 border-t border-white/10">
        <div className="container mx-auto px-4 text-center">
          <div className="flex items-center justify-center space-x-2 mb-4">
            <div className="relative">
              <Cpu className="h-8 w-8 text-electric" />
              <Zap className="h-4 w-4 text-tech absolute -top-1 -right-1" />
            </div>
            <span className="text-xl font-bold gradient-text">TechRepair Pro</span>
          </div>
          <p className="text-gray-400 mb-4">
            Sistema profissional para empresas de manutenção e diagnóstico de computadores.
          </p>
          <p className="text-gray-500">&copy; 2024 TechRepair Pro. Todos os direitos reservados.</p>
        </div>
      </footer>
    </div>
  );
}
