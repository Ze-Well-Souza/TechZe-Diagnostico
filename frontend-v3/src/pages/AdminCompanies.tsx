
import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from '@/components/ui/alert-dialog';
import { Building2, Plus, Edit, Trash2, Users, Settings } from 'lucide-react';

export default function AdminCompanies() {
  const [companies, setCompanies] = useState([
    {
      id: '1',
      name: 'UlyTech Informática',
      code: 'ULYTECH',
      email: 'contato@ulytech.com',
      phone: '(11) 99999-9999',
      address: 'Rua das Flores, 123 - São Paulo/SP',
      employees: 5,
      status: 'active',
      createdAt: '2024-01-15'
    },
    {
      id: '2',
      name: 'TechFix Solutions',
      code: 'TECHFIX',
      email: 'admin@techfix.com',
      phone: '(11) 88888-8888',
      address: 'Av. Paulista, 456 - São Paulo/SP',
      employees: 12,
      status: 'active',
      createdAt: '2024-02-20'
    }
  ]);

  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingCompany, setEditingCompany] = useState(null);

  const handleAddCompany = () => {
    setEditingCompany(null);
    setIsDialogOpen(true);
  };

  const handleEditCompany = (company) => {
    setEditingCompany(company);
    setIsDialogOpen(true);
  };

  const handleDeleteCompany = (companyId) => {
    setCompanies(companies.filter(c => c.id !== companyId));
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'active':
        return <Badge className="bg-green-500/20 text-green-400 border-green-500/30">Ativa</Badge>;
      case 'inactive':
        return <Badge className="bg-red-500/20 text-red-400 border-red-500/30">Inativa</Badge>;
      case 'suspended':
        return <Badge className="bg-yellow-500/20 text-yellow-400 border-yellow-500/30">Suspensa</Badge>;
      default:
        return <Badge variant="outline">Desconhecido</Badge>;
    }
  };

  return (
    <div className="min-h-screen bg-black">
      <main className="pt-20 pb-10 px-4 sm:px-6 lg:px-8">
        <div className="container mx-auto max-w-7xl">
          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-3xl font-bold text-white mb-2">Gerenciar Empresas</h1>
              <p className="text-gray-400">Administre as empresas cadastradas no sistema</p>
            </div>
            
            <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
              <DialogTrigger asChild>
                <Button 
                  onClick={handleAddCompany}
                  className="bg-gradient-to-r from-electric to-tech hover:from-electric/80 hover:to-tech/80 text-black"
                >
                  <Plus className="mr-2 h-4 w-4" />
                  Nova Empresa
                </Button>
              </DialogTrigger>
              
              <DialogContent className="bg-dark border-white/20 text-white max-w-md">
                <DialogHeader>
                  <DialogTitle>
                    {editingCompany ? 'Editar Empresa' : 'Nova Empresa'}
                  </DialogTitle>
                  <DialogDescription className="text-gray-400">
                    {editingCompany 
                      ? 'Edite as informações da empresa' 
                      : 'Preencha os dados para cadastrar uma nova empresa'
                    }
                  </DialogDescription>
                </DialogHeader>
                
                <form className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="name">Nome da Empresa</Label>
                      <Input
                        id="name"
                        placeholder="Ex: UlyTech Informática"
                        className="bg-dark/50 border-white/20"
                        defaultValue={editingCompany?.name}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="code">Código</Label>
                      <Input
                        id="code"
                        placeholder="Ex: ULYTECH"
                        className="bg-dark/50 border-white/20"
                        defaultValue={editingCompany?.code}
                      />
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="email">Email</Label>
                    <Input
                      id="email"
                      type="email"
                      placeholder="contato@empresa.com"
                      className="bg-dark/50 border-white/20"
                      defaultValue={editingCompany?.email}
                    />
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="phone">Telefone</Label>
                      <Input
                        id="phone"
                        placeholder="(11) 99999-9999"
                        className="bg-dark/50 border-white/20"
                        defaultValue={editingCompany?.phone}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="status">Status</Label>
                      <select className="w-full h-10 px-3 rounded-md bg-dark/50 border border-white/20 text-white">
                        <option value="active">Ativa</option>
                        <option value="inactive">Inativa</option>
                        <option value="suspended">Suspensa</option>
                      </select>
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="address">Endereço</Label>
                    <Input
                      id="address"
                      placeholder="Rua, número - Cidade/Estado"
                      className="bg-dark/50 border-white/20"
                      defaultValue={editingCompany?.address}
                    />
                  </div>
                  
                  <div className="flex justify-end space-x-2 pt-4">
                    <Button
                      type="button"
                      variant="outline"
                      onClick={() => setIsDialogOpen(false)}
                      className="border-white/20 text-white hover:bg-white/10"
                    >
                      Cancelar
                    </Button>
                    <Button
                      type="submit"
                      className="bg-gradient-to-r from-electric to-tech hover:from-electric/80 hover:to-tech/80 text-black"
                    >
                      {editingCompany ? 'Salvar' : 'Cadastrar'}
                    </Button>
                  </div>
                </form>
              </DialogContent>
            </Dialog>
          </div>

          {/* Stats Cards */}
          <div className="grid md:grid-cols-4 gap-6 mb-8">
            <Card className="bg-dark/50 border-white/10">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-400 text-sm">Total de Empresas</p>
                    <p className="text-2xl font-bold text-white">{companies.length}</p>
                  </div>
                  <Building2 className="h-8 w-8 text-electric" />
                </div>
              </CardContent>
            </Card>
            
            <Card className="bg-dark/50 border-white/10">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-400 text-sm">Empresas Ativas</p>
                    <p className="text-2xl font-bold text-green-400">
                      {companies.filter(c => c.status === 'active').length}
                    </p>
                  </div>
                  <div className="h-8 w-8 rounded-full bg-green-500/20 flex items-center justify-center">
                    <div className="h-3 w-3 rounded-full bg-green-400"></div>
                  </div>
                </div>
              </CardContent>
            </Card>
            
            <Card className="bg-dark/50 border-white/10">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-400 text-sm">Total Funcionários</p>
                    <p className="text-2xl font-bold text-white">
                      {companies.reduce((total, company) => total + company.employees, 0)}
                    </p>
                  </div>
                  <Users className="h-8 w-8 text-tech" />
                </div>
              </CardContent>
            </Card>
            
            <Card className="bg-dark/50 border-white/10">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-400 text-sm">Média Funcionários</p>
                    <p className="text-2xl font-bold text-white">
                      {Math.round(companies.reduce((total, company) => total + company.employees, 0) / companies.length)}
                    </p>
                  </div>
                  <Settings className="h-8 w-8 text-electric" />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Companies Table */}
          <Card className="bg-dark/50 border-white/10">
            <CardHeader>
              <CardTitle className="text-white">Empresas Cadastradas</CardTitle>
              <CardDescription className="text-gray-400">
                Lista de todas as empresas registradas no sistema
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow className="border-white/10">
                    <TableHead className="text-gray-400">Empresa</TableHead>
                    <TableHead className="text-gray-400">Código</TableHead>
                    <TableHead className="text-gray-400">Contato</TableHead>
                    <TableHead className="text-gray-400">Funcionários</TableHead>
                    <TableHead className="text-gray-400">Status</TableHead>
                    <TableHead className="text-gray-400">Ações</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {companies.map((company) => (
                    <TableRow key={company.id} className="border-white/10">
                      <TableCell>
                        <div>
                          <div className="font-medium text-white">{company.name}</div>
                          <div className="text-sm text-gray-400">{company.address}</div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline" className="text-electric border-electric/30">
                          {company.code}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="text-sm">
                          <div className="text-white">{company.email}</div>
                          <div className="text-gray-400">{company.phone}</div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center text-white">
                          <Users className="h-4 w-4 mr-1 text-tech" />
                          {company.employees}
                        </div>
                      </TableCell>
                      <TableCell>
                        {getStatusBadge(company.status)}
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center space-x-2">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleEditCompany(company)}
                            className="border-white/20 text-white hover:bg-white/10"
                          >
                            <Edit className="h-4 w-4" />
                          </Button>
                          
                          <AlertDialog>
                            <AlertDialogTrigger asChild>
                              <Button
                                size="sm"
                                variant="outline"
                                className="border-red-500/30 text-red-400 hover:bg-red-500/10"
                              >
                                <Trash2 className="h-4 w-4" />
                              </Button>
                            </AlertDialogTrigger>
                            <AlertDialogContent className="bg-dark border-white/20">
                              <AlertDialogHeader>
                                <AlertDialogTitle className="text-white">
                                  Excluir empresa?
                                </AlertDialogTitle>
                                <AlertDialogDescription className="text-gray-400">
                                  Esta ação não pode ser desfeita. Todos os dados da empresa {company.name} serão removidos permanentemente.
                                </AlertDialogDescription>
                              </AlertDialogHeader>
                              <AlertDialogFooter>
                                <AlertDialogCancel className="bg-transparent border-white/20 text-white hover:bg-white/10">
                                  Cancelar
                                </AlertDialogCancel>
                                <AlertDialogAction
                                  onClick={() => handleDeleteCompany(company.id)}
                                  className="bg-red-500 hover:bg-red-600"
                                >
                                  Excluir
                                </AlertDialogAction>
                              </AlertDialogFooter>
                            </AlertDialogContent>
                          </AlertDialog>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}
