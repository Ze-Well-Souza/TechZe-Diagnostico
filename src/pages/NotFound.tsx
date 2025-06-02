import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Wrench, Home, ArrowLeft } from "lucide-react";

const NotFound = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-black flex items-center justify-center">
      {/* Header */}
      <div className="fixed top-0 left-0 right-0 border-b border-gray-800 bg-black z-50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-gray-900 rounded-lg">
              <Wrench className="w-6 h-6 text-white" />
            </div>
            <h1 className="text-2xl font-bold text-white">TechRepair</h1>
          </div>
          <Button 
            onClick={() => navigate("/")}
            className="bg-gray-800 hover:bg-gray-700 text-white border border-gray-700"
          >
            <Home className="w-4 h-4 mr-2" />
            Início
          </Button>
        </div>
      </div>

      {/* Main Content */}
      <div className="text-center px-6 pt-20">
        <div className="max-w-md mx-auto">
          <div className="mb-8">
            <div className="text-8xl font-bold text-gray-600 mb-4">404</div>
            <h2 className="text-3xl font-bold text-white mb-4">
              Página não encontrada
            </h2>
            <p className="text-xl text-gray-400 mb-8">
              A página que você está procurando não existe ou foi movida.
            </p>
          </div>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button 
              onClick={() => navigate(-1)}
              variant="outline"
              className="border-gray-700 text-gray-300 hover:bg-gray-800"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Voltar
            </Button>
            <Button 
              onClick={() => navigate("/")}
              className="bg-white text-black hover:bg-gray-100"
            >
              <Home className="w-4 h-4 mr-2" />
              Página Inicial
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NotFound;
