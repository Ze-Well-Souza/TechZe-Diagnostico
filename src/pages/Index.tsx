import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/hooks/useAuth";
import { 
  Wrench, 
  Monitor, 
  FileText, 
  Users, 
  ArrowRight,
  CheckCircle,
  ShoppingBag,
  Settings,
  Activity,
  Shield,
  Zap,
  TrendingUp
} from "lucide-react";

const Index = () => {
  const navigate = useNavigate();
  const { user } = useAuth();

  // If user is logged in, redirect to dashboard
  if (user) {
    navigate("/dashboard");
    return null;
  }

  return (
    <div className="min-h-screen bg-black">
      {/* Header */}
      <header className="border-b border-gray-800 bg-black">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-gray-900 rounded-lg">
              <Wrench className="w-6 h-6 text-white" />
            </div>
            <h1 className="text-2xl font-bold text-white">TechRepair</h1>
          </div>
          <Button 
            onClick={() => navigate("/auth")}
            className="bg-gray-800 hover:bg-gray-700 text-white border border-gray-700"
          >
            Acessar Sistema
          </Button>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-24 px-6 bg-gradient-to-b from-black to-gray-900">
        <div className="max-w-7xl mx-auto text-center">
          <div className="mb-8">
            <Badge className="bg-gray-800 text-gray-200 border-gray-700 mb-4">
              Sistema de Diagnóstico v2.0
            </Badge>
          </div>
          <h2 className="text-6xl font-bold text-white mb-6 leading-tight">
            Sistema de Diagnóstico
            <span className="block text-gray-300">Técnico</span>
          </h2>
          <p className="text-xl text-gray-400 mb-10 max-w-3xl mx-auto leading-relaxed">
            Realize diagnósticos completos de hardware e software, gere relatórios detalhados 
            e mantenha o controle total sobre a saúde dos sistemas.
          </p>
          <div className="flex flex-wrap gap-4 justify-center">
            <Button 
              size="lg"
              onClick={() => navigate("/auth")}
              className="bg-white text-black hover:bg-gray-100 px-8 py-6 text-lg font-semibold"
            >
              Começar Agora
              <ArrowRight className="w-5 h-5 ml-2" />
            </Button>
            <Button 
              size="lg"
              variant="outline"
              className="border-gray-700 text-gray-300 hover:bg-gray-800 px-8 py-6 text-lg"
            >
              Ver Demo
            </Button>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 px-6 bg-gray-900">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 text-center">
            <div>
              <div className="text-4xl font-bold text-white mb-2">99.9%</div>
              <div className="text-gray-400">Precisão</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-white mb-2">500+</div>
              <div className="text-gray-400">Sistemas Analisados</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-white mb-2">24/7</div>
              <div className="text-gray-400">Monitoramento</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-white mb-2">5min</div>
              <div className="text-gray-400">Diagnóstico Rápido</div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-6 bg-black">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h3 className="text-4xl font-bold text-white mb-4">
              Funcionalidades Principais
            </h3>
            <p className="text-xl text-gray-400 max-w-2xl mx-auto">
              Tudo que você precisa para manter seus sistemas funcionando perfeitamente
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            <Card className="bg-gray-900 border-gray-800 hover:border-gray-700 transition-colors">
              <CardHeader>
                <div className="w-12 h-12 bg-gray-800 rounded-lg flex items-center justify-center mb-4">
                  <Monitor className="w-6 h-6 text-white" />
                </div>
                <CardTitle className="text-white text-xl">Diagnóstico Completo</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-400 leading-relaxed">
                  Análise detalhada de CPU, memória, disco e rede com métricas em tempo real e alertas inteligentes.
                </p>
              </CardContent>
            </Card>

            <Card className="bg-gray-900 border-gray-800 hover:border-gray-700 transition-colors">
              <CardHeader>
                <div className="w-12 h-12 bg-gray-800 rounded-lg flex items-center justify-center mb-4">
                  <FileText className="w-6 h-6 text-white" />
                </div>
                <CardTitle className="text-white text-xl">Relatórios Automáticos</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-400 leading-relaxed">
                  Geração automática de relatórios em PDF, HTML e JSON com recomendações e soluções.
                </p>
              </CardContent>
            </Card>

            <Card className="bg-gray-900 border-gray-800 hover:border-gray-700 transition-colors">
              <CardHeader>
                <div className="w-12 h-12 bg-gray-800 rounded-lg flex items-center justify-center mb-4">
                  <TrendingUp className="w-6 h-6 text-white" />
                </div>
                <CardTitle className="text-white text-xl">Análise de Saúde</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-400 leading-relaxed">
                  Score de saúde do sistema com tendências, alertas preventivos e previsões.
                </p>
              </CardContent>
            </Card>

            <Card className="bg-gray-900 border-gray-800 hover:border-gray-700 transition-colors">
              <CardHeader>
                <div className="w-12 h-12 bg-gray-800 rounded-lg flex items-center justify-center mb-4">
                  <Shield className="w-6 h-6 text-white" />
                </div>
                <CardTitle className="text-white text-xl">Segurança Avançada</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-400 leading-relaxed">
                  Detecção de vulnerabilidades, análise de antivírus e firewall com alertas de segurança.
                </p>
              </CardContent>
            </Card>

            <Card className="bg-gray-900 border-gray-800 hover:border-gray-700 transition-colors">
              <CardHeader>
                <div className="w-12 h-12 bg-gray-800 rounded-lg flex items-center justify-center mb-4">
                  <Users className="w-6 h-6 text-white" />
                </div>
                <CardTitle className="text-white text-xl">Multi-usuário</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-400 leading-relaxed">
                  Sistema com diferentes níveis de acesso para técnicos, supervisores e administradores.
                </p>
              </CardContent>
            </Card>

            <Card className="bg-gray-900 border-gray-800 hover:border-gray-700 transition-colors">
              <CardHeader>
                <div className="w-12 h-12 bg-gray-800 rounded-lg flex items-center justify-center mb-4">
                  <Zap className="w-6 h-6 text-white" />
                </div>
                <CardTitle className="text-white text-xl">Performance Otimizada</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-400 leading-relaxed">
                  Análise de performance em tempo real com sugestões de otimização automáticas.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Stores Section */}
      <section className="py-20 px-6 bg-gray-900">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h3 className="text-4xl font-bold text-white mb-4">
              Nossas Lojas
            </h3>
            <p className="text-xl text-gray-400">
              Parcerias estratégicas para soluções completas
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <Card className="bg-black border-gray-800 hover:border-gray-600 transition-colors">
              <CardHeader>
                <div className="flex items-center justify-between mb-4">
                  <CardTitle className="text-white text-xl">UlyTech</CardTitle>
                  <Badge className="bg-green-900 text-green-300 border-green-700">
                    Principal
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-gray-400 mb-6 leading-relaxed">
                  Loja principal de tecnologia com equipamentos de ponta e soluções completas.
                </p>
                <div className="flex items-center gap-2 text-green-400">
                  <CheckCircle className="w-5 h-5" />
                  <span className="font-medium">Ativa</span>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-black border-gray-800 hover:border-gray-600 transition-colors">
              <CardHeader>
                <CardTitle className="text-white text-xl mb-4">UtiliMix</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-400 mb-6 leading-relaxed">
                  Loja de utilitários diversos para casa e escritório com foco em produtividade.
                </p>
                <div className="flex items-center gap-2 text-green-400">
                  <CheckCircle className="w-5 h-5" />
                  <span className="font-medium">Ativa</span>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-black border-gray-800 hover:border-gray-600 transition-colors">
              <CardHeader>
                <CardTitle className="text-white text-xl mb-4">UsePrint</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-400 mb-6 leading-relaxed">
                  Especializada em impressão e suprimentos gráficos de alta qualidade.
                </p>
                <div className="flex items-center gap-2 text-green-400">
                  <CheckCircle className="w-5 h-5" />
                  <span className="font-medium">Ativa</span>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 px-6 bg-black">
        <div className="max-w-4xl mx-auto text-center">
          <h3 className="text-5xl font-bold text-white mb-6 leading-tight">
            Pronto para começar?
          </h3>
          <p className="text-xl text-gray-400 mb-10 leading-relaxed">
            Faça login ou crie sua conta para começar a usar o sistema de diagnóstico mais avançado do mercado.
          </p>
          <Button 
            size="lg"
            onClick={() => navigate("/auth")}
            className="bg-white text-black hover:bg-gray-100 px-10 py-6 text-lg font-semibold"
          >
            Acessar Sistema
            <ArrowRight className="w-6 h-6 ml-2" />
          </Button>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-800 bg-black py-12 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center gap-3 mb-4 md:mb-0">
              <div className="p-2 bg-gray-900 rounded-lg">
                <Wrench className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold text-white">TechRepair</span>
            </div>
            <p className="text-gray-400 text-center md:text-right">
              © 2024 TechRepair. Sistema de Diagnóstico Técnico.
              <br />
              <span className="text-sm">Todos os direitos reservados.</span>
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Index;
