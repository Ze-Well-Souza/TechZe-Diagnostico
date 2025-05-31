
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/hooks/useAuth";
import { 
  Wrench, 
  CheckCircle, 
  Monitor,
  Activity,
  Star,
  ArrowRight
} from "lucide-react";

const Welcome = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [currentStep, setCurrentStep] = useState(0);

  const welcomeSteps = [
    {
      icon: Wrench,
      title: "Bem-vindo ao TechRepair!",
      description: "Sistema de diagnóstico técnico da Ulytech",
      color: "text-orange-500"
    },
    {
      icon: CheckCircle,
      title: "Você está conectado!",
      description: "Sua sessão foi iniciada com sucesso",
      color: "text-green-500"
    },
    {
      icon: Monitor,
      title: "Pronto para trabalhar!",
      description: "Vamos começar os diagnósticos?",
      color: "text-blue-500"
    }
  ];

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentStep((prev) => {
        if (prev < welcomeSteps.length - 1) {
          return prev + 1;
        }
        return prev;
      });
    }, 1500);

    return () => clearInterval(timer);
  }, []);

  const handleGetStarted = () => {
    navigate("/dashboard");
  };

  const currentWelcome = welcomeSteps[currentStep];
  const Icon = currentWelcome.icon;

  return (
    <div className="min-h-screen bg-gradient-to-br from-black via-gray-900 to-black flex items-center justify-center p-6">
      <div className="w-full max-w-2xl">
        <Card className="bg-black/40 backdrop-blur-md border-white/20 text-center overflow-hidden">
          <CardContent className="p-12">
            <div className="space-y-8">
              {/* Logo Animation */}
              <div className="flex items-center justify-center gap-3 mb-8">
                <div className="relative">
                  <Wrench className="w-16 h-16 text-orange-500 animate-pulse" />
                  <div className="absolute -top-2 -right-2">
                    <Star className="w-6 h-6 text-yellow-400 animate-bounce" />
                  </div>
                </div>
                <div>
                  <h1 className="text-4xl font-bold text-white">TechRepair</h1>
                  <p className="text-orange-400 text-sm">by Ulytech</p>
                </div>
              </div>

              {/* Welcome Animation */}
              <div className="space-y-6 min-h-[200px] flex flex-col justify-center">
                <div className="animate-fade-in">
                  <Icon className={`w-20 h-20 mx-auto mb-4 ${currentWelcome.color} animate-scale-in`} />
                </div>
                
                <div className="space-y-2 animate-fade-in">
                  <h2 className="text-3xl font-bold text-white">
                    {currentWelcome.title}
                  </h2>
                  <p className="text-xl text-gray-300">
                    {currentWelcome.description}
                  </p>
                </div>

                {user && (
                  <div className="animate-fade-in">
                    <p className="text-lg text-orange-400">
                      Olá, <span className="font-semibold">{user.email}</span>!
                    </p>
                  </div>
                )}
              </div>

              {/* Progress Indicators */}
              <div className="flex justify-center space-x-2 mb-8">
                {welcomeSteps.map((_, index) => (
                  <div
                    key={index}
                    className={`w-3 h-3 rounded-full transition-all duration-500 ${
                      index <= currentStep 
                        ? "bg-orange-500 scale-110" 
                        : "bg-white/20"
                    }`}
                  />
                ))}
              </div>

              {/* Action Buttons */}
              {currentStep >= welcomeSteps.length - 1 && (
                <div className="space-y-4 animate-fade-in">
                  <Button 
                    onClick={handleGetStarted}
                    size="lg"
                    className="btn-tecno w-full text-lg"
                  >
                    <Activity className="w-5 h-5 mr-2" />
                    Começar Diagnósticos
                    <ArrowRight className="w-5 h-5 ml-2" />
                  </Button>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <Button 
                      variant="outline" 
                      onClick={() => navigate("/reports")}
                      className="border-white/30 text-white hover:bg-white/10"
                    >
                      Ver Relatórios
                    </Button>
                    <Button 
                      variant="outline" 
                      onClick={() => navigate("/history")}
                      className="border-white/30 text-white hover:bg-white/10"
                    >
                      Histórico
                    </Button>
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Welcome;
