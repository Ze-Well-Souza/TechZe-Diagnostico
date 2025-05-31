
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
  Activity
} from "lucide-react";

const Index = () => {
  const navigate = useNavigate();
  const { user } = useAuth();

  // If user is logged in, redirect to welcome
  if (user) {
    navigate("/welcome");
    return null;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-black via-gray-900 to-black">
      {/* Header */}
      <header className="border-b border-white/20 bg-black/40 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Wrench className="w-8 h-8 text-white" />
            <h1 className="text-2xl font-bold text-white">TechRepair</h1>
          </div>
          <Button 
            onClick={() => navigate("/auth")}
            className="bg-gradient-to-r from-gray-600 to-gray-800 hover:from-gray-700 hover:to-gray-900"
          >
            Acessar Sistema
          </Button>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-20 px-6">
        <div className="max-w-7xl mx-auto text-center">
          <h2 className="text-5xl font-bold text-white mb-6">
            Sistema de Diagnóstico Técnico
          </h2>
          <p className="text-xl text-gray-300 mb-8 max-w-3xl mx-auto">
            Realize diagnósticos completos de hardware e software, gere relatórios detalhados 
            e mantenha o controle total sobre a saúde dos sistemas.
          </p>
          <div className="flex flex-wrap gap-4 justify-center">
            <Button 
              size="lg"
              onClick={() => navigate("/auth")}
              className="bg-gradient-to-r from-gray-600 to-gray-800 hover:from-gray-700 hover:to-gray-900"
            >
              Começar Agora
              <ArrowRight className="w-5 h-5 ml-2" />
            </Button>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16 px-6">
        <div className="max-w-7xl mx-auto">
          <h3 className="text-3xl font-bold text-white text-center mb-12">
            Funcionalidades Principais
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            <Card className="bg-black/40 backdrop-blur-md border-white/20">
              <CardHeader>
                <Monitor className="w-12 h-12 text-gray-400 mb-4" />
                <CardTitle className="text-white">Diagnóstico Completo</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-300">
                  Análise detalhada de CPU, memória, disco e rede com métricas em tempo real.
                </p>
              </CardContent>
            </Card>

            <Card className="bg-black/40 backdrop-blur-md border-white/20">
              <CardHeader>
                <FileText className="w-12 h-12 text-gray-400 mb-4" />
                <CardTitle className="text-white">Relatórios Automáticos</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-300">
                  Geração automática de relatórios em PDF, HTML e JSON com recomendações.
                </p>
              </CardContent>
            </Card>

            <Card className="bg-black/40 backdrop-blur-md border-white/20">
              <CardHeader>
                <Activity className="w-12 h-12 text-gray-400 mb-4" />
                <CardTitle className="text-white">Análise de Saúde</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-300">
                  Score de saúde do sistema com tendências e alertas preventivos.
                </p>
              </CardContent>
            </Card>

            <Card className="bg-black/40 backdrop-blur-md border-white/20">
              <CardHeader>
                <Users className="w-12 h-12 text-gray-400 mb-4" />
                <CardTitle className="text-white">Multi-usuário</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-300">
                  Sistema com diferentes níveis de acesso para técnicos e administradores.
                </p>
              </CardContent>
            </Card>

            <Card className="bg-black/40 backdrop-blur-md border-white/20">
              <CardHeader>
                <ShoppingBag className="w-12 h-12 text-gray-400 mb-4" />
                <CardTitle className="text-white">Marketplace</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-300">
                  Integração com marketplace para venda de produtos e serviços.
                </p>
              </CardContent>
            </Card>

            <Card className="bg-black/40 backdrop-blur-md border-white/20">
              <CardHeader>
                <Settings className="w-12 h-12 text-gray-400 mb-4" />
                <CardTitle className="text-white">Configuração Flexível</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-300">
                  Configuração personalizada para diferentes tipos de negócios.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Stores Section */}
      <section className="py-16 px-6 bg-black/20">
        <div className="max-w-7xl mx-auto">
          <h3 className="text-3xl font-bold text-white text-center mb-12">
            Nossas Lojas
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <Card className="bg-black/40 backdrop-blur-md border-white/20">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="text-white">UlyTech</CardTitle>
                  <Badge className="bg-green-500/20 text-green-300">Principal</Badge>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-gray-300 mb-4">
                  Loja principal de tecnologia com equipamentos de ponta.
                </p>
                <div className="flex items-center gap-2 text-green-400">
                  <CheckCircle className="w-4 h-4" />
                  <span className="text-sm">Ativa</span>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-black/40 backdrop-blur-md border-white/20">
              <CardHeader>
                <CardTitle className="text-white">UtiliMix</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-300 mb-4">
                  Loja de utilitários diversos para casa e escritório.
                </p>
                <div className="flex items-center gap-2 text-green-400">
                  <CheckCircle className="w-4 h-4" />
                  <span className="text-sm">Ativa</span>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-black/40 backdrop-blur-md border-white/20">
              <CardHeader>
                <CardTitle className="text-white">UsePrint</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-300 mb-4">
                  Especializada em impressão e suprimentos gráficos.
                </p>
                <div className="flex items-center gap-2 text-green-400">
                  <CheckCircle className="w-4 h-4" />
                  <span className="text-sm">Ativa</span>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <h3 className="text-4xl font-bold text-white mb-6">
            Pronto para começar?
          </h3>
          <p className="text-xl text-gray-300 mb-8">
            Faça login ou crie sua conta para começar a usar o sistema de diagnóstico.
          </p>
          <Button 
            size="lg"
            onClick={() => navigate("/auth")}
            className="bg-gradient-to-r from-gray-600 to-gray-800 hover:from-gray-700 hover:to-gray-900"
          >
            Acessar Sistema
            <ArrowRight className="w-5 h-5 ml-2" />
          </Button>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/20 bg-black/40 backdrop-blur-md py-8 px-6">
        <div className="max-w-7xl mx-auto text-center">
          <p className="text-gray-400">
            © 2024 TechRepair. Sistema de Diagnóstico Técnico.
          </p>
        </div>
      </footer>
    </div>
  );
};

export default Index;
