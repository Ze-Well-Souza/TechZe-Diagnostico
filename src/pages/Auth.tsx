
import React, { useState } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, Zap, MonitorSpeaker } from 'lucide-react';

export default function Auth() {
  const { user, signIn, signUp, loading } = useAuth();
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [authLoading, setAuthLoading] = useState(false);
  const [error, setError] = useState('');

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-tech-darker to-tech-dark">
        <div className="flex items-center space-x-2 text-electric">
          <Loader2 className="h-8 w-8 animate-spin" />
          <span className="tech-font text-lg">Inicializando TechZe...</span>
        </div>
      </div>
    );
  }

  if (user) {
    return <Navigate to="/dashboard" replace />;
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setAuthLoading(true);

    try {
      let result;
      if (isLogin) {
        result = await signIn(email, password);
      } else {
        result = await signUp(email, password, fullName);
      }

      if (result.error) {
        setError(
          result.error.message === 'Invalid login credentials'
            ? 'Email ou senha incorretos'
            : result.error.message
        );
      } else if (!isLogin) {
        setError('');
        alert('Conta criada! Verifique seu email para confirmar.');
      }
    } catch (err) {
      setError('Erro inesperado. Tente novamente.');
    } finally {
      setAuthLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-tech-darker via-tech-dark to-tech-darker relative overflow-hidden">
      {/* Background Effects */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-electric rounded-full filter blur-3xl"></div>
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-electric rounded-full filter blur-3xl"></div>
      </div>

      <div className="relative z-10 w-full max-w-md p-6">
        <Card className="card-electric backdrop-blur-md">
          <CardHeader className="text-center space-y-4">
            <div className="flex items-center justify-center space-x-2">
              <div className="p-3 rounded-lg bg-primary/10 electric-glow">
                <MonitorSpeaker className="h-8 w-8 text-electric" />
              </div>
              <div>
                <h1 className="tech-font text-2xl font-bold neon-text">TechRepair</h1>
                <p className="text-sm text-muted-foreground">Sistema de Diagnóstico</p>
              </div>
            </div>
            
            <CardTitle className="text-xl text-foreground">
              {isLogin ? 'Entre na sua conta' : 'Criar nova conta'}
            </CardTitle>
            <CardDescription className="text-muted-foreground">
              {isLogin 
                ? 'Acesse o sistema de diagnóstico da sua loja' 
                : 'Registre-se para acessar o TechRepair'
              }
            </CardDescription>
          </CardHeader>

          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              {!isLogin && (
                <div className="space-y-2">
                  <Label htmlFor="fullName" className="text-foreground">Nome Completo</Label>
                  <Input
                    id="fullName"
                    type="text"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    required={!isLogin}
                    className="electric-border bg-input text-foreground"
                    placeholder="Seu nome completo"
                  />
                </div>
              )}

              <div className="space-y-2">
                <Label htmlFor="email" className="text-foreground">Email</Label>
                <Input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="electric-border bg-input text-foreground"
                  placeholder="seu@email.com"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="password" className="text-foreground">Senha</Label>
                <Input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="electric-border bg-input text-foreground"
                  placeholder="Sua senha"
                />
              </div>

              {error && (
                <Alert className="border-destructive/50 text-destructive">
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

              <Button
                type="submit"
                disabled={authLoading}
                className="w-full btn-electric tech-font font-semibold"
              >
                {authLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    {isLogin ? 'Entrando...' : 'Criando conta...'}
                  </>
                ) : (
                  <>
                    <Zap className="mr-2 h-4 w-4" />
                    {isLogin ? 'Entrar' : 'Criar Conta'}
                  </>
                )}
              </Button>

              <div className="text-center">
                <button
                  type="button"
                  onClick={() => {
                    setIsLogin(!isLogin);
                    setError('');
                  }}
                  className="text-electric hover:text-electric-glow transition-colors text-sm underline"
                >
                  {isLogin 
                    ? 'Não tem conta? Criar uma agora' 
                    : 'Já tem conta? Fazer login'
                  }
                </button>
              </div>
            </form>
          </CardContent>
        </Card>

        <div className="mt-6 text-center text-xs text-muted-foreground">
          <p>TechZe Diagnóstico v3.0 - Sistema Profissional</p>
        </div>
      </div>
    </div>
  );
}
