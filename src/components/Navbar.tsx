
import { Button } from "@/components/ui/button";
import { useAuth } from "@/hooks/useAuth";
import { useNavigate, useLocation } from "react-router-dom";
import { 
  LogOut, 
  User, 
  Home, 
  Activity, 
  FileText, 
  History, 
  Settings,
  Wrench
} from "lucide-react";

const Navbar = () => {
  const { user, signOut } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = async () => {
    await signOut();
    navigate("/auth");
  };

  const navItems = [
    { path: "/dashboard", label: "Dashboard", icon: Home },
    { path: "/diagnostic", label: "Diagnóstico", icon: Activity },
    { path: "/reports", label: "Relatórios", icon: FileText },
    { path: "/history", label: "Histórico", icon: History },
    { path: "/admin", label: "Admin", icon: Settings },
  ];

  return (
    <nav className="bg-black/40 backdrop-blur-md border-b border-white/20 px-6 py-4">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-2">
            <Wrench className="w-6 h-6 text-white" />
            <span className="text-xl font-bold text-white">TecnoReparo</span>
          </div>
          
          <div className="hidden md:flex items-center gap-4">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              
              return (
                <Button
                  key={item.path}
                  variant="ghost"
                  size="sm"
                  onClick={() => navigate(item.path)}
                  className={`flex items-center gap-2 transition-all ${
                    isActive 
                      ? "bg-white/20 text-white border border-white/30" 
                      : "text-gray-300 hover:text-white hover:bg-white/10 hover:border hover:border-white/20"
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {item.label}
                </Button>
              );
            })}
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 text-white">
            <User className="w-4 h-4" />
            <span className="text-sm">{user?.email}</span>
          </div>
          
          <Button
            variant="ghost"
            size="sm"
            onClick={handleLogout}
            className="border border-white/30 text-white hover:bg-white/10 hover:border-white/50 transition-all"
          >
            <LogOut className="w-4 h-4 mr-2" />
            Sair
          </Button>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
