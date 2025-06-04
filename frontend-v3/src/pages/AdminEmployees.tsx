import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Users, Plus, Edit, Trash2, UserCheck, Mail, Phone, Building2 } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { useCompany } from '@/contexts/CompanyContext';

interface Employee {
  id: string;
  name: string;
  email: string;
  phone: string;
  role: string;
  status: 'active' | 'inactive';
  companyId: string;
  createdAt: string;
}

export default function AdminEmployees() {
  const { selectedCompany } = useCompany();
  const { toast } = useToast();
  const [employees, setEmployees] = useState<Employee[]>([
    {
      id: '1',
      name: 'João Silva',
      email: 'joao@ulytech.com',
      phone: '(11) 99999-1111',
      role: 'Técnico',
      status: 'active',
      companyId: 'ulytech',
      createdAt: '2024-01-15'
    },
    {
      id: '2',
      name: 'Maria Santos',
      email: 'maria@ulytech.com',
      phone: '(11) 99999-2222',
      role: 'Gerente',
      status: 'active',
      companyId: 'ulytech',
      createdAt: '2024-01-10'
    }
  ]);

  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingEmployee, setEditingEmployee] = useState<Employee | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    role: '',
    status: 'active' as 'active' | 'inactive'
  });

  const roles = ['Técnico', 'Gerente', 'Administrador', 'Recepcionista'];

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (editingEmployee) {
      setEmployees(prev => prev.map(emp => 
        emp.id === editingEmployee.id 
          ? { ...emp, ...formData }
          : emp
      ));
      toast({
        title: "Funcionário atualizado",
        description: "Os dados do funcionário foram atualizados com sucesso.",
      });
    } else {
      const newEmployee: Employee = {
        id: Date.now().toString(),
        ...formData,
        companyId: selectedCompany?.id || 'ulytech',
        createdAt: new Date().toISOString().split('T')[0]
      };
      setEmployees(prev => [...prev, newEmployee]);
      toast({
        title: "Funcionário cadastrado",
        description: "Novo funcionário foi cadastrado com sucesso.",
      });
    }

    setFormData({ name: '', email: '', phone: '', role: '', status: 'active' });
    setEditingEmployee(null);
    setIsDialogOpen(false);
  };

  const handleEdit = (employee: Employee) => {
    setEditingEmployee(employee);
    setFormData({
      name: employee.name,
      email: employee.email,
      phone: employee.phone,
      role: employee.role,
      status: employee.status
    });
    setIsDialogOpen(true);
  };

  const handleDelete = (id: string) => {
    setEmployees(prev => prev.filter(emp => emp.id !== id));
    toast({
      title: "Funcionário removido",
      description: "O funcionário foi removido do sistema.",
    });
  };

  const companyEmployees = employees.filter(emp => emp.companyId === selectedCompany?.id);

  return (
    <div className="min-h-screen bg-black text-white p-8 pt-24">
      <div className="container mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold gradient-text mb-2">
              Gerenciar Funcionários
            </h1>
            <p className="text-gray-400">
              Gerencie os funcionários da empresa {selectedCompany?.displayName}
            </p>
          </div>
          
          <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
            <DialogTrigger asChild>
              <Button className="bg-gradient-to-r from-electric to-tech hover:from-electric/80 hover:to-tech/80">
                <Plus className="mr-2 h-4 w-4" />
                Novo Funcionário
              </Button>
            </DialogTrigger>
            <DialogContent className="bg-dark border-white/10 text-white">
              <DialogHeader>
                <DialogTitle>
                  {editingEmployee ? 'Editar Funcionário' : 'Novo Funcionário'}
                </DialogTitle>
                <DialogDescription className="text-gray-400">
                  {editingEmployee ? 'Atualize os dados do funcionário' : 'Cadastre um novo funcionário no sistema'}
                </DialogDescription>
              </DialogHeader>
              
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <Label htmlFor="name" className="text-white">Nome Completo</Label>
                  <Input
                    id="name"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="bg-darker border-white/20 text-white"
                    required
                  />
                </div>
                
                <div>
                  <Label htmlFor="email" className="text-white">Email</Label>
                  <Input
                    id="email"
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    className="bg-darker border-white/20 text-white"
                    required
                  />
                </div>
                
                <div>
                  <Label htmlFor="phone" className="text-white">Telefone</Label>
                  <Input
                    id="phone"
                    value={formData.phone}
                    onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                    className="bg-darker border-white/20 text-white"
                    placeholder="(11) 99999-9999"
                    required
                  />
                </div>
                
                <div>
                  <Label htmlFor="role" className="text-white">Cargo</Label>
                  <Select value={formData.role} onValueChange={(value) => setFormData({ ...formData, role: value })}>
                    <SelectTrigger className="bg-darker border-white/20 text-white">
                      <SelectValue placeholder="Selecione o cargo" />
                    </SelectTrigger>
                    <SelectContent className="bg-dark border-white/20">
                      {roles.map((role) => (
                        <SelectItem key={role} value={role} className="text-white hover:bg-white/10">
                          {role}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                
                <div>
                  <Label htmlFor="status" className="text-white">Status</Label>
                  <Select value={formData.status} onValueChange={(value: 'active' | 'inactive') => setFormData({ ...formData, status: value })}>
                    <SelectTrigger className="bg-darker border-white/20 text-white">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-dark border-white/20">
                      <SelectItem value="active" className="text-white hover:bg-white/10">Ativo</SelectItem>
                      <SelectItem value="inactive" className="text-white hover:bg-white/10">Inativo</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <div className="flex justify-end space-x-2 pt-4">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => {
                      setIsDialogOpen(false);
                      setEditingEmployee(null);
                      setFormData({ name: '', email: '', phone: '', role: '', status: 'active' });
                    }}
                    className="border-white/20 text-white hover:bg-white/10"
                  >
                    Cancelar
                  </Button>
                  <Button
                    type="submit"
                    className="bg-gradient-to-r from-electric to-tech hover:from-electric/80 hover:to-tech/80"
                  >
                    {editingEmployee ? 'Atualizar' : 'Cadastrar'}
                  </Button>
                </div>
              </form>
            </DialogContent>
          </Dialog>
        </div>

        <Card className="glass-effect border-white/10">
          <CardHeader>
            <CardTitle className="text-white flex items-center">
              <Users className="mr-2 h-5 w-5 text-electric" />
              Funcionários Cadastrados
            </CardTitle>
            <CardDescription className="text-gray-400">
              Total de {companyEmployees.length} funcionários cadastrados
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow className="border-white/10">
                  <TableHead className="text-gray-300">Nome</TableHead>
                  <TableHead className="text-gray-300">Email</TableHead>
                  <TableHead className="text-gray-300">Telefone</TableHead>
                  <TableHead className="text-gray-300">Cargo</TableHead>
                  <TableHead className="text-gray-300">Status</TableHead>
                  <TableHead className="text-gray-300">Ações</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {companyEmployees.map((employee) => (
                  <TableRow key={employee.id} className="border-white/10">
                    <TableCell className="text-white font-medium">{employee.name}</TableCell>
                    <TableCell className="text-gray-300">{employee.email}</TableCell>
                    <TableCell className="text-gray-300">{employee.phone}</TableCell>
                    <TableCell className="text-gray-300">{employee.role}</TableCell>
                    <TableCell>
                      <Badge variant={employee.status === 'active' ? 'default' : 'secondary'}>
                        {employee.status === 'active' ? 'Ativo' : 'Inativo'}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <div className="flex space-x-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleEdit(employee)}
                          className="border-white/20 text-white hover:bg-white/10"
                        >
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleDelete(employee.id)}
                          className="border-red-500/20 text-red-400 hover:bg-red-500/10"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
