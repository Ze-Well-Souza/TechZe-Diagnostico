
import React from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import { TechCard } from '@/components/ui/tech-card';
import { TechButton } from '@/components/ui/tech-button';
import { TechNavbar } from '@/components/layout/TechNavbar';
import { 
  Wrench,
  Monitor,
  FileText,
  TrendingUp,
  Shield,
  Users,
  Zap,
  ArrowRight,
  CheckCircle,
  Activity,
  Cpu,
  HardDrive,
  Wifi,
  BarChart3,
  Clock,
  Star
} from 'lucide-react';

const NewIndex: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuth();

  // Redirecionar se já logado
  if (user) {
    navigate('/dashboard');
    return null;
  }

  const features = [
    {
      icon: Monitor,
      title: 'Diagnóstico Completo',
      description: 'Análise detalhada de CPU, memória, disco e rede com métricas em tempo real',
      gradient: 'from-blue-500 to-cyan-500'
    },
    {
      icon: FileText,
      title: 'Relatórios Automáticos',
      description: 'Geração automática de relatórios em PDF, HTML e JSON com recomendações',
      gradient: 'from-green-500 to-emerald-500'
    },
    {
      icon: TrendingUp,
      title: 'Análise Preditiva',
      description: 'Score de saúde do sistema com tendências e previsões inteligentes',
      gradient: 'from-purple-500 to-pink-500'
    },
    {
      icon: Shield,
      title: 'Segurança Avançada',
      description: 'Detecção de vulnerabilidades e análise de segurança em tempo real',
      gradient: 'from-red-500 to-orange-500'
    },
    {
      icon: Users,
      title: 'Multi-usuário',
      description: 'Sistema com diferentes níveis de acesso para técnicos e administradores',
      gradient: 'from-indigo-500 to-blue-500'
    },
    {
      icon: Zap,
      title: 'Performance Otimizada',
      description: 'Análise de performance com sugestões de otimização automáticas',
      gradient: 'from-yellow-500 to-amber-500'
    }
  ];

  const stats = [
    { value: '99.9%', label: 'Precisão', icon: Activity },
    { value: '500+', label: 'Sistemas Analisados', icon: Monitor },
    { value: '24/7', label: 'Monitoramento', icon: Clock },
    { value: '5min', label: 'Diagnóstico Rápido', icon: Zap }
  ];

  const diagnosticSteps = [
    { icon: Cpu, title: 'CPU Analysis', description: 'Verificação de performance e temperatura' },
    { icon: HardDrive, title: 'Storage Check', description: 'Análise de discos e fragmentação' },
    { icon: Wifi, title: 'Network Test', description: 'Teste de conectividade e velocidade' },
    { icon: BarChart3, title: 'Report Generation', description: 'Geração de relatório completo' }
  ];

  return (
    <div className="min-h-screen bg-black font-display">
      <TechNavbar />
      
      {/* Hero Section */}
      <section className="relative pt-24 pb-20 px-6 overflow-hidden">
        {/* Background Effects */}
        <div className="absolute inset-0 bg-gradient-to-br from-blue-900/20 via-black to-green-900/20" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-blue-600/10 rounded-full blur-3xl animate-pulse" />
        
        <div className="relative max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
              className="mb-8"
            >
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-blue-600/20 border border-blue-500/30 mb-6">
                <Star className="w-4 h-4 text-blue-400" />
                <span className="text-blue-300 text-sm font-medium">Sistema de Diagnóstico v2.0</span>
              </div>
              
              <h1 className="text-5xl md:text-7xl font-bold text-white mb-6 leading-tight">
                Diagnóstico
                <span className="block bg-gradient-to-r from-blue-400 to-green-400 bg-clip-text text-transparent">
                  Técnico Avançado
                </span>
              </h1>
              
              <p className="text-xl text-gray-300 mb-10 max-w-3xl mx-auto leading-relaxed">
                Realize diagnósticos completos de hardware e software com IA, 
                gere relatórios detalhados e mantenha o controle total sobre a saúde dos sistemas.
              </p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="flex flex-col sm:flex-row gap-4 justify-center items-center"
            >
              <TechButton
                variant="primary"
                size="lg"
                icon={ArrowRight}
                onClick={() => navigate('/auth')}
                className="px-8 py-4 text-lg"
              >
                Começar Diagnóstico
              </TechButton>
              
              <TechButton
                variant="glass"
                size="lg"
                icon={Monitor}
                className="px-8 py-4 text-lg"
              >
                Ver Demo Interativa
              </TechButton>
            </motion.div>
          </div>

          {/* Demo Interactive Section */}
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
            className="max-w-4xl mx-auto"
          >
            <TechCard className="p-8" variant="glass">
              <div className="text-center mb-8">
                <h3 className="text-2xl font-bold text-white mb-2">Preview do Diagnóstico</h3>
                <p className="text-gray-400">Veja como funciona nosso sistema em tempo real</p>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                {diagnosticSteps.map((step, index) => {
                  const Icon = step.icon;
                  return (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ duration: 0.5, delay: 0.6 + index * 0.1 }}
                      className="text-center"
                    >
                      <div className="w-16 h-16 bg-gradient-to-r from-blue-600 to-green-600 rounded-full flex items-center justify-center mx-auto mb-4 animate-glow-pulse">
                        <Icon className="w-8 h-8 text-white" />
                      </div>
                      <h4 className="font-semibold text-white mb-2">{step.title}</h4>
                      <p className="text-sm text-gray-400">{step.description}</p>
                    </motion.div>
                  );
                })}
              </div>
            </TechCard>
          </motion.div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 px-6 bg-gray-900/50">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, index) => {
              const Icon = stat.icon;
              return (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 30 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: index * 0.1 }}
                  className="text-center"
                >
                  <Icon className="w-8 h-8 text-blue-400 mx-auto mb-4" />
                  <div className="text-3xl font-bold text-white mb-2">{stat.value}</div>
                  <div className="text-gray-400 text-sm">{stat.label}</div>
                </motion.div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-6">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center mb-16"
          >
            <h3 className="text-4xl font-bold text-white mb-4">
              Tecnologia de Ponta
            </h3>
            <p className="text-xl text-gray-400 max-w-2xl mx-auto">
              Recursos avançados para diagnóstico profissional e análise completa de sistemas
            </p>
          </motion.div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 30 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: index * 0.1 }}
                >
                  <TechCard className="h-full tech-hover">
                    <div className={`w-12 h-12 bg-gradient-to-r ${feature.gradient} rounded-lg flex items-center justify-center mb-6`}>
                      <Icon className="w-6 h-6 text-white" />
                    </div>
                    <h4 className="text-xl font-semibold text-white mb-4">{feature.title}</h4>
                    <p className="text-gray-400 leading-relaxed">{feature.description}</p>
                  </TechCard>
                </motion.div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Lojas Section */}
      <section className="py-20 px-6 bg-gray-900/30">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center mb-16"
          >
            <h3 className="text-4xl font-bold text-white mb-4">Nossas Lojas Parceiras</h3>
            <p className="text-xl text-gray-400">Parcerias estratégicas para soluções completas</p>
          </motion.div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              { name: 'UlyTech', type: 'Principal', description: 'Tecnologia de ponta e soluções completas' },
              { name: 'UtiliMix', type: 'Parceira', description: 'Utilitários diversos para casa e escritório' },
              { name: 'UsePrint', type: 'Parceira', description: 'Impressão e suprimentos gráficos' }
            ].map((store, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
              >
                <TechCard className="tech-hover">
                  <div className="flex items-center justify-between mb-4">
                    <h4 className="text-xl font-semibold text-white">{store.name}</h4>
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                      store.type === 'Principal' 
                        ? 'bg-green-600/20 text-green-400 border border-green-500/30'
                        : 'bg-blue-600/20 text-blue-400 border border-blue-500/30'
                    }`}>
                      {store.type}
                    </span>
                  </div>
                  <p className="text-gray-400 mb-6">{store.description}</p>
                  <div className="flex items-center gap-2 text-green-400">
                    <CheckCircle className="w-5 h-5" />
                    <span className="font-medium">Ativa</span>
                  </div>
                </TechCard>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 px-6 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-900/20 to-green-900/20" />
        <div className="relative max-w-4xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <h3 className="text-5xl font-bold text-white mb-6">
              Pronto para começar?
            </h3>
            <p className="text-xl text-gray-300 mb-10 leading-relaxed">
              Acesse o sistema de diagnóstico mais avançado do mercado e 
              revolucione a forma como você analisa e mantém seus equipamentos.
            </p>
            <TechButton
              variant="primary"
              size="lg"
              icon={ArrowRight}
              onClick={() => navigate('/auth')}
              className="px-10 py-4 text-lg animate-glow-pulse"
            >
              Acessar Sistema Agora
            </TechButton>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-800 py-12 px-6 bg-black">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center gap-3 mb-4 md:mb-0">
              <div className="p-2 bg-gradient-to-r from-blue-600 to-green-600 rounded-lg">
                <Wrench className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold text-white">TechRepair</span>
            </div>
            <div className="text-gray-400 text-center md:text-right">
              <p>© 2024 TechRepair. Sistema de Diagnóstico Técnico.</p>
              <p className="text-sm mt-1">Todos os direitos reservados.</p>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default NewIndex;
