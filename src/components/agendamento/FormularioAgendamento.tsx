import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { User } from 'lucide-react';

interface DadosCliente {
  nome: string;
  email: string;
  telefone: string;
  descricaoProblema: string;
}

interface FormularioAgendamentoProps {
  onSubmit: (dados: DadosCliente) => void;
  onVoltar: () => void;
  loading?: boolean;
  className?: string;
}

export const FormularioAgendamento: React.FC<FormularioAgendamentoProps> = ({
  onSubmit,
  onVoltar,
  loading = false,
  className = ''
}) => {
  const [dados, setDados] = useState<DadosCliente>({
    nome: '',
    email: '',
    telefone: '',
    descricaoProblema: ''
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(dados);
  };

  return (
    <Card className={`w-full max-w-2xl ${className}`}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <User className="w-5 h-5" />
          Dados do Cliente
        </CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="nome">Nome Completo *</Label>
              <Input
                id="nome"
                value={dados.nome}
                onChange={(e) => setDados(prev => ({ ...prev, nome: e.target.value }))}
                placeholder="Seu nome completo"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="email">Email *</Label>
              <Input
                id="email"
                type="email"
                value={dados.email}
                onChange={(e) => setDados(prev => ({ ...prev, email: e.target.value }))}
                placeholder="seu@email.com"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="telefone">Telefone *</Label>
              <Input
                id="telefone"
                value={dados.telefone}
                onChange={(e) => setDados(prev => ({ ...prev, telefone: e.target.value }))}
                placeholder="(11) 99999-9999"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="descricaoProblema">Descrição do Problema *</Label>
              <Textarea
                id="descricaoProblema"
                value={dados.descricaoProblema}
                onChange={(e) => setDados(prev => ({ ...prev, descricaoProblema: e.target.value }))}
                placeholder="Descreva o problema..."
                rows={4}
              />
            </div>
          </div>

          <div className="flex gap-3 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={onVoltar}
              disabled={loading}
              className="flex-1"
            >
              Voltar
            </Button>
            <Button
              type="submit"
              disabled={loading}
              className="flex-1"
            >
              {loading ? 'Criando Agendamento...' : 'Finalizar Agendamento'}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}; 