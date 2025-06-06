import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Loader2, 
  Monitor, 
  Eye, 
  EyeOff, 
  LogIn,
  Building2,
  Shield,
  Smartphone,
  Wifi,
  AlertTriangle,
  CheckCircle2
} from 'lucide-react';

export default function Auth() {
  const { signIn, signUp } = useAuth();
  const navigate = useNavigate();
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [companyName, setCompanyName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showSystemStatus, setShowSystemStatus] = useState(true);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      if (isLogin) {
        await signIn(email, password);
      } else {
        if (!companyName.trim()) {
          setError('Nome da empresa é obrigatório');
          return;
        }
        await signUp(email, password, companyName);
      }
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.message || 'Erro ao fazer login');
    } finally {
      setLoading(false);
    }
  };

  const quickAccess = [
    { email: 'loja1@techze.com', password: 'demo123', name: 'Loja Centro' },
    { email: 'loja2@techze.com', password: 'demo123', name: 'Loja Shopping' }
  ];

  const fillQuickAccess = (cred: typeof quickAccess[0]) => {
    setEmail(cred.email);
    setPassword(cred.password);
    setIsLogin(true);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-tech-darker to-tech-dark flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo e Título */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center mb-4">
            <div className="p-4 rounded-full bg-primary/10 electric-glow">
              <Monitor className="h-12 w-12 text-electric" />
            </div>
          </div>
          <h1 className="tech-font text-3xl font-bold neon-text mb-2">
            TechZe Diagnóstico
          </h1>
          <p className="text-sm text-muted-foreground">
            Sistema Profissional de Diagnóstico para Assistências Técnicas
          </p>
        </div>

        {/* Status do Sistema - Mais visível */}
        {showSystemStatus && (
          <Card className="card-electric mb-6">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm font-medium">Status do Sistema</CardTitle>
                <Button 
                  variant="ghost" 
                  size="sm" 
                  onClick={() => setShowSystemStatus(false)}
                  className="h-6 w-6 p-0"
                >
                  ✕
                </Button>
              </div>
            </CardHeader>
            <CardContent className="pt-0">
              <div className="space-y-2">
                <div className="flex items-center space-x-2">
                  <CheckCircle2 className="h-4 w-4 text-green-400" />
                  <span className="text-sm">Servidor Online</span>
                </div>
                <div className="flex items-center space-x-2">
                  <CheckCircle2 className="h-4 w-4 text-green-400" />
                  <span className="text-sm">Banco de Dados Conectado</span>
                </div>
                <div className="flex items-center space-x-2">
                  <CheckCircle2 className="h-4 w-4 text-green-400" />
                  <span className="text-sm">IA de Diagnóstico Ativa</span>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Formulário de Login */}
        <Card className="card-electric">
          <CardHeader className="text-center">
            <CardTitle className="flex items-center justify-center space-x-2">
              <LogIn className="h-5 w-5 text-electric" />
              <span>{isLogin ? 'Entrar no Sistema' : 'Cadastrar Nova Loja'}</span>
            </CardTitle>
            <CardDescription>
              {isLogin 
                ? 'Acesse seu painel de controle técnico'
                : 'Registre sua assistência técnica'
              }
            </CardDescription>
          </CardHeader>

          <CardContent className="space-y-4">
            <form onSubmit={handleSubmit} className="space-y-4">
              {!isLogin && (
                <div className="space-y-2">
                  <Label htmlFor="companyName" className="text-sm font-medium">
                    Nome da Empresa/Loja *
                  </Label>
                  <div className="relative">
                    <Building2 className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                      id="companyName"
                      type="text"
                      placeholder="Ex: TechFix - Assistência Técnica"
                      value={companyName}
                      onChange={(e) => setCompanyName(e.target.value)}
                      className="pl-10 electric-border"
                      disabled={loading}
                      required={!isLogin}
                    />
                  </div>
                </div>
              )}

              <div className="space-y-2">
                <Label htmlFor="email" className="text-sm font-medium">
                  Email do Técnico/Gerente *
                </Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="tecnico@minhaloja.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="electric-border"
                  disabled={loading}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="password" className="text-sm font-medium">
                  Senha *
                </Label>
                <div className="relative">
                  <Input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    placeholder="Sua senha segura"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="pr-10 electric-border"
                    disabled={loading}
                    required
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                  >
                    {showPassword ? (
                      <EyeOff className="h-4 w-4 text-muted-foreground" />
                    ) : (
                      <Eye className="h-4 w-4 text-muted-foreground" />
                    )}
                  </Button>
                </div>
              </div>

              {error && (
                <Alert className="bg-red-900/20 border-red-900/50">
                  <AlertTriangle className="h-4 w-4" />
                  <AlertDescription className="text-red-400">
                    {error}
                  </AlertDescription>
                </Alert>
              )}

              <Button
                type="submit"
                disabled={loading}
                className="w-full btn-electric tech-font font-semibold"
                size="lg"
              >
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                    {isLogin ? 'Entrando...' : 'Cadastrando...'}
                  </>
                ) : (
                  <>
                    <LogIn className="mr-2 h-5 w-5" />
                    {isLogin ? 'Entrar na Plataforma' : 'Cadastrar Minha Loja'}
                  </>
                )}
              </Button>
            </form>

            <div className="text-center">
              <Button
                variant="link"
                onClick={() => {
                  setIsLogin(!isLogin);
                  setError('');
                  setCompanyName('');
                }}
                className="text-electric hover:text-electric/80"
              >
                {isLogin 
                  ? 'Primeira vez? Cadastrar nova assistência técnica' 
                  : 'Já tenho conta? Fazer login'
                }
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Acesso Rápido para Demo */}
        {isLogin && (
          <Card className="card-electric mt-6">
            <CardHeader>
              <CardTitle className="text-sm font-medium text-center">
                🚀 Acesso Rápido - DEMO
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 gap-3">
                {quickAccess.map((cred, index) => (
                  <Button
                    key={index}
                    variant="outline"
                    size="sm"
                    onClick={() => fillQuickAccess(cred)}
                    className="electric-border text-left justify-start"
                  >
                    <Building2 className="h-4 w-4 mr-2" />
                    <div className="text-left">
                      <div className="font-medium">{cred.name}</div>
                      <div className="text-xs text-muted-foreground">{cred.email}</div>
                    </div>
                  </Button>
                ))}
              </div>
              <p className="text-xs text-muted-foreground text-center mt-3">
                Clique para preencher automaticamente
              </p>
            </CardContent>
          </Card>
        )}

        {/* Características do Sistema */}
        <div className="mt-8 space-y-3">
          <div className="flex items-center space-x-3 text-sm text-muted-foreground">
            <Smartphone className="h-4 w-4 text-electric" />
            <span>Interface otimizada para tablets e celulares</span>
          </div>
          <div className="flex items-center space-x-3 text-sm text-muted-foreground">
            <Wifi className="h-4 w-4 text-electric" />
            <span>Funciona offline em modo PWA</span>
          </div>
          <div className="flex items-center space-x-3 text-sm text-muted-foreground">
            <Shield className="h-4 w-4 text-electric" />
            <span>Dados criptografados e seguros</span>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-8 text-center text-xs text-muted-foreground">
          <p>TechZe Diagnóstico © 2024</p>
          <p>Desenvolvido especialmente para assistências técnicas</p>
        </div>
      </div>
    </div>
  );
}
