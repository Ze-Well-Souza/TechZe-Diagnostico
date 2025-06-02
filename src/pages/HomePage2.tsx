
import React from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { 
  Cpu, 
  Shield, 
  Zap, 
  Monitor,
  HardDrive,
  Wifi,
  Battery,
  TrendingUp,
  CheckCircle,
  ArrowRight,
  Play,
  Star,
  Users
} from 'lucide-react';

const HomePage2: React.FC = () => {
  const navigate = useNavigate();

  // Animação de curto-circuito para os botões
  const circuitAnimation = {
    initial: { 
      boxShadow: "0 0 0px rgba(59, 130, 246, 0)",
      background: "linear-gradient(135deg, #1e293b 0%, #334155 100%)"
    },
    hover: {
      boxShadow: [
        "0 0 20px rgba(59, 130, 246, 0.6)",
        "0 0 40px rgba(34, 197, 94, 0.8)",
        "0 0 60px rgba(239, 68, 68, 0.6)",
        "0 0 20px rgba(59, 130, 246, 0.8)"
      ],
      background: [
        "linear-gradient(135deg, #1e293b 0%, #334155 100%)",
        "linear-gradient(135deg, #3b82f6 0%, #22c55e 100%)",
        "linear-gradient(135deg, #ef4444 0%, #f59e0b 100%)",
        "linear-gradient(135deg, #3b82f6 0%, #22c55e 100%)"
      ],
      transition: {
        duration: 0.8,
        repeat: Infinity,
        repeatType: "reverse" as const
      }
    },
    tap: {
      scale: 0.96,
      boxShadow: "0 0 100px rgba(59, 130, 246, 1)"
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-black to-gray-900 text-white overflow-hidden">
      {/* Particles Background */}
      <div className="absolute inset-0 opacity-20">
        {[...Array(50)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-1 h-1 bg-blue-400 rounded-full"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
            }}
            animate={{
              opacity: [0, 1, 0],
              scale: [0, 1, 0],
            }}
            transition={{
              duration: Math.random() * 3 + 2,
              repeat: Infinity,
              delay: Math.random() * 2,
            }}
          />
        ))}
      </div>

      {/* Header */}
      <header className="relative z-10 border-b border-gray-800/50 bg-black/20 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <motion.div 
            className="flex items-center gap-3"
            initial={{ opacity: 0, x: -30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8 }}
          >
            <div className="p-2 bg-gradient-to-r from-blue-500 to-green-500 rounded-xl">
              <Cpu className="w-8 h-8 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-green-400 bg-clip-text text-transparent">
                TechRepair
              </h1>
              <p className="text-xs text-gray-400">Diagnostic System v2.0</p>
            </div>
          </motion.div>
          
          <motion.button
            className="px-6 py-3 bg-slate-800/80 hover:bg-slate-700/80 text-white border border-slate-600 rounded-xl transition-all duration-300 backdrop-blur-sm"
            onClick={() => navigate("/auth")}
            initial={{ opacity: 0, x: 30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8 }}
            whileHover={{ scale: 1.05, y: -2 }}
            whileTap={{ scale: 0.95 }}
          >
            Login
          </motion.button>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative z-10 pt-20 pb-32 px-6">
        <div className="max-w-6xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 1 }}
            className="mb-8"
          >
            <div className="inline-flex items-center gap-2 px-6 py-3 rounded-full bg-blue-500/20 border border-blue-500/30 mb-8">
              <Zap className="w-5 h-5 text-blue-400" />
              <span className="text-blue-300 font-medium">Advanced AI Diagnostics</span>
            </div>
            
            <h2 className="text-7xl font-bold mb-6 leading-tight">
              <span className="text-white">Sistema de</span>
              <br />
              <span className="bg-gradient-to-r from-blue-400 via-purple-400 to-green-400 bg-clip-text text-transparent">
                Diagnóstico Técnico
              </span>
            </h2>
            
            <p className="text-2xl text-gray-300 mb-12 max-w-4xl mx-auto leading-relaxed">
              Revolucione seus diagnósticos com IA avançada. Detecte problemas,
              analise performance e otimize sistemas em tempo real.
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 1, delay: 0.3 }}
            className="flex flex-col sm:flex-row gap-6 justify-center items-center mb-16"
          >
            {/* Botão Começar Agora com animação de curto-circuito */}
            <motion.button
              className="px-10 py-5 text-xl font-bold text-white rounded-2xl flex items-center gap-4 relative overflow-hidden shadow-2xl"
              onClick={() => navigate('/auth')}
              variants={circuitAnimation}
              initial="initial"
              whileHover="hover"
              whileTap="tap"
            >
              <span className="relative z-10 flex items-center gap-3">
                <Play className="w-6 h-6" />
                Começar Agora
              </span>
              
              {/* Efeito de energia elétrica */}
              <motion.div
                className="absolute inset-0 opacity-30"
                style={{
                  background: "radial-gradient(circle at 50% 50%, rgba(59, 130, 246, 0.4) 0%, transparent 70%)"
                }}
                animate={{
                  scale: [1, 1.3, 1],
                  opacity: [0.3, 0.8, 0.3]
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
              className="px-10 py-5 text-xl font-bold text-white border-2 border-slate-600 rounded-2xl flex items-center gap-4 relative overflow-hidden backdrop-blur-sm"
              onClick={() => navigate('/auth')}
              variants={circuitAnimation}
              initial="initial"
              whileHover="hover"
              whileTap="tap"
            >
              <span className="relative z-10 flex items-center gap-3">
                <Monitor className="w-6 h-6" />
                Acessar Sistema
              </span>
              
              {/* Efeito de energia elétrica */}
              <motion.div
                className="absolute inset-0 opacity-20"
                style={{
                  background: "radial-gradient(circle at 50% 50%, rgba(34, 197, 94, 0.4) 0%, transparent 70%)"
                }}
                animate={{
                  scale: [1, 1.3, 1],
                  opacity: [0.2, 0.7, 0.2]
                }}
                transition={{
                  duration: 1.8,
                  repeat: Infinity,
                  ease: "easeInOut",
                  delay: 0.8
                }}
              />
            </motion.button>
          </motion.div>

          {/* Demo Preview */}
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 1, delay: 0.6 }}
            className="bg-gradient-to-br from-slate-800/50 to-slate-900/50 rounded-3xl p-8 backdrop-blur-sm border border-slate-700/50 shadow-2xl"
          >
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-8">
              {[
                { icon: Cpu, label: "CPU", value: "98%", color: "text-green-400" },
                { icon: HardDrive, label: "Storage", value: "76%", color: "text-blue-400" },
                { icon: Wifi, label: "Network", value: "92%", color: "text-purple-400" },
                { icon: Battery, label: "Health", value: "85%", color: "text-yellow-400" }
              ].map((stat, index) => {
                const Icon = stat.icon;
                return (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.6, delay: 0.8 + index * 0.1 }}
                    className="text-center"
                  >
                    <Icon className={`w-10 h-10 mx-auto mb-3 ${stat.color}`} />
                    <div className={`text-2xl font-bold ${stat.color} mb-1`}>{stat.value}</div>
                    <div className="text-gray-400 text-sm">{stat.label}</div>
                  </motion.div>
                );
              })}
            </div>
            <p className="text-gray-300 text-lg">
              Visualização em tempo real do status do sistema
            </p>
          </motion.div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="relative z-10 py-20 px-6 bg-black/20">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center mb-16"
          >
            <h3 className="text-5xl font-bold text-white mb-6">
              Tecnologia de Ponta
            </h3>
            <p className="text-xl text-gray-400 max-w-3xl mx-auto">
              Ferramentas avançadas para diagnósticos precisos e soluções eficazes
            </p>
          </motion.div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              {
                icon: Shield,
                title: 'Diagnóstico IA',
                description: 'Análise inteligente com machine learning para detecção precisa de problemas',
                color: 'from-blue-500 to-cyan-500'
              },
              {
                icon: TrendingUp,
                title: 'Analytics Avançado',
                description: 'Métricas detalhadas e insights profundos sobre performance do sistema',
                color: 'from-green-500 to-emerald-500'
              },
              {
                icon: Zap,
                title: 'Tempo Real',
                description: 'Monitoramento contínuo com alertas instantâneos e respostas rápidas',
                color: 'from-purple-500 to-pink-500'
              }
            ].map((feature, index) => {
              const Icon = feature.icon;
              return (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 30 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: index * 0.2 }}
                  className="bg-gradient-to-br from-slate-800/60 to-slate-900/60 rounded-2xl p-8 backdrop-blur-sm border border-slate-700/50 hover:border-slate-600 transition-all duration-300 group hover:transform hover:scale-105"
                >
                  <div className={`w-16 h-16 bg-gradient-to-r ${feature.color} rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300`}>
                    <Icon className="w-8 h-8 text-white" />
                  </div>
                  <h4 className="text-2xl font-bold text-white mb-4">{feature.title}</h4>
                  <p className="text-gray-400 leading-relaxed">{feature.description}</p>
                </motion.div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="relative z-10 py-16 px-6">
        <div className="max-w-6xl mx-auto">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            {[
              { value: '99.9%', label: 'Precisão', icon: CheckCircle },
              { value: '1M+', label: 'Diagnósticos', icon: Monitor },
              { value: '24/7', label: 'Suporte', icon: Shield },
              { value: '500+', label: 'Clientes', icon: Users }
            ].map((stat, index) => {
              const Icon = stat.icon;
              return (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.6, delay: index * 0.1 }}
                  className="text-center"
                >
                  <Icon className="w-12 h-12 text-blue-400 mx-auto mb-4" />
                  <div className="text-4xl font-bold text-white mb-2">{stat.value}</div>
                  <div className="text-gray-400 text-lg">{stat.label}</div>
                </motion.div>
              );
            })}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="relative z-10 py-24 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <h3 className="text-6xl font-bold text-white mb-8">
              Experimente Agora
            </h3>
            <p className="text-2xl text-gray-400 mb-12">
              Transforme seu processo de diagnóstico técnico hoje mesmo
            </p>
            
            <motion.button
              className="px-12 py-6 text-2xl font-bold text-white rounded-2xl flex items-center gap-4 mx-auto relative overflow-hidden shadow-2xl"
              onClick={() => navigate('/auth')}
              variants={circuitAnimation}
              initial="initial"
              whileHover="hover"
              whileTap="tap"
            >
              <span className="relative z-10 flex items-center gap-4">
                Iniciar Diagnóstico
                <ArrowRight className="w-8 h-8" />
              </span>
              
              {/* Efeito de energia elétrica intenso */}
              <motion.div
                className="absolute inset-0 opacity-40"
                style={{
                  background: "radial-gradient(circle at 50% 50%, rgba(59, 130, 246, 0.5) 0%, transparent 70%)"
                }}
                animate={{
                  scale: [1, 1.4, 1],
                  opacity: [0.4, 0.9, 0.4]
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
      <footer className="relative z-10 border-t border-gray-800/50 py-12 px-6 bg-black/30 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center gap-3 mb-6 md:mb-0">
              <div className="p-2 bg-gradient-to-r from-blue-500 to-green-500 rounded-xl">
                <Cpu className="w-6 h-6 text-white" />
              </div>
              <div>
                <span className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-green-400 bg-clip-text text-transparent">
                  TechRepair
                </span>
                <p className="text-xs text-gray-500">Diagnostic System</p>
              </div>
            </div>
            <div className="text-center md:text-right">
              <p className="text-gray-400">
                © 2024 TechRepair. Sistema de Diagnóstico Técnico Avançado.
              </p>
              <div className="flex items-center justify-center md:justify-end gap-2 mt-2">
                {[...Array(5)].map((_, i) => (
                  <Star key={i} className="w-4 h-4 text-yellow-400 fill-current" />
                ))}
                <span className="text-sm text-gray-500 ml-2">Avaliado por especialistas</span>
              </div>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default HomePage2;
