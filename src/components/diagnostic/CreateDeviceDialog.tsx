
import { useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useDiagnostics } from "@/hooks/useDiagnostics";
import { CreateDeviceRequest } from "@/types/diagnostic";

interface CreateDeviceDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export const CreateDeviceDialog = ({ open, onOpenChange }: CreateDeviceDialogProps) => {
  const { createDevice, isCreatingDevice } = useDiagnostics();
  
  const [formData, setFormData] = useState<CreateDeviceRequest>({
    name: '',
    type: '',
    os: '',
    os_version: '',
    processor: '',
    ram: '',
    storage: '',
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.name || !formData.type) {
      return;
    }

    createDevice(formData);
    
    // Reset form
    setFormData({
      name: '',
      type: '',
      os: '',
      os_version: '',
      processor: '',
      ram: '',
      storage: '',
    });
    
    onOpenChange(false);
  };

  const deviceTypes = [
    { value: 'desktop', label: 'Desktop' },
    { value: 'laptop', label: 'Laptop' },
    { value: 'server', label: 'Servidor' },
    { value: 'mobile', label: 'Mobile' },
  ];

  const operatingSystems = [
    { value: 'Windows 11', label: 'Windows 11' },
    { value: 'Windows 10', label: 'Windows 10' },
    { value: 'macOS', label: 'macOS' },
    { value: 'Ubuntu', label: 'Ubuntu' },
    { value: 'Debian', label: 'Debian' },
    { value: 'CentOS', label: 'CentOS' },
    { value: 'Android', label: 'Android' },
    { value: 'iOS', label: 'iOS' },
  ];

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="bg-black/90 backdrop-blur-md border-white/20 text-white">
        <DialogHeader>
          <DialogTitle>Cadastrar Novo Dispositivo</DialogTitle>
        </DialogHeader>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="name">Nome do Dispositivo *</Label>
            <Input
              id="name"
              placeholder="Ex: PC-Escritório-01"
              value={formData.name}
              onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
              className="bg-white/10 border-white/30 text-white placeholder:text-white/50"
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="type">Tipo de Dispositivo *</Label>
            <Select value={formData.type} onValueChange={(value) => setFormData(prev => ({ ...prev, type: value }))}>
              <SelectTrigger className="bg-white/10 border-white/30 text-white">
                <SelectValue placeholder="Selecione o tipo" />
              </SelectTrigger>
              <SelectContent className="bg-black/90 border-white/20">
                {deviceTypes.map((type) => (
                  <SelectItem key={type.value} value={type.value} className="text-white">
                    {type.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="os">Sistema Operacional</Label>
              <Select value={formData.os} onValueChange={(value) => setFormData(prev => ({ ...prev, os: value }))}>
                <SelectTrigger className="bg-white/10 border-white/30 text-white">
                  <SelectValue placeholder="Selecione o SO" />
                </SelectTrigger>
                <SelectContent className="bg-black/90 border-white/20">
                  {operatingSystems.map((os) => (
                    <SelectItem key={os.value} value={os.value} className="text-white">
                      {os.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="os_version">Versão do SO</Label>
              <Input
                id="os_version"
                placeholder="Ex: 22H2, 14.1"
                value={formData.os_version}
                onChange={(e) => setFormData(prev => ({ ...prev, os_version: e.target.value }))}
                className="bg-white/10 border-white/30 text-white placeholder:text-white/50"
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="processor">Processador</Label>
            <Input
              id="processor"
              placeholder="Ex: Intel Core i7-12700K"
              value={formData.processor}
              onChange={(e) => setFormData(prev => ({ ...prev, processor: e.target.value }))}
              className="bg-white/10 border-white/30 text-white placeholder:text-white/50"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="ram">Memória RAM</Label>
              <Input
                id="ram"
                placeholder="Ex: 16GB DDR4"
                value={formData.ram}
                onChange={(e) => setFormData(prev => ({ ...prev, ram: e.target.value }))}
                className="bg-white/10 border-white/30 text-white placeholder:text-white/50"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="storage">Armazenamento</Label>
              <Input
                id="storage"
                placeholder="Ex: 1TB SSD"
                value={formData.storage}
                onChange={(e) => setFormData(prev => ({ ...prev, storage: e.target.value }))}
                className="bg-white/10 border-white/30 text-white placeholder:text-white/50"
              />
            </div>
          </div>

          <div className="flex justify-end space-x-2 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              className="border-white/30 text-white hover:bg-white/10"
            >
              Cancelar
            </Button>
            <Button
              type="submit"
              disabled={isCreatingDevice || !formData.name || !formData.type}
              className="btn-tecno"
            >
              {isCreatingDevice ? "Criando..." : "Criar Dispositivo"}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
};
