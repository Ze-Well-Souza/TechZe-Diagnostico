
import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Separator } from '@/components/ui/separator';
import { Cpu, Zap, Eye, EyeOff, Building2 } from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';

export default function Auth() {
  const [isLogin, setIsLogin] = useState(true);
  const [showPassword, setShowPassword] = useState(false);
  const [selectedCompany, setSelectedCompany] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  const { user, signIn, signUp } = useAuth();
  const navigate = useNavigate();

  // Redirect if already authenticated
  useEffect(() => {
    if (user) {
      navigate('/dashboard');
    }
  }, [user, navigate]);

  // Mock data - será substituído pela integração com Supabase
  const companies = [
    { id: '1', name: 'UlyTech Informática', code: 'ULYTECH' },
    { id: '2', name: 'TechFix Solutions', code: 'TECHFIX' },
    { id: '3', name: 'InfoRepair Pro', code: 'INFOREPAIR' }
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!email || !password || !selectedCompany) {
      return;
    }

    if (!isLogin && password !== confirmPassword) {
      return;
    }

    setIsLoading(true);
    
    try {
      if (isLogin) {
        await signIn(email, password);
      } else {
        await signUp(email, password, {
          company_id: selectedCompany,
          company_name: companies.find(c => c.id === selectedCompany)?.name || ''
        });
      }
    } catch (error) {
      console.error('Auth error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-black flex items-center justify-center px-4">
      {/* Background Effects */}
      <div className="absolute inset-0">
        <div className="absolute top-1/4 right-1/4 w-96 h-96 bg-electric/5 rounded-full blur-3xl"></div>
        <div className="absolute bottom-1/4 left-1/4 w-96 h-96 bg-tech/5 rounded-full blur-3xl"></div>
      </div>

      <div className="w-full max-w-md relative">
        {/* Logo */}
        <div className="text-center mb-8">
          <Link to="/" className="inline-flex items-center space-x-2">
            <div className="relative">
              <Cpu className="h-10 w-10 text-electric" />
              <Zap className="h-5 w-5 text-tech absolute -top-1 -right-1" />
            </div>
            <span className="text-2xl font-bold gradient-text">TechRepair Pro</span>
          </Link>
        </div>

        <Card className="glass-effect border-white/10">
          <CardHeader className="space-y-1 text-center">
            <CardTitle className="text-2xl text-white">
              {isLogin ? 'Fazer Login' : 'Criar Conta'}
            </CardTitle>
            <CardDescription className="text-gray-400">
              {isLogin 
                ? 'Acesse sua conta para continuar' 
                : 'Crie sua conta para começar'
              }
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <form className="space-y-4" onSubmit={handleSubmit}>
              {/* Seleção de Empresa */}
              <div className="space-y-2">
                <Label htmlFor="company" className="text-white">Empresa</Label>
                <Select value={selectedCompany} onValueChange={setSelectedCompany}>
                  <SelectTrigger className="bg-dark/50 border-white/20 text-white">
                    <div className="flex items-center">
                      <Building2 className="mr-2 h-4 w-4 text-electric" />
                      <SelectValue placeholder="Selecione sua empresa" />
                    </div>
                  </SelectTrigger>
                  <SelectContent className="bg-dark border-white/20">
                    {companies.map((company) => (
                      <SelectItem key={company.id} value={company.id} className="text-white hover:bg-white/10">
                        <div className="flex flex-col">
                          <span>{company.name}</span>
                          <span className="text-xs text-gray-400">{company.code}</span>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Email */}
              <div className="space-y-2">
                <Label htmlFor="email" className="text-white">Email</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="seu@email.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="bg-dark/50 border-white/20 text-white placeholder:text-gray-400"
                  required
                />
              </div>

              {/* Password */}
              <div className="space-y-2">
                <Label htmlFor="password" className="text-white">Senha</Label>
                <div className="relative">
                  <Input
                    id="password"
                    type={showPassword ? "text" : "password"}
                    placeholder="••••••••"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="bg-dark/50 border-white/20 text-white placeholder:text-gray-400 pr-10"
                    required
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    {showPassword ? (
                      <EyeOff className="h-4 w-4 text-gray-400" />
                    ) : (
                      <Eye className="h-4 w-4 text-gray-400" />
                    )}
                  </Button>
                </div>
              </div>

              {/* Confirm Password for Register */}
              {!isLogin && (
                <div className="space-y-2">
                  <Label htmlFor="confirmPassword" className="text-white">Confirmar Senha</Label>
                  <Input
                    id="confirmPassword"
                    type="password"
                    placeholder="••••••••"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    className="bg-dark/50 border-white/20 text-white placeholder:text-gray-400"
                    required
                  />
                </div>
              )}

              {/* Submit Button */}
              <Button 
                type="submit" 
                disabled={isLoading || !email || !password || !selectedCompany || (!isLogin && password !== confirmPassword)}
                className="w-full bg-gradient-to-r from-electric to-tech hover:from-electric/80 hover:to-tech/80 text-black font-semibold disabled:opacity-50"
              >
                {isLoading ? 'Carregando...' : (isLogin ? 'Entrar' : 'Criar Conta')}
              </Button>
            </form>

            <Separator className="bg-white/10" />

            {/* Toggle Login/Register */}
            <div className="text-center">
              <span className="text-gray-400">
                {isLogin ? 'Não tem uma conta?' : 'Já tem uma conta?'}
              </span>
              <Button
                variant="link"
                className="text-electric hover:text-electric/80 p-0 ml-1"
                onClick={() => setIsLogin(!isLogin)}
              >
                {isLogin ? 'Criar conta' : 'Fazer login'}
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
