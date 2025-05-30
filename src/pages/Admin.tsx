
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  User, 
  Users, 
  Settings, 
  Lock, 
  Building, 
  Store, 
  Shield, 
  Plus, 
  Trash2, 
  Search
} from "lucide-react";

// Fake data for demo purposes
const initialUsers = [
  { id: 1, name: "José Silva", email: "jose@ulytech.com", role: "admin", active: true },
  { id: 2, name: "Ana Maria", email: "ana@ulytech.com", role: "tech", active: true },
  { id: 3, name: "Roberto Carlos", email: "roberto@ulytech.com", role: "tech", active: false },
  { id: 4, name: "Mariana Oliveira", email: "mariana@ulytech.com", role: "tech", active: true },
];

const permissions = [
  { id: "diagnostic", name: "Diagnóstico", description: "Acesso à tela de diagnóstico de computadores" },
  { id: "customers", name: "Clientes", description: "Gerenciar cadastro de clientes" },
  { id: "services", name: "Serviços", description: "Acessar e gerenciar serviços" },
  { id: "inventory", name: "Estoque", description: "Gerenciar produtos e estoque" },
  { id: "reports", name: "Relatórios", description: "Visualizar e exportar relatórios" },
  { id: "settings", name: "Configurações", description: "Acessar configurações do sistema" },
  { id: "admin", name: "Administração", description: "Acesso à funcionalidades administrativas" },
];

const stores = [
  { id: "ulytech", name: "UlyTech", address: "Rua Exemplo, 123 - Carapicuiba" },
  { id: "utilimix", name: "UtiliMix", address: "Av. Principal, 456 - Alphaville" },
  { id: "useprint", name: "UsePrint", address: "Praça Central, 789 - São Paulo" },
];

const Admin = () => {
  const [users, setUsers] = useState(initialUsers);
  const [newUser, setNewUser] = useState({ name: "", email: "", role: "tech", password: "" });
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedUser, setSelectedUser] = useState<number | null>(null);
  const [userPermissions, setUserPermissions] = useState<Record<string, boolean>>({});

  // Handle user selection and load their permissions
  const handleSelectUser = (userId: number) => {
    setSelectedUser(userId);
    // Simulate loading user permissions
    const randomPermissions: Record<string, boolean> = {};
    permissions.forEach(perm => {
      randomPermissions[perm.id] = Math.random() > 0.3;
    });
    setUserPermissions(randomPermissions);
  };

  // Handle adding a new user
  const handleAddUser = () => {
    if (newUser.name && newUser.email && newUser.password) {
      const newId = Math.max(...users.map(u => u.id)) + 1;
      setUsers([...users, {
        id: newId,
        name: newUser.name,
        email: newUser.email,
        role: newUser.role,
        active: true
      }]);
      setNewUser({ name: "", email: "", role: "tech", password: "" });
    }
  };
  
  // Handle toggling user active status
  const handleToggleActive = (userId: number) => {
    setUsers(users.map(user => 
      user.id === userId ? { ...user, active: !user.active } : user
    ));
  };

  // Handle permission toggle
  const handlePermissionChange = (permId: string, checked: boolean) => {
    setUserPermissions(prev => ({
      ...prev,
      [permId]: checked
    }));
  };

  // Filter users based on search term
  const filteredUsers = users.filter(user => 
    user.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
    user.email.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-black via-gray-900 to-black p-6">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">
            Painel Administrativo
          </h1>
          <p className="text-gray-200">Configurações e gerenciamento do sistema</p>
        </div>
        
        <Tabs defaultValue="users" className="space-y-6">
          <TabsList className="bg-black/40 backdrop-blur-md border-white/20 grid grid-cols-3 w-full max-w-lg mx-auto">
            <TabsTrigger value="users" className="text-white">
              <Users className="w-4 h-4 mr-2" />
              Usuários
            </TabsTrigger>
            <TabsTrigger value="stores" className="text-white">
              <Store className="w-4 h-4 mr-2" />
              Lojas
            </TabsTrigger>
            <TabsTrigger value="settings" className="text-white">
              <Settings className="w-4 h-4 mr-2" />
              Sistema
            </TabsTrigger>
          </TabsList>
          
          {/* Gerenciamento de Usuários */}
          <TabsContent value="users">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Lista de Usuários */}
              <Card className="bg-black/40 backdrop-blur-md border-white/20 lg:col-span-1">
                <CardHeader className="pb-2">
                  <CardTitle className="text-white flex items-center gap-2">
                    <Users className="w-5 h-5" />
                    Usuários do Sistema
                  </CardTitle>
                  <div className="relative mt-2">
                    <Search className="absolute left-2 top-2.5 h-4 w-4 text-gray-400" />
                    <Input
                      placeholder="Buscar usuário..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="bg-black/30 border-white/20 pl-8 text-white"
                    />
                  </div>
                </CardHeader>
                <CardContent className="space-y-2 max-h-[500px] overflow-y-auto">
                  {filteredUsers.length === 0 ? (
                    <p className="text-gray-400 text-center py-3">Nenhum usuário encontrado</p>
                  ) : (
                    filteredUsers.map(user => (
                      <div 
                        key={user.id} 
                        className={`
                          flex items-center justify-between p-3 rounded-md cursor-pointer
                          ${selectedUser === user.id ? 'bg-gray-800/50 border border-gray-500/50' : 'bg-black/20 hover:bg-black/30 border border-white/10'}
                        `}
                        onClick={() => handleSelectUser(user.id)}
                      >
                        <div className="flex items-center gap-3">
                          <div className={`
                            w-10 h-10 rounded-full flex items-center justify-center
                            ${user.role === 'admin' ? 'bg-gray-500/20' : 'bg-gray-600/20'}
                          `}>
                            {user.role === 'admin' ? 
                              <Shield className="w-5 h-5 text-gray-400" /> : 
                              <User className="w-5 h-5 text-gray-400" />
                            }
                          </div>
                          <div>
                            <p className="text-white font-medium">{user.name}</p>
                            <p className="text-gray-200 text-sm">{user.email}</p>
                          </div>
                        </div>
                        <div className="flex flex-col items-end gap-1">
                          <Badge className={user.role === 'admin' ? 'bg-gray-500/20 text-gray-300' : 'bg-gray-600/20 text-gray-300'}>
                            {user.role === 'admin' ? 'Admin' : 'Técnico'}
                          </Badge>
                          <div className="flex items-center gap-1">
                            <div className={`w-2 h-2 rounded-full ${user.active ? 'bg-green-500' : 'bg-red-500'}`}></div>
                            <span className="text-xs text-gray-400">{user.active ? 'Ativo' : 'Inativo'}</span>
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                </CardContent>
              </Card>
              
              {/* Detalhes do Usuário e Permissões */}
              <Card className="bg-black/40 backdrop-blur-md border-white/20 lg:col-span-2">
                <CardHeader className="pb-2">
                  <CardTitle className="text-white flex items-center gap-2">
                    {selectedUser ? (
                      <>
                        <Lock className="w-5 h-5" />
                        Permissões de Acesso
                      </>
                    ) : (
                      <>
                        <Plus className="w-5 h-5" />
                        Adicionar Novo Usuário
                      </>
                    )}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {selectedUser ? (
                    <div className="space-y-6">
                      <div className="p-4 bg-black/30 rounded-md border border-white/10">
                        <h3 className="text-white mb-2 font-medium">Informações do Usuário</h3>
                        <div className="grid grid-cols-2 gap-4">
                          <div>
                            <Label className="text-gray-200">Status</Label>
                            <div className="mt-1 flex items-center gap-2">
                              <Switch 
                                checked={users.find(u => u.id === selectedUser)?.active || false}
                                onCheckedChange={() => handleToggleActive(selectedUser)}
                              />
                              <span className="text-white">
                                {users.find(u => u.id === selectedUser)?.active ? 'Ativo' : 'Inativo'}
                              </span>
                            </div>
                          </div>
                          <div>
                            <Label className="text-gray-200">Função</Label>
                            <div className="mt-1">
                              <select 
                                className="w-full bg-black/50 border border-white/20 rounded text-white p-2"
                                value={users.find(u => u.id === selectedUser)?.role}
                                onChange={() => {}} // Would handle role change in a real implementation
                              >
                                <option value="tech">Técnico</option>
                                <option value="admin">Administrador</option>
                              </select>
                            </div>
                          </div>
                        </div>
                      </div>

                      <div>
                        <h3 className="text-white mb-4 font-medium">Permissões do Sistema</h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          {permissions.map(perm => (
                            <div 
                              key={perm.id}
                              className="p-3 bg-black/30 rounded-md border border-white/10 flex items-center justify-between"
                            >
                              <div>
                                <Label className="text-white">{perm.name}</Label>
                                <p className="text-sm text-gray-200">{perm.description}</p>
                              </div>
                              <Switch 
                                checked={userPermissions[perm.id] || false}
                                onCheckedChange={(checked) => handlePermissionChange(perm.id, checked)}
                              />
                            </div>
                          ))}
                        </div>
                        
                        <div className="mt-6 flex justify-end gap-3">
                          <Button variant="default" className="bg-gradient-to-r from-gray-700 to-gray-800 text-white hover:from-gray-600 hover:to-gray-700">
                            Salvar Alterações
                          </Button>
                          <Button variant="outline" className="border-white/30 text-white hover:bg-white/10">
                            <Trash2 className="w-4 h-4 mr-1" />
                            Excluir Usuário
                          </Button>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      <div className="space-y-2">
                        <Label htmlFor="name" className="text-white">Nome Completo</Label>
                        <Input
                          id="name"
                          value={newUser.name}
                          onChange={(e) => setNewUser({...newUser, name: e.target.value})}
                          className="bg-black/30 border-white/20 text-white"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="email" className="text-white">Email</Label>
                        <Input
                          id="email"
                          type="email"
                          value={newUser.email}
                          onChange={(e) => setNewUser({...newUser, email: e.target.value})}
                          className="bg-black/30 border-white/20 text-white"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="password" className="text-white">Senha</Label>
                        <Input
                          id="password"
                          type="password"
                          value={newUser.password}
                          onChange={(e) => setNewUser({...newUser, password: e.target.value})}
                          className="bg-black/30 border-white/20 text-white"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="role" className="text-white">Função</Label>
                        <select
                          id="role"
                          value={newUser.role}
                          onChange={(e) => setNewUser({...newUser, role: e.target.value})}
                          className="w-full bg-black/30 border border-white/20 rounded text-white p-2"
                        >
                          <option value="tech">Técnico</option>
                          <option value="admin">Administrador</option>
                        </select>
                      </div>
                      <Button 
                        onClick={handleAddUser} 
                        className="w-full mt-2 bg-gradient-to-r from-gray-700 to-gray-800 text-white hover:from-gray-600 hover:to-gray-700"
                      >
                        <Plus className="w-4 h-4 mr-1" />
                        Adicionar Usuário
                      </Button>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </TabsContent>
          
          {/* Gerenciamento de Lojas */}
          <TabsContent value="stores">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card className="bg-black/40 backdrop-blur-md border-white/20">
                <CardHeader>
                  <CardTitle className="text-white flex items-center gap-2">
                    <Building className="w-5 h-5" />
                    Lojas Cadastradas
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {stores.map(store => (
                    <div 
                      key={store.id}
                      className="bg-black/20 p-4 rounded-md border border-white/10 flex justify-between"
                    >
                      <div>
                        <h3 className="text-white font-medium">{store.name}</h3>
                        <p className="text-gray-200 text-sm">{store.address}</p>
                      </div>
                      <div className="flex gap-2">
                        <Button variant="outline" size="sm" className="border-white/30 text-white hover:bg-white/10">
                          Editar
                        </Button>
                        <Button variant="outline" size="sm" className="border-white/30 text-white hover:bg-white/10">
                          Configurar
                        </Button>
                      </div>
                    </div>
                  ))}
                  <Button className="w-full mt-4 bg-gradient-to-r from-gray-700 to-gray-800 text-white hover:from-gray-600 hover:to-gray-700">
                    <Plus className="w-4 h-4 mr-1" />
                    Adicionar Nova Loja
                  </Button>
                </CardContent>
              </Card>
              <Card className="bg-black/40 backdrop-blur-md border-white/20">
                <CardHeader>
                  <CardTitle className="text-white flex items-center gap-2">
                    <Settings className="w-5 h-5" />
                    Configurações de Loja
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="store-name" className="text-white">Nome da Loja</Label>
                    <Input
                      id="store-name"
                      defaultValue="UlyTech"
                      className="bg-black/30 border-white/20 text-white"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="store-address" className="text-white">Endereço</Label>
                    <Input
                      id="store-address"
                      defaultValue="Rua Exemplo, 123 - Carapicuiba"
                      className="bg-black/30 border-white/20 text-white"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="store-phone" className="text-white">Telefone</Label>
                    <Input
                      id="store-phone"
                      defaultValue="(11) 94380-6290"
                      className="bg-black/30 border-white/20 text-white"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="store-email" className="text-white">Email de Contato</Label>
                    <Input
                      id="store-email"
                      type="email"
                      defaultValue="contato@ulytech.com"
                      className="bg-black/30 border-white/20 text-white"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label className="text-white">Logo da Loja</Label>
                    <div className="flex items-center gap-4">
                      <div className="w-20 h-20 bg-gradient-to-br from-gray-600 to-gray-800 rounded-lg flex items-center justify-center shadow-lg">
                        <span className="text-white font-bold text-2xl">U</span>
                      </div>
                      <Button variant="outline" className="border-white/30 text-white hover:bg-white/10">
                        Alterar Logo
                      </Button>
                    </div>
                  </div>
                  <Button className="w-full mt-4 bg-gradient-to-r from-gray-700 to-gray-800 text-white hover:from-gray-600 hover:to-gray-700">
                    Salvar Configurações
                  </Button>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
          
          {/* Configurações do Sistema */}
          <TabsContent value="settings">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card className="bg-black/40 backdrop-blur-md border-white/20">
                <CardHeader>
                  <CardTitle className="text-white flex items-center gap-2">
                    <Settings className="w-5 h-5" />
                    Configurações Gerais
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="p-3 bg-black/20 rounded-md border border-white/10 flex items-center justify-between">
                    <div>
                      <Label className="text-white">Modo Escuro</Label>
                      <p className="text-sm text-gray-200">Ativar tema escuro no sistema</p>
                    </div>
                    <Switch defaultChecked={true} />
                  </div>
                  <div className="p-3 bg-black/20 rounded-md border border-white/10 flex items-center justify-between">
                    <div>
                      <Label className="text-white">Notificações</Label>
                      <p className="text-sm text-gray-200">Receber alertas do sistema</p>
                    </div>
                    <Switch defaultChecked={true} />
                  </div>
                  <div className="p-3 bg-black/20 rounded-md border border-white/10 flex items-center justify-between">
                    <div>
                      <Label className="text-white">Backups Automáticos</Label>
                      <p className="text-sm text-gray-200">Realizar backups periódicos</p>
                    </div>
                    <Switch defaultChecked={true} />
                  </div>
                  <div className="p-3 bg-black/20 rounded-md border border-white/10 flex items-center justify-between">
                    <div>
                      <Label className="text-white">Modo Manutenção</Label>
                      <p className="text-sm text-gray-200">Bloquear acesso ao sistema</p>
                    </div>
                    <Switch defaultChecked={false} />
                  </div>
                  <Button className="w-full mt-4 bg-gradient-to-r from-gray-700 to-gray-800 text-white hover:from-gray-600 hover:to-gray-700">
                    Salvar Configurações
                  </Button>
                </CardContent>
              </Card>
              <Card className="bg-black/40 backdrop-blur-md border-white/20">
                <CardHeader>
                  <CardTitle className="text-white flex items-center gap-2">
                    <Shield className="w-5 h-5" />
                    Segurança do Sistema
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="timeout" className="text-white">Tempo de Inatividade (minutos)</Label>
                    <Input
                      id="timeout"
                      type="number"
                      defaultValue="30"
                      className="bg-black/30 border-white/20 text-white"
                    />
                  </div>
                  <div className="p-3 bg-black/20 rounded-md border border-white/10 flex items-center justify-between">
                    <div>
                      <Label className="text-white">Autenticação em Duas Etapas</Label>
                      <p className="text-sm text-gray-200">Aumentar segurança do login</p>
                    </div>
                    <Switch defaultChecked={false} />
                  </div>
                  <div className="p-3 bg-black/20 rounded-md border border-white/10 flex items-center justify-between">
                    <div>
                      <Label className="text-white">Registro de Atividades</Label>
                      <p className="text-sm text-gray-200">Manter logs de acesso</p>
                    </div>
                    <Switch defaultChecked={true} />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="password-policy" className="text-white">Política de Senhas</Label>
                    <select
                      id="password-policy"
                      defaultValue="strong"
                      className="w-full bg-black/30 border border-white/20 rounded text-white p-2"
                    >
                      <option value="basic">Básica (mínimo 6 caracteres)</option>
                      <option value="medium">Média (8+ caracteres com números)</option>
                      <option value="strong">Forte (8+ caracteres com números e símbolos)</option>
                    </select>
                  </div>
                  <Button className="w-full mt-4 bg-gradient-to-r from-gray-700 to-gray-800 text-white hover:from-gray-600 hover:to-gray-700">
                    Aplicar Configurações
                  </Button>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

// Missing components for the demo
const Badge = ({ className, children }: { className?: string, children: React.ReactNode }) => (
  <span className={`px-2 py-1 text-xs rounded ${className}`}>{children}</span>
);

export default Admin;
