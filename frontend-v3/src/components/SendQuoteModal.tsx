
import { useState } from 'react';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Send, MessageCircle, Mail, Phone, DollarSign } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

interface SendQuoteModalProps {
  clientName: string;
  deviceInfo: string;
  estimatedCost: number;
  problems: string[];
  trigger: React.ReactNode;
}

export const SendQuoteModal: React.FC<SendQuoteModalProps> = ({
  clientName,
  deviceInfo,
  estimatedCost,
  problems,
  trigger
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [sending, setSending] = useState(false);
  const [clientPhone, setClientPhone] = useState('');
  const [clientEmail, setClientEmail] = useState('');
  const [customMessage, setCustomMessage] = useState('');
  const { toast } = useToast();

  const defaultMessage = `Olá ${clientName}! 

Concluímos o diagnóstico do seu ${deviceInfo}.

📋 *Problemas identificados:*
${problems.map(p => `• ${p}`).join('\n')}

💰 *Valor estimado para reparo:* R$ ${estimatedCost.toFixed(2)}

O orçamento completo está em anexo. Estamos à disposição para esclarecer qualquer dúvida!

Atenciosamente,
Equipe TechRepair`;

  const handleSendWhatsApp = async () => {
    setSending(true);
    try {
      // Simular envio via WhatsApp
      const message = encodeURIComponent(customMessage || defaultMessage);
      const whatsappUrl = `https://wa.me/55${clientPhone.replace(/\D/g, '')}?text=${message}`;
      window.open(whatsappUrl, '_blank');
      
      toast({
        title: "WhatsApp aberto",
        description: "O WhatsApp foi aberto com a mensagem pré-preenchida.",
      });
      
      setIsOpen(false);
    } catch (error) {
      toast({
        title: "Erro",
        description: "Não foi possível abrir o WhatsApp.",
        variant: "destructive",
      });
    } finally {
      setSending(false);
    }
  };

  const handleSendEmail = async () => {
    setSending(true);
    try {
      // Simular envio via Email
      const subject = encodeURIComponent(`Orçamento - ${deviceInfo} - ${clientName}`);
      const body = encodeURIComponent(customMessage || defaultMessage);
      const mailtoUrl = `mailto:${clientEmail}?subject=${subject}&body=${body}`;
      window.open(mailtoUrl, '_blank');
      
      toast({
        title: "Email aberto",
        description: "O cliente de email foi aberto com a mensagem pré-preenchida.",
      });
      
      setIsOpen(false);
    } catch (error) {
      toast({
        title: "Erro",
        description: "Não foi possível abrir o cliente de email.",
        variant: "destructive",
      });
    } finally {
      setSending(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        {trigger}
      </DialogTrigger>
      <DialogContent className="bg-dark border-white/10 text-white max-w-2xl">
        <DialogHeader>
          <DialogTitle className="flex items-center">
            <Send className="mr-2 h-5 w-5 text-electric" />
            Enviar Orçamento
          </DialogTitle>
          <DialogDescription className="text-gray-400">
            Envie o orçamento para o cliente via WhatsApp ou Email
          </DialogDescription>
        </DialogHeader>

        <Tabs defaultValue="whatsapp" className="w-full">
          <TabsList className="grid w-full grid-cols-2 bg-darker">
            <TabsTrigger value="whatsapp" className="data-[state=active]:bg-electric data-[state=active]:text-black">
              <MessageCircle className="mr-2 h-4 w-4" />
              WhatsApp
            </TabsTrigger>
            <TabsTrigger value="email" className="data-[state=active]:bg-electric data-[state=active]:text-black">
              <Mail className="mr-2 h-4 w-4" />
              Email
            </TabsTrigger>
          </TabsList>

          <TabsContent value="whatsapp" className="space-y-4">
            <Card className="bg-darker/50 border-white/10">
              <CardHeader>
                <CardTitle className="text-white flex items-center">
                  <MessageCircle className="mr-2 h-5 w-5 text-green-400" />
                  Envio via WhatsApp
                </CardTitle>
                <CardDescription className="text-gray-400">
                  Envie o orçamento diretamente pelo WhatsApp do cliente
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="phone" className="text-white">Telefone do Cliente</Label>
                  <div className="relative">
                    <Phone className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                    <Input
                      id="phone"
                      type="tel"
                      placeholder="(11) 99999-9999"
                      value={clientPhone}
                      onChange={(e) => setClientPhone(e.target.value)}
                      className="pl-10 bg-dark border-white/20 text-white"
                    />
                  </div>
                </div>
                
                <div>
                  <Label htmlFor="whatsapp-message" className="text-white">Mensagem</Label>
                  <Textarea
                    id="whatsapp-message"
                    placeholder="Personalize a mensagem..."
                    value={customMessage}
                    onChange={(e) => setCustomMessage(e.target.value)}
                    className="bg-dark border-white/20 text-white h-32"
                  />
                  <p className="text-xs text-gray-400 mt-1">
                    Deixe em branco para usar a mensagem padrão
                  </p>
                </div>

                <Button
                  onClick={handleSendWhatsApp}
                  disabled={!clientPhone || sending}
                  className="w-full bg-green-600 hover:bg-green-700 text-white"
                >
                  {sending ? (
                    "Enviando..."
                  ) : (
                    <>
                      <MessageCircle className="mr-2 h-4 w-4" />
                      Enviar via WhatsApp
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="email" className="space-y-4">
            <Card className="bg-darker/50 border-white/10">
              <CardHeader>
                <CardTitle className="text-white flex items-center">
                  <Mail className="mr-2 h-5 w-5 text-blue-400" />
                  Envio via Email
                </CardTitle>
                <CardDescription className="text-gray-400">
                  Envie o orçamento por email para o cliente
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="email" className="text-white">Email do Cliente</Label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                    <Input
                      id="email"
                      type="email"
                      placeholder="cliente@email.com"
                      value={clientEmail}
                      onChange={(e) => setClientEmail(e.target.value)}
                      className="pl-10 bg-dark border-white/20 text-white"
                    />
                  </div>
                </div>
                
                <div>
                  <Label htmlFor="email-message" className="text-white">Mensagem</Label>
                  <Textarea
                    id="email-message"
                    placeholder="Personalize a mensagem..."
                    value={customMessage}
                    onChange={(e) => setCustomMessage(e.target.value)}
                    className="bg-dark border-white/20 text-white h-32"
                  />
                  <p className="text-xs text-gray-400 mt-1">
                    Deixe em branco para usar a mensagem padrão
                  </p>
                </div>

                <Button
                  onClick={handleSendEmail}
                  disabled={!clientEmail || sending}
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white"
                >
                  {sending ? (
                    "Enviando..."
                  ) : (
                    <>
                      <Mail className="mr-2 h-4 w-4" />
                      Enviar via Email
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* Summary */}
        <Card className="bg-darker/30 border-electric/20">
          <CardContent className="p-4">
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-400">Cliente:</span>
              <span className="text-white">{clientName}</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-400">Dispositivo:</span>
              <span className="text-white">{deviceInfo}</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-400">Valor Estimado:</span>
              <span className="text-green-400 font-semibold flex items-center">
                <DollarSign className="h-4 w-4 mr-1" />
                R$ {estimatedCost.toFixed(2)}
              </span>
            </div>
          </CardContent>
        </Card>
      </DialogContent>
    </Dialog>
  );
};
