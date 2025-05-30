
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { 
  ShoppingCart, 
  Store, 
  Package, 
  Truck, 
  BarChart3, 
  Tag, 
  Search, 
  Plus,
  CheckCircle,
  FileText,
  Settings,
  RefreshCcw,
  AlertTriangle
} from "lucide-react";

// Mock product data
const mockProducts = [
  {
    id: 1,
    name: "SSD Kingston A400 480GB",
    price: 279.90,
    stock: 15,
    image: "https://m.media-amazon.com/images/I/71NuO1r0QLL._AC_SX679_.jpg",
    category: "Armazenamento",
    published: {
      mercadolivre: true,
      shopee: true,
      americanas: false
    },
    status: "active"
  },
  {
    id: 2,
    name: "Memória RAM Corsair Vengeance 8GB DDR4",
    price: 199.90,
    stock: 8,
    image: "https://m.media-amazon.com/images/I/61GU6iiVpJS._AC_SL1500_.jpg",
    category: "Memória",
    published: {
      mercadolivre: true,
      shopee: false,
      americanas: true
    },
    status: "active"
  },
  {
    id: 3,
    name: "Mouse Gamer Logitech G203",
    price: 129.90,
    stock: 23,
    image: "https://m.media-amazon.com/images/I/51DQuESn8VS._AC_SL1500_.jpg",
    category: "Periféricos",
    published: {
      mercadolivre: true,
      shopee: true,
      americanas: true
    },
    status: "active"
  },
  {
    id: 4,
    name: "Monitor LG 24\" Full HD IPS",
    price: 699.90,
    stock: 4,
    image: "https://m.media-amazon.com/images/I/71nxeyxJAuL._AC_SL1500_.jpg",
    category: "Monitores",
    published: {
      mercadolivre: false,
      shopee: false,
      americanas: false
    },
    status: "inactive"
  },
  {
    id: 5,
    name: "Teclado Mecânico Redragon Kumara",
    price: 189.90,
    stock: 12,
    image: "https://m.media-amazon.com/images/I/61+WhnwgItL._AC_SL1500_.jpg",
    category: "Periféricos",
    published: {
      mercadolivre: true,
      shopee: true,
      americanas: false
    },
    status: "active"
  }
];

// Mock order data
const mockOrders = [
  {
    id: "ML-12345",
    marketplace: "mercadolivre",
    customer: "João da Silva",
    date: "2023-05-28",
    total: 279.90,
    status: "pending",
    items: [{id: 1, quantity: 1}]
  },
  {
    id: "SP-67890",
    marketplace: "shopee",
    customer: "Maria Oliveira",
    date: "2023-05-27",
    total: 329.80,
    status: "shipped",
    items: [{id: 3, quantity: 1}, {id: 5, quantity: 1}]
  },
  {
    id: "AM-24680",
    marketplace: "americanas",
    customer: "Carlos Santos",
    date: "2023-05-25",
    total: 199.90,
    status: "delivered",
    items: [{id: 2, quantity: 1}]
  }
];

// Mock marketplaces data
const marketplaces = [
  {
    id: "mercadolivre",
    name: "Mercado Livre",
    logo: "https://http2.mlstatic.com/frontend-assets/ui-navigation/5.19.1/mercadolibre/logo__large_plus@2x.png",
    color: "from-yellow-400 to-yellow-600",
    connected: true
  },
  {
    id: "shopee",
    name: "Shopee",
    logo: "https://deo.shopeemobile.com/shopee/shopee-mobilemall-live-sg/assets/d91264e165ed6facc6178994d5afae79.png",
    color: "from-orange-400 to-orange-600",
    connected: true
  },
  {
    id: "americanas",
    name: "Americanas",
    logo: "https://www.designi.com.br/images/preview/10222951.jpg",
    color: "from-red-400 to-red-600",
    connected: false
  }
];

const Marketplace = () => {
  const [products, setProducts] = useState(mockProducts);
  const [orders, setOrders] = useState(mockOrders);
  const [search, setSearch] = useState("");
  const [selectedMarketplaces, setSelectedMarketplaces] = useState<string[]>([]);
  const [isConnecting, setIsConnecting] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);

  // Filter products based on search
  const filteredProducts = products.filter(product =>
    product.name.toLowerCase().includes(search.toLowerCase())
  );

  // Handle marketplace connection
  const handleConnectMarketplace = (marketplaceId: string) => {
    setIsConnecting(true);
    
    // Simulate connection process
    setTimeout(() => {
      setIsConnecting(false);
      setShowSuccess(true);
      
      // Reset success message
      setTimeout(() => {
        setShowSuccess(false);
      }, 3000);
    }, 2000);
  };

  // Handle product publication
  const handlePublishProduct = (productId: number, marketplaceIds: string[]) => {
    setProducts(products.map(product =>
      product.id === productId
        ? {
            ...product,
            published: {
              ...product.published,
              ...marketplaceIds.reduce((acc, id) => ({ ...acc, [id]: true }), {})
            }
          }
        : product
    ));
  };

  // Render a marketplace indicator
  const MarketplaceIndicator = ({ id, isPublished }: { id: string, isPublished: boolean }) => {
    const marketplace = marketplaces.find(m => m.id === id);
    
    return (
      <span 
        className={`inline-block w-3 h-3 rounded-full mr-1 ${isPublished ? `bg-${id === 'mercadolivre' ? 'yellow' : id === 'shopee' ? 'orange' : 'red'}-500` : 'bg-gray-400'}`}
        title={`${isPublished ? 'Publicado' : 'Não publicado'} no ${marketplace?.name}`}
      ></span>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">
            Marketplace Integrado
          </h1>
          <p className="text-blue-200">Gerencie seus produtos em múltiplas plataformas</p>
        </div>
        
        {/* Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card className="bg-black/40 backdrop-blur-md border-white/20">
            <CardContent className="p-6">
              <div className="flex justify-between items-center">
                <div>
                  <p className="text-blue-200">Total de Produtos</p>
                  <h3 className="text-3xl font-bold text-white">{products.length}</h3>
                </div>
                <div className="p-3 rounded-full bg-blue-500/20">
                  <Package className="w-8 h-8 text-blue-400" />
                </div>
              </div>
              <div className="mt-4 text-sm text-blue-200">
                <span className="text-green-400">{products.filter(p => p.status === 'active').length}</span> ativos, 
                <span className="text-gray-400 ml-1">{products.filter(p => p.status === 'inactive').length}</span> inativos
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-black/40 backdrop-blur-md border-white/20">
            <CardContent className="p-6">
              <div className="flex justify-between items-center">
                <div>
                  <p className="text-blue-200">Pedidos Recentes</p>
                  <h3 className="text-3xl font-bold text-white">{orders.length}</h3>
                </div>
                <div className="p-3 rounded-full bg-purple-500/20">
                  <ShoppingCart className="w-8 h-8 text-purple-400" />
                </div>
              </div>
              <div className="mt-4 text-sm text-blue-200">
                <span className="text-yellow-400">{orders.filter(o => o.status === 'pending').length}</span> pendentes, 
                <span className="text-green-400 ml-1">{orders.filter(o => o.status === 'delivered').length}</span> entregues
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-black/40 backdrop-blur-md border-white/20">
            <CardContent className="p-6">
              <div className="flex justify-between items-center">
                <div>
                  <p className="text-blue-200">Plataformas Conectadas</p>
                  <h3 className="text-3xl font-bold text-white">{marketplaces.filter(m => m.connected).length}</h3>
                </div>
                <div className="p-3 rounded-full bg-green-500/20">
                  <Store className="w-8 h-8 text-green-400" />
                </div>
              </div>
              <div className="mt-4 text-sm text-blue-200">
                <span className="text-green-400">Mercado Livre, Shopee</span> ativos
              </div>
            </CardContent>
          </Card>
        </div>
        
        <Tabs defaultValue="products" className="space-y-6">
          <TabsList className="bg-black/40 backdrop-blur-md border-white/20 grid grid-cols-3 w-full max-w-md mx-auto">
            <TabsTrigger value="products" className="text-white">
              <Package className="w-4 h-4 mr-2" />
              Produtos
            </TabsTrigger>
            <TabsTrigger value="orders" className="text-white">
              <ShoppingCart className="w-4 h-4 mr-2" />
              Pedidos
            </TabsTrigger>
            <TabsTrigger value="marketplaces" className="text-white">
              <Store className="w-4 h-4 mr-2" />
              Plataformas
            </TabsTrigger>
          </TabsList>
          
          {/* Products Tab */}
          <TabsContent value="products">
            <Card className="bg-black/40 backdrop-blur-md border-white/20">
              <CardHeader className="flex flex-col sm:flex-row items-start sm:items-center justify-between space-y-2 sm:space-y-0">
                <CardTitle className="text-white">
                  Gerenciar Produtos
                </CardTitle>
                <div className="flex gap-2 w-full sm:w-auto">
                  <div className="relative flex-grow">
                    <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-gray-400" />
                    <Input
                      placeholder="Buscar produtos..."
                      value={search}
                      onChange={(e) => setSearch(e.target.value)}
                      className="bg-black/30 border-white/20 pl-8 text-white w-full"
                    />
                  </div>
                  <Button className="bg-gradient-to-r from-blue-600 to-purple-600">
                    <Plus className="w-4 h-4 mr-2" />
                    Adicionar
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-white/10">
                        <th className="text-left py-3 px-4 text-blue-200 font-normal">Produto</th>
                        <th className="text-left py-3 px-4 text-blue-200 font-normal">Preço</th>
                        <th className="text-left py-3 px-4 text-blue-200 font-normal">Estoque</th>
                        <th className="text-left py-3 px-4 text-blue-200 font-normal">Marketplaces</th>
                        <th className="text-left py-3 px-4 text-blue-200 font-normal">Status</th>
                        <th className="text-right py-3 px-4 text-blue-200 font-normal">Ações</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredProducts.map(product => (
                        <tr key={product.id} className="border-b border-white/5 hover:bg-white/5">
                          <td className="py-3 px-4">
                            <div className="flex items-center gap-3">
                              <div className="w-10 h-10 rounded bg-white flex items-center justify-center overflow-hidden">
                                <img src={product.image} alt={product.name} className="w-full h-full object-cover" />
                              </div>
                              <div>
                                <p className="text-white font-medium">{product.name}</p>
                                <p className="text-sm text-blue-200">{product.category}</p>
                              </div>
                            </div>
                          </td>
                          <td className="py-3 px-4 text-white">R$ {product.price.toFixed(2)}</td>
                          <td className="py-3 px-4 text-white">{product.stock} un.</td>
                          <td className="py-3 px-4">
                            <div className="flex space-x-1">
                              <MarketplaceIndicator id="mercadolivre" isPublished={product.published.mercadolivre} />
                              <MarketplaceIndicator id="shopee" isPublished={product.published.shopee} />
                              <MarketplaceIndicator id="americanas" isPublished={product.published.americanas} />
                            </div>
                          </td>
                          <td className="py-3 px-4">
                            <span className={`px-2 py-1 text-xs rounded-full ${product.status === 'active' ? 'bg-green-500/20 text-green-300' : 'bg-gray-500/20 text-gray-300'}`}>
                              {product.status === 'active' ? 'Ativo' : 'Inativo'}
                            </span>
                          </td>
                          <td className="py-3 px-4 text-right">
                            <Dialog>
                              <DialogTrigger asChild>
                                <Button variant="outline" size="sm" className="border-white/30 text-white hover:bg-white/10">
                                  Publicar
                                </Button>
                              </DialogTrigger>
                              <DialogContent className="bg-slate-900 border-white/20 text-white">
                                <DialogHeader>
                                  <DialogTitle>Publicar Produto</DialogTitle>
                                  <DialogDescription className="text-blue-200">
                                    Selecione os marketplaces onde deseja publicar este produto.
                                  </DialogDescription>
                                </DialogHeader>
                                <div className="space-y-4 py-4">
                                  <div className="space-y-2">
                                    <Label className="text-white">Produto</Label>
                                    <div className="flex items-center gap-3 p-3 bg-black/30 rounded-md">
                                      <div className="w-12 h-12 rounded bg-white flex items-center justify-center overflow-hidden">
                                        <img src={product.image} alt={product.name} className="w-full h-full object-cover" />
                                      </div>
                                      <div>
                                        <p className="text-white font-medium">{product.name}</p>
                                        <p className="text-sm text-blue-200">R$ {product.price.toFixed(2)} • {product.stock} em estoque</p>
                                      </div>
                                    </div>
                                  </div>
                                  <div className="space-y-2">
                                    <Label className="text-white">Selecione os Marketplaces</Label>
                                    <div className="space-y-2">
                                      {marketplaces.map(marketplace => (
                                        <div 
                                          key={marketplace.id}
                                          className={`
                                            p-3 border rounded-md flex items-center justify-between cursor-pointer
                                            ${selectedMarketplaces.includes(marketplace.id) 
                                              ? `border-${marketplace.id === 'mercadolivre' ? 'yellow' : marketplace.id === 'shopee' ? 'orange' : 'red'}-500/50 bg-black/50` 
                                              : 'border-white/10 hover:border-white/30 bg-black/20'}
                                            ${!marketplace.connected && 'opacity-50'}
                                          `}
                                          onClick={() => {
                                            if (!marketplace.connected) return;
                                            setSelectedMarketplaces(
                                              selectedMarketplaces.includes(marketplace.id)
                                                ? selectedMarketplaces.filter(id => id !== marketplace.id)
                                                : [...selectedMarketplaces, marketplace.id]
                                            );
                                          }}
                                        >
                                          <div className="flex items-center gap-3">
                                            <div className="w-8 h-8 rounded bg-white flex items-center justify-center p-1">
                                              <img src={marketplace.logo} alt={marketplace.name} className="w-full h-full object-contain" />
                                            </div>
                                            <span className="text-white">{marketplace.name}</span>
                                          </div>
                                          {marketplace.connected ? (
                                            <div className={`
                                              w-5 h-5 rounded-full border-2 flex items-center justify-center
                                              ${selectedMarketplaces.includes(marketplace.id) 
                                                ? `border-${marketplace.id === 'mercadolivre' ? 'yellow' : marketplace.id === 'shopee' ? 'orange' : 'red'}-500 bg-${marketplace.id === 'mercadolivre' ? 'yellow' : marketplace.id === 'shopee' ? 'orange' : 'red'}-500` 
                                                : 'border-white/30'}
                                            `}>
                                              {selectedMarketplaces.includes(marketplace.id) && (
                                                <CheckCircle className="w-3 h-3 text-black" />
                                              )}
                                            </div>
                                          ) : (
                                            <span className="text-sm text-gray-400">Desconectado</span>
                                          )}
                                        </div>
                                      ))}
                                    </div>
                                  </div>
                                </div>
                                <DialogFooter>
                                  <Button variant="outline" className="border-white/30 text-white hover:bg-white/10">
                                    Cancelar
                                  </Button>
                                  <Button 
                                    className="bg-gradient-to-r from-blue-600 to-purple-600"
                                    onClick={() => handlePublishProduct(product.id, selectedMarketplaces)}
                                  >
                                    Publicar Agora
                                  </Button>
                                </DialogFooter>
                              </DialogContent>
                            </Dialog>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
          
          {/* Orders Tab */}
          <TabsContent value="orders">
            <Card className="bg-black/40 backdrop-blur-md border-white/20">
              <CardHeader>
                <CardTitle className="text-white">
                  Pedidos Recentes
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-white/10">
                        <th className="text-left py-3 px-4 text-blue-200 font-normal">ID</th>
                        <th className="text-left py-3 px-4 text-blue-200 font-normal">Marketplace</th>
                        <th className="text-left py-3 px-4 text-blue-200 font-normal">Cliente</th>
                        <th className="text-left py-3 px-4 text-blue-200 font-normal">Data</th>
                        <th className="text-left py-3 px-4 text-blue-200 font-normal">Valor</th>
                        <th className="text-left py-3 px-4 text-blue-200 font-normal">Status</th>
                        <th className="text-right py-3 px-4 text-blue-200 font-normal">Ações</th>
                      </tr>
                    </thead>
                    <tbody>
                      {orders.map(order => (
                        <tr key={order.id} className="border-b border-white/5 hover:bg-white/5">
                          <td className="py-3 px-4 text-white">{order.id}</td>
                          <td className="py-3 px-4">
                            <div className="flex items-center gap-2">
                              <div className="w-6 h-6 rounded bg-white flex items-center justify-center p-0.5">
                                <img 
                                  src={marketplaces.find(m => m.id === order.marketplace)?.logo} 
                                  alt={order.marketplace} 
                                  className="w-full h-full object-contain" 
                                />
                              </div>
                              <span className="text-white">
                                {marketplaces.find(m => m.id === order.marketplace)?.name}
                              </span>
                            </div>
                          </td>
                          <td className="py-3 px-4 text-white">{order.customer}</td>
                          <td className="py-3 px-4 text-white">{new Date(order.date).toLocaleDateString('pt-BR')}</td>
                          <td className="py-3 px-4 text-white">R$ {order.total.toFixed(2)}</td>
                          <td className="py-3 px-4">
                            <span className={`
                              px-2 py-1 text-xs rounded-full
                              ${order.status === 'pending' ? 'bg-yellow-500/20 text-yellow-300' : 
                                order.status === 'shipped' ? 'bg-blue-500/20 text-blue-300' :
                                'bg-green-500/20 text-green-300'}
                            `}>
                              {order.status === 'pending' ? 'Aguardando' : 
                               order.status === 'shipped' ? 'Enviado' : 'Entregue'}
                            </span>
                          </td>
                          <td className="py-3 px-4 text-right">
                            <Dialog>
                              <DialogTrigger asChild>
                                <Button variant="outline" size="sm" className="border-white/30 text-white hover:bg-white/10">
                                  Detalhes
                                </Button>
                              </DialogTrigger>
                              <DialogContent className="bg-slate-900 border-white/20 text-white">
                                <DialogHeader>
                                  <DialogTitle>Detalhes do Pedido</DialogTitle>
                                  <DialogDescription className="text-blue-200">
                                    Pedido {order.id} - {new Date(order.date).toLocaleDateString('pt-BR')}
                                  </DialogDescription>
                                </DialogHeader>
                                <div className="space-y-4 py-4">
                                  {/* Cliente Info */}
                                  <div className="bg-black/30 p-3 rounded-md">
                                    <h3 className="text-white font-medium mb-2">Informações do Cliente</h3>
                                    <p className="text-blue-200">Nome: {order.customer}</p>
                                    <p className="text-blue-200">Pedido via: {marketplaces.find(m => m.id === order.marketplace)?.name}</p>
                                  </div>
                                  
                                  {/* Produtos */}
                                  <div className="bg-black/30 p-3 rounded-md">
                                    <h3 className="text-white font-medium mb-2">Produtos</h3>
                                    <div className="space-y-2">
                                      {order.items.map((item) => {
                                        const product = products.find(p => p.id === item.id);
                                        return (
                                          <div key={item.id} className="flex justify-between">
                                            <div className="flex items-center gap-2">
                                              <div className="w-8 h-8 rounded bg-white flex items-center justify-center overflow-hidden">
                                                <img src={product?.image} alt={product?.name} className="w-full h-full object-cover" />
                                              </div>
                                              <div>
                                                <p className="text-white">{product?.name}</p>
                                                <p className="text-sm text-blue-200">Qtd: {item.quantity}</p>
                                              </div>
                                            </div>
                                            <p className="text-white">R$ {(product?.price || 0).toFixed(2)}</p>
                                          </div>
                                        );
                                      })}
                                    </div>
                                    <div className="mt-3 pt-3 border-t border-white/10 flex justify-between">
                                      <p className="text-white font-medium">Total</p>
                                      <p className="text-white font-medium">R$ {order.total.toFixed(2)}</p>
                                    </div>
                                  </div>
                                  
                                  {/* Status */}
                                  <div className="bg-black/30 p-3 rounded-md">
                                    <h3 className="text-white font-medium mb-2">Status do Pedido</h3>
                                    <div className="flex items-center gap-2">
                                      <span className={`
                                        px-2 py-1 text-xs rounded-full
                                        ${order.status === 'pending' ? 'bg-yellow-500/20 text-yellow-300' : 
                                          order.status === 'shipped' ? 'bg-blue-500/20 text-blue-300' :
                                          'bg-green-500/20 text-green-300'}
                                      `}>
                                        {order.status === 'pending' ? 'Aguardando' : 
                                         order.status === 'shipped' ? 'Enviado' : 'Entregue'}
                                      </span>
                                      <select className="bg-black/50 text-white border border-white/20 rounded py-1 px-2 text-sm ml-2">
                                        <option value="pending">Aguardando</option>
                                        <option value="shipped">Enviado</option>
                                        <option value="delivered">Entregue</option>
                                        <option value="cancelled">Cancelado</option>
                                      </select>
                                    </div>
                                  </div>
                                </div>
                                <DialogFooter className="space-x-2">
                                  <Button variant="outline" className="border-white/30 text-white hover:bg-white/10">
                                    <FileText className="w-4 h-4 mr-2" />
                                    Imprimir
                                  </Button>
                                  <Button 
                                    className="bg-gradient-to-r from-blue-600 to-purple-600"
                                  >
                                    Atualizar Pedido
                                  </Button>
                                </DialogFooter>
                              </DialogContent>
                            </Dialog>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
          
          {/* Marketplaces Tab */}
          <TabsContent value="marketplaces">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {marketplaces.map(marketplace => (
                <Card 
                  key={marketplace.id}
                  className={`
                    bg-gradient-to-br from-black/80 to-black/40
                    backdrop-blur-md border-white/10 overflow-hidden
                  `}
                >
                  <div className={`h-1 bg-gradient-to-r ${marketplace.color}`}></div>
                  <CardContent className="p-6">
                    <div className="flex justify-between items-center mb-4">
                      <div className="flex items-center gap-3">
                        <div className="w-12 h-12 rounded-md bg-white flex items-center justify-center p-1 shadow-lg">
                          <img src={marketplace.logo} alt={marketplace.name} className="w-full h-full object-contain" />
                        </div>
                        <div>
                          <h3 className="text-white text-xl font-medium">{marketplace.name}</h3>
                          <p className="text-sm text-blue-200">
                            {marketplace.connected ? 'Conectado' : 'Não conectado'}
                          </p>
                        </div>
                      </div>
                      <div>
                        {marketplace.connected ? (
                          <Badge className="bg-green-500/20 text-green-300">Conectado</Badge>
                        ) : (
                          <Badge className="bg-gray-500/20 text-gray-300">Desconectado</Badge>
                        )}
                      </div>
                    </div>
                    
                    {marketplace.connected ? (
                      <div className="space-y-5">
                        {/* Stats */}
                        <div className="grid grid-cols-3 gap-2">
                          <div className="p-3 bg-black/30 rounded">
                            <p className="text-sm text-blue-200">Produtos</p>
                            <p className="text-xl font-medium text-white">
                              {products.filter(p => p.published[marketplace.id]).length}
                            </p>
                          </div>
                          <div className="p-3 bg-black/30 rounded">
                            <p className="text-sm text-blue-200">Pedidos</p>
                            <p className="text-xl font-medium text-white">
                              {orders.filter(o => o.marketplace === marketplace.id).length}
                            </p>
                          </div>
                          <div className="p-3 bg-black/30 rounded">
                            <p className="text-sm text-blue-200">Vendas</p>
                            <p className="text-xl font-medium text-white">
                              R$ {orders.filter(o => o.marketplace === marketplace.id)
                                 .reduce((sum, order) => sum + order.total, 0)
                                 .toFixed(2)}
                            </p>
                          </div>
                        </div>
                        
                        {/* Actions */}
                        <div className="flex space-x-2">
                          <Button 
                            variant="outline" 
                            className="flex-1 border-white/30 text-white hover:bg-white/10"
                            onClick={() => {}}
                          >
                            <RefreshCcw className="w-4 h-4 mr-2" />
                            Sincronizar
                          </Button>
                          <Button 
                            variant="outline"
                            className="flex-1 border-white/30 text-white hover:bg-white/10"
                            onClick={() => {}}
                          >
                            <Settings className="w-4 h-4 mr-2" />
                            Configurar
                          </Button>
                        </div>
                      </div>
                    ) : (
                      <div className="mt-4 space-y-5">
                        <div className="bg-black/30 p-4 rounded-md flex items-center gap-3">
                          <AlertTriangle className="w-6 h-6 text-yellow-400" />
                          <p className="text-blue-200">
                            Conecte sua conta do {marketplace.name} para começar a vender seus produtos.
                          </p>
                        </div>
                        <Button 
                          className={`w-full bg-gradient-to-r ${marketplace.color}`}
                          onClick={() => handleConnectMarketplace(marketplace.id)}
                          disabled={isConnecting}
                        >
                          {isConnecting ? (
                            <>
                              <RefreshCcw className="w-4 h-4 mr-2 animate-spin" />
                              Conectando...
                            </>
                          ) : (
                            <>
                              <Store className="w-4 h-4 mr-2" />
                              Conectar ao {marketplace.name}
                            </>
                          )}
                        </Button>
                        {showSuccess && (
                          <div className="bg-green-500/20 border border-green-500/40 text-green-300 p-3 rounded-md mt-4 flex items-center gap-2">
                            <CheckCircle className="w-4 h-4" />
                            Conectado com sucesso!
                          </div>
                        )}
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))}
              
              {/* Integration Features Card */}
              <Card className="bg-black/40 backdrop-blur-md border-white/20 md:col-span-2">
                <CardHeader>
                  <CardTitle className="text-white flex items-center gap-2">
                    <BarChart3 className="w-5 h-5" />
                    Recursos da Integração
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="p-4 bg-black/20 rounded-md border border-white/10">
                      <div className="mb-3 p-2 rounded-full bg-blue-500/20 w-fit">
                        <Tag className="w-6 h-6 text-blue-400" />
                      </div>
                      <h3 className="text-lg font-medium text-white mb-2">Gerenciamento de Preços</h3>
                      <p className="text-blue-200 text-sm">Atualize preços em todas as plataformas automaticamente a partir do sistema.</p>
                    </div>
                    <div className="p-4 bg-black/20 rounded-md border border-white/10">
                      <div className="mb-3 p-2 rounded-full bg-purple-500/20 w-fit">
                        <Package className="w-6 h-6 text-purple-400" />
                      </div>
                      <h3 className="text-lg font-medium text-white mb-2">Controle de Estoque</h3>
                      <p className="text-blue-200 text-sm">Sincronização automática de estoque entre todas as plataformas conectadas.</p>
                    </div>
                    <div className="p-4 bg-black/20 rounded-md border border-white/10">
                      <div className="mb-3 p-2 rounded-full bg-green-500/20 w-fit">
                        <Truck className="w-6 h-6 text-green-400" />
                      </div>
                      <h3 className="text-lg font-medium text-white mb-2">Gestão de Entregas</h3>
                      <p className="text-blue-200 text-sm">Acompanhe o status de entrega dos pedidos de todas as plataformas em um só lugar.</p>
                    </div>
                  </div>
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

export default Marketplace;
