
import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { 
  ShoppingCart, 
  Search, 
  Filter, 
  Star,
  Heart,
  Eye,
  Cpu,
  HardDrive,
  Monitor,
  Keyboard,
  Mouse,
  Smartphone,
  Laptop,
  Headphones
} from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { useCompany } from '@/contexts/CompanyContext';

interface Product {
  id: string;
  name: string;
  description: string;
  price: number;
  originalPrice?: number;
  category: string;
  brand: string;
  rating: number;
  reviews: number;
  image: string;
  inStock: boolean;
  featured: boolean;
  specifications: { [key: string]: string };
}

export default function Marketplace() {
  const { selectedCompany } = useCompany();
  const { toast } = useToast();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [sortBy, setSortBy] = useState('featured');
  const [cart, setCart] = useState<{ productId: string; quantity: number }[]>([]);

  const categories = [
    { id: 'all', name: 'Todos', icon: <ShoppingCart className="h-4 w-4" /> },
    { id: 'processors', name: 'Processadores', icon: <Cpu className="h-4 w-4" /> },
    { id: 'memory', name: 'Memória RAM', icon: <HardDrive className="h-4 w-4" /> },
    { id: 'storage', name: 'Armazenamento', icon: <HardDrive className="h-4 w-4" /> },
    { id: 'monitors', name: 'Monitores', icon: <Monitor className="h-4 w-4" /> },
    { id: 'peripherals', name: 'Periféricos', icon: <Keyboard className="h-4 w-4" /> },
    { id: 'laptops', name: 'Notebooks', icon: <Laptop className="h-4 w-4" /> },
    { id: 'mobile', name: 'Smartphones', icon: <Smartphone className="h-4 w-4" /> },
  ];

  const products: Product[] = [
    {
      id: '1',
      name: 'Processador Intel Core i7-13700K',
      description: 'Processador de alta performance com 16 núcleos e 24 threads',
      price: 1899.99,
      originalPrice: 2199.99,
      category: 'processors',
      brand: 'Intel',
      rating: 4.8,
      reviews: 342,
      image: '/placeholder.svg',
      inStock: true,
      featured: true,
      specifications: {
        'Núcleos': '16 (8P + 8E)',
        'Threads': '24',
        'Frequência Base': '3.4 GHz',
        'Frequência Turbo': '5.4 GHz',
        'Socket': 'LGA 1700'
      }
    },
    {
      id: '2',
      name: 'Memória RAM Corsair 32GB DDR4',
      description: 'Kit de memória DDR4 3200MHz para alta performance',
      price: 899.99,
      category: 'memory',
      brand: 'Corsair',
      rating: 4.6,
      reviews: 156,
      image: '/placeholder.svg',
      inStock: true,
      featured: false,
      specifications: {
        'Capacidade': '32GB (2x16GB)',
        'Tipo': 'DDR4',
        'Frequência': '3200MHz',
        'Latência': 'CL16',
        'Voltagem': '1.35V'
      }
    },
    {
      id: '3',
      name: 'SSD Samsung 970 EVO Plus 1TB',
      description: 'SSD NVMe M.2 de alta velocidade para armazenamento',
      price: 549.99,
      category: 'storage',
      brand: 'Samsung',
      rating: 4.9,
      reviews: 892,
      image: '/placeholder.svg',
      inStock: true,
      featured: true,
      specifications: {
        'Capacidade': '1TB',
        'Interface': 'NVMe M.2',
        'Velocidade Leitura': '3,500 MB/s',
        'Velocidade Escrita': '3,300 MB/s',
        'Formato': '2280'
      }
    },
    {
      id: '4',
      name: 'Monitor LG UltraWide 34"',
      description: 'Monitor ultrawide 34" WQHD com tecnologia IPS',
      price: 1799.99,
      originalPrice: 2099.99,
      category: 'monitors',
      brand: 'LG',
      rating: 4.7,
      reviews: 234,
      image: '/placeholder.svg',
      inStock: true,
      featured: false,
      specifications: {
        'Tamanho': '34 polegadas',
        'Resolução': '3440x1440',
        'Painel': 'IPS',
        'Taxa Atualização': '144Hz',
        'Conectividade': 'HDMI, DisplayPort, USB-C'
      }
    }
  ];

  const filteredProducts = products.filter(product => {
    const matchesSearch = product.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         product.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || product.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const sortedProducts = [...filteredProducts].sort((a, b) => {
    switch (sortBy) {
      case 'price-low':
        return a.price - b.price;
      case 'price-high':
        return b.price - a.price;
      case 'rating':
        return b.rating - a.rating;
      case 'name':
        return a.name.localeCompare(b.name);
      default: // featured
        return b.featured ? 1 : -1;
    }
  });

  const addToCart = (productId: string) => {
    setCart(prev => {
      const existing = prev.find(item => item.productId === productId);
      if (existing) {
        return prev.map(item =>
          item.productId === productId
            ? { ...item, quantity: item.quantity + 1 }
            : item
        );
      }
      return [...prev, { productId, quantity: 1 }];
    });

    toast({
      title: "Produto adicionado",
      description: "Item adicionado ao carrinho com sucesso!",
    });
  };

  const getCartItemCount = () => {
    return cart.reduce((total, item) => total + item.quantity, 0);
  };

  return (
    <div className="min-h-screen bg-black text-white p-8 pt-24">
      <div className="container mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold gradient-text mb-2">
              {selectedCompany?.displayName} Store
            </h1>
            <p className="text-gray-400">
              Equipamentos e componentes de informática
            </p>
          </div>
          
          <Button className="bg-gradient-to-r from-electric to-tech hover:from-electric/80 hover:to-tech/80 relative">
            <ShoppingCart className="mr-2 h-4 w-4" />
            Carrinho
            {getCartItemCount() > 0 && (
              <Badge className="absolute -top-2 -right-2 bg-red-500 text-white text-xs">
                {getCartItemCount()}
              </Badge>
            )}
          </Button>
        </div>

        <Tabs defaultValue="products" className="space-y-6">
          <TabsList className="grid w-full grid-cols-3 bg-darker">
            <TabsTrigger value="products" className="data-[state=active]:bg-electric data-[state=active]:text-black">
              Produtos
            </TabsTrigger>
            <TabsTrigger value="categories" className="data-[state=active]:bg-electric data-[state=active]:text-black">
              Categorias
            </TabsTrigger>
            <TabsTrigger value="featured" className="data-[state=active]:bg-electric data-[state=active]:text-black">
              Destaques
            </TabsTrigger>
          </TabsList>

          <TabsContent value="products">
            {/* Filters */}
            <Card className="glass-effect border-white/10 mb-6">
              <CardContent className="p-4">
                <div className="flex flex-col md:flex-row gap-4">
                  <div className="flex-1">
                    <div className="relative">
                      <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                      <Input
                        placeholder="Buscar produtos..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="pl-10 bg-darker border-white/20 text-white"
                      />
                    </div>
                  </div>
                  
                  <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                    <SelectTrigger className="w-48 bg-darker border-white/20 text-white">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-dark border-white/20">
                      {categories.map((category) => (
                        <SelectItem key={category.id} value={category.id} className="text-white hover:bg-white/10">
                          <div className="flex items-center">
                            {category.icon}
                            <span className="ml-2">{category.name}</span>
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  
                  <Select value={sortBy} onValueChange={setSortBy}>
                    <SelectTrigger className="w-48 bg-darker border-white/20 text-white">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-dark border-white/20">
                      <SelectItem value="featured" className="text-white hover:bg-white/10">Destaques</SelectItem>
                      <SelectItem value="price-low" className="text-white hover:bg-white/10">Menor Preço</SelectItem>
                      <SelectItem value="price-high" className="text-white hover:bg-white/10">Maior Preço</SelectItem>
                      <SelectItem value="rating" className="text-white hover:bg-white/10">Melhor Avaliado</SelectItem>
                      <SelectItem value="name" className="text-white hover:bg-white/10">Nome A-Z</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </CardContent>
            </Card>

            {/* Products Grid */}
            <div className="grid md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {sortedProducts.map((product) => (
                <Card key={product.id} className="glass-effect border-white/10 hover:border-electric/30 transition-all duration-300 group">
                  <CardHeader className="p-4">
                    <div className="relative">
                      <img
                        src={product.image}
                        alt={product.name}
                        className="w-full h-48 object-cover rounded-lg bg-darker"
                      />
                      {product.featured && (
                        <Badge className="absolute top-2 left-2 bg-electric text-black">
                          Destaque
                        </Badge>
                      )}
                      <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
                        <Button size="sm" variant="outline" className="bg-black/50 border-white/20">
                          <Heart className="h-4 w-4" />
                        </Button>
                      </div>
                      {!product.inStock && (
                        <div className="absolute inset-0 bg-black/50 flex items-center justify-center rounded-lg">
                          <Badge variant="destructive">Fora de Estoque</Badge>
                        </div>
                      )}
                    </div>
                  </CardHeader>
                  <CardContent className="p-4">
                    <div className="mb-2">
                      <Badge variant="outline" className="text-xs">
                        {product.brand}
                      </Badge>
                    </div>
                    
                    <CardTitle className="text-white text-lg mb-2 line-clamp-2">
                      {product.name}
                    </CardTitle>
                    
                    <CardDescription className="text-gray-400 text-sm mb-3 line-clamp-2">
                      {product.description}
                    </CardDescription>
                    
                    <div className="flex items-center mb-3">
                      <div className="flex items-center">
                        {[...Array(5)].map((_, i) => (
                          <Star
                            key={i}
                            className={`h-4 w-4 ${
                              i < Math.floor(product.rating)
                                ? 'text-yellow-400 fill-current'
                                : 'text-gray-400'
                            }`}
                          />
                        ))}
                        <span className="ml-2 text-sm text-gray-400">
                          {product.rating} ({product.reviews})
                        </span>
                      </div>
                    </div>
                    
                    <div className="mb-4">
                      {product.originalPrice && (
                        <span className="text-gray-400 line-through text-sm mr-2">
                          R$ {product.originalPrice.toFixed(2)}
                        </span>
                      )}
                      <span className="text-electric font-bold text-xl">
                        R$ {product.price.toFixed(2)}
                      </span>
                    </div>
                    
                    <Button
                      onClick={() => addToCart(product.id)}
                      disabled={!product.inStock}
                      className="w-full bg-gradient-to-r from-electric to-tech hover:from-electric/80 hover:to-tech/80 disabled:opacity-50"
                    >
                      <ShoppingCart className="mr-2 h-4 w-4" />
                      {product.inStock ? 'Adicionar ao Carrinho' : 'Fora de Estoque'}
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="categories">
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
              {categories.filter(cat => cat.id !== 'all').map((category) => (
                <Card
                  key={category.id}
                  className="glass-effect border-white/10 hover:border-electric/30 transition-all duration-300 cursor-pointer"
                  onClick={() => {
                    setSelectedCategory(category.id);
                  }}
                >
                  <CardHeader className="text-center p-8">
                    <div className="w-16 h-16 bg-gradient-to-r from-electric/20 to-tech/20 rounded-full flex items-center justify-center mx-auto mb-4">
                      {category.icon}
                    </div>
                    <CardTitle className="text-white">{category.name}</CardTitle>
                    <CardDescription className="text-gray-400">
                      {products.filter(p => p.category === category.id).length} produtos
                    </CardDescription>
                  </CardHeader>
                </Card>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="featured">
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {products.filter(p => p.featured).map((product) => (
                <Card key={product.id} className="glass-effect border-electric/20">
                  <CardHeader>
                    <img
                      src={product.image}
                      alt={product.name}
                      className="w-full h-48 object-cover rounded-lg bg-darker"
                    />
                  </CardHeader>
                  <CardContent>
                    <CardTitle className="text-white mb-2">{product.name}</CardTitle>
                    <CardDescription className="text-gray-400 mb-4">
                      {product.description}
                    </CardDescription>
                    <div className="flex items-center justify-between">
                      <span className="text-electric font-bold text-xl">
                        R$ {product.price.toFixed(2)}
                      </span>
                      <Button
                        onClick={() => addToCart(product.id)}
                        className="bg-gradient-to-r from-electric to-tech hover:from-electric/80 hover:to-tech/80"
                      >
                        <ShoppingCart className="mr-2 h-4 w-4" />
                        Comprar
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
