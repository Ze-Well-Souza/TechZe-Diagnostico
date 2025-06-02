
import React from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { 
  Wrench, 
  Monitor, 
  FileText, 
  Users, 
  ArrowRight,
  CheckCircle,
  TrendingUp,
  Shield,
  Zap,
  Activity
} from 'lucide-react';

const HomePage: React.FC = () => {
  const navigate = useNavigate();

  // Animação de curto-circuito para os botões
  const shortCircuitAnimation = {
    initial: { 
      boxShadow: "0 0 0px rgba(14, 165, 233, 0)",
      background: "linear-gradient(135deg, #1f2937 0%, #374151 100%)"
    },
    hover: {
      boxShadow: [
        "0 0 20px rgba(14, 165, 233, 0.5)",
        "0 0 40px rgba(16, 185, 129, 0.7)",
        "0 0 60px rgba(239, 68, 68, 0.5)",
        "0 0 20px rgba(14, 165, 233, 0.8)"
      ],
      background: [
        "linear-gradient(135deg, #1f2937 0%, #374151 100%)",
        "linear-gradient(135deg, #0ea5e9 0%, #10b981 100%)",
        "linear-gradient(135deg, #ef4444 0%, #f59e0b 100%)",
        "linear-gradient(135deg, #0ea5e9 0%, #10b981 100%)"
      ],
      transition: {
        duration: 0.6,
        repeat: Infinity,
        repeatType: "reverse" as const
      }
    },
    tap: {
      scale: 0.95,
      boxShadow: "0 0 80px rgba(14, 165, 233, 1)"
    }
  };

  return (
    <div className="min-h-screen bg-black text-white">
      {/* Header */}
      <header className="border-b border-gray-800 bg-black/95 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <motion.div 
            className="flex items-center gap-3"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6 }}
          >
            <div className="p-2 bg-gradient-to-r from-blue-600 to-green-600 rounded-lg">
              <Wrench className="w-6 h-6 text-white" />
            </div>
            <h1 className="text-2xl font-bold text-white">TechRepair</h1>
          </motion.div>
          
          <motion.button
            className="px-6 py-2 bg-gray-800 hover:bg-gray-700 text-white border border-gray-700 rounded-lg transition-colors"
            onClick={() => navigate("/auth")}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            Fazer Login
          </motion.button>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-24 px-6 bg-gradient-to-b from-black via-gray-900 to-black">
        <div className="max-w-7xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="mb-8"
          >
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-blue-600/20 border border-blue-500/30 mb-6">
              <Zap className="w-4 h-4 text-blue-400" />
              <span className="text-blue-300 text-sm font-medium">Sistema de Diagnóstico v2.0</span>
            </div>
            
            <h2 className="text-6xl font-bold text-white mb-6 leading-tight">
              Sistema de Diagnóstico
              <span className="block bg-gradient-to-r from-blue-400 to-green-400 bg-clip-text text-transparent">
                Técnico Avançado
              </span>
            </h2>
            
            <p className="text-xl text-gray-300 mb-10 max-w-3xl mx-auto leading-relaxed">
              Realize diagnósticos completos de hardware e software com IA, 
              gere relatórios detalhados e mantenha o controle total sobre a saúde dos sistemas.
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="flex flex-col sm:flex-row gap-6 justify-center items-center"
          >
            {/* Botão Começar Agora com animação de curto-circuito */}
            <motion.button
              className="px-8 py-4 text-lg font-semibold text-white rounded-lg flex items-center gap-3 relative overflow-hidden"
              onClick={() => navigate('/auth')}
              variants={shortCircuitAnimation}
              initial="initial"
              whileHover="hover"
              whileTap="tap"
            >
              <span className="relative z-10">Começar Agora</span>
              <ArrowRight className="w-5 h-5 relative z-10" />
              
              {/* Efeito de raios */}
              <motion.div
                className="absolute inset-0 opacity-30"
                style={{
                  background: "radial-gradient(circle at 50% 50%, rgba(14, 165, 233, 0.3) 0%, transparent 70%)"
                }}
                animate={{
                  scale: [1, 1.2, 1],
                  opacity: [0.3, 0.7, 0.3]
                }}
                transition={{
                  duration: 1.5,
                  repeat: Infinity,
                  ease: "easeInOut"
                }}
              />
            </motion.button>
            
            {/* Botão Acessar Sistema com animação de curto-circuito */}
            <motion.button
              className="px-8 py-4 text-lg font-semibold text-gray-300 border border-gray-600 rounded-lg flex items-center gap-3 relative overflow-hidden"
              onClick={() => navigate('/auth')}
              variants={shortCircuitAnimation}
              initial="initial"
              whileHover="hover"
              whileTap="tap"
            >
              <span className="relative z-10">Acessar Sistema</span>
              <Monitor className="w-5 h-5 relative z-10" />
              
              {/* Efeito de raios */}
              <motion.div
                className="absolute inset-0 opacity-20"
                style={{
                  background: "radial-gradient(circle at 50% 50%, rgba(16, 185, 129, 0.3) 0%, transparent 70%)"
                }}
                animate={{
                  scale: [1, 1.2, 1],
                  opacity: [0.2, 0.6, 0.2]
                }}
                transition={{
                  duration: 1.8,
                  repeat: Infinity,
                  ease: "easeInOut",
                  delay: 0.5
                }}
              />
            </motion.button>
          </motion.div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 px-6 bg-gray-900/50">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            {[
              { value: '99.9%', label: 'Precisão', icon: Activity },
              { value: '500+', label: 'Sistemas Analisados', icon: Monitor },
              { value: '24/7', label: 'Monitoramento', icon: Shield },
              { value: '5min', label: 'Diagnóstico Rápido', icon: Zap }
            ].map((stat, index) => {
              const Icon = stat.icon;
              return (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: index * 0.1 }}
                  className="text-center"
                >
                  <Icon className="w-8 h-8 text-blue-400 mx-auto mb-4" />
                  <div className="text-3xl font-bold text-white mb-2">{stat.value}</div>
                  <div className="text-gray-400">{stat.label}</div>
                </motion.div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-6 bg-black">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center mb-16"
          >
            <h3 className="text-4xl font-bold text-white mb-4">
              Funcionalidades Principais
            </h3>
            <p className="text-xl text-gray-400 max-w-2xl mx-auto">
              Tudo que você precisa para manter seus sistemas funcionando perfeitamente
            </p>
          </motion.div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              {
                icon: Monitor,
                title: 'Diagnóstico Completo',
                description: 'Análise detalhada de CPU, memória, disco e rede com métricas em tempo real'
              },
              {
                icon: FileText,
                title: 'Relatórios Automáticos',
                description: 'Geração automática de relatórios em PDF, HTML e JSON com recomendações'
              },
              {
                icon: TrendingUp,
                title: 'Análise de Saúde',
                description: 'Score de saúde do sistema com tendências, alertas preventivos e previsões'
              },
              {
                icon: Shield,
                title: 'Segurança Avançada',
                description: 'Detecção de vulnerabilidades, análise de antivírus e firewall'
              },
              {
                icon: Users,
                title: 'Multi-usuário',
                description: 'Sistema com diferentes níveis de acesso para técnicos e administradores'
              },
              {
                icon: Zap,
                title: 'Performance Otimizada',
                description: 'Análise de performance com sugestões de otimização automáticas'
              }
            ].map((feature, index) => {
              const Icon = feature.icon;
              return (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 30 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: index * 0.1 }}
                  className="bg-gray-900 border border-gray-800 rounded-xl p-6 hover:border-gray-700 transition-all duration-300 hover:transform hover:scale-105"
                >
                  <div className="w-12 h-12 bg-gray-800 rounded-lg flex items-center justify-center mb-4">
                    <Icon className="w-6 h-6 text-white" />
                  </div>
                  <h4 className="text-xl font-semibold text-white mb-3">{feature.title}</h4>
                  <p className="text-gray-400 leading-relaxed">{feature.description}</p>
                </motion.div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Stores Section */}
      <section className="py-20 px-6 bg-gray-900">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center mb-16"
          >
            <h3 className="text-4xl font-bold text-white mb-4">Nossas Lojas</h3>
            <p className="text-xl text-gray-400">Parcerias estratégicas para soluções completas</p>
          </motion.div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              { name: 'UlyTech', type: 'Principal', description: 'Loja principal de tecnologia com equipamentos de ponta' },
              { name: 'UtiliMix', type: 'Parceira', description: 'Loja de utilitários diversos para casa e escritório' },
              { name: 'UsePrint', type: 'Parceira', description: 'Especializada em impressão e suprimentos gráficos' }
            ].map((store, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                className="bg-black border border-gray-800 rounded-xl p-6 hover:border-gray-600 transition-colors"
              >
                <div className="flex items-center justify-between mb-4">
                  <h4 className="text-xl font-semibold text-white">{store.name}</h4>
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                    store.type === 'Principal' 
                      ? 'bg-green-900 text-green-300 border border-green-700'
                      : 'bg-blue-900 text-blue-300 border border-blue-700'
                  }`}>
                    {store.type}
                  </span>
                </div>
                <p className="text-gray-400 mb-6">{store.description}</p>
                <div className="flex items-center gap-2 text-green-400">
                  <CheckCircle className="w-5 h-5" />
                  <span className="font-medium">Ativa</span>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 px-6 bg-black">
        <div className="max-w-4xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <h3 className="text-5xl font-bold text-white mb-6">
              Pronto para começar?
            </h3>
            <p className="text-xl text-gray-400 mb-10">
              Faça login ou crie sua conta para começar a usar o sistema de diagnóstico mais avançado do mercado.
            </p>
            
            <motion.button
              className="px-10 py-4 text-lg font-semibold text-white rounded-lg flex items-center gap-3 mx-auto relative overflow-hidden"
              onClick={() => navigate('/auth')}
              variants={shortCircuitAnimation}
              initial="initial"
              whileHover="hover"
              whileTap="tap"
            >
              <span className="relative z-10">Acessar Sistema</span>
              <ArrowRight className="w-6 h-6 relative z-10" />
              
              {/* Efeito de raios intenso */}
              <motion.div
                className="absolute inset-0 opacity-40"
                style={{
                  background: "radial-gradient(circle at 50% 50%, rgba(14, 165, 233, 0.4) 0%, transparent 70%)"
                }}
                animate={{
                  scale: [1, 1.3, 1],
                  opacity: [0.4, 0.8, 0.4]
                }}
                transition={{
                  duration: 1.2,
                  repeat: Infinity,
                  ease: "easeInOut"
                }}
              />
            </motion.button>
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

export default HomePage;
