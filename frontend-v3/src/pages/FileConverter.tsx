
import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  FileText, 
  Image, 
  Music, 
  Video, 
  Upload, 
  Download, 
  RefreshCw, 
  Check,
  File,
  AlertCircle
} from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

interface ConversionJob {
  id: string;
  fileName: string;
  fromFormat: string;
  toFormat: string;
  status: 'pending' | 'converting' | 'completed' | 'error';
  progress: number;
  downloadUrl?: string;
}

export default function FileConverter() {
  const { toast } = useToast();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [fromFormat, setFromFormat] = useState('');
  const [toFormat, setToFormat] = useState('');
  const [conversions, setConversions] = useState<ConversionJob[]>([]);
  const [converting, setConverting] = useState(false);

  const documentFormats = ['pdf', 'docx', 'doc', 'txt', 'rtf', 'odt', 'xlsx', 'pptx'];
  const imageFormats = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp', 'svg'];
  const audioFormats = ['mp3', 'wav', 'flac', 'aac', 'ogg', 'm4a', 'wma'];
  const videoFormats = ['mp4', 'avi', 'mkv', 'mov', 'wmv', 'flv', 'webm', '3gp'];

  const getFormatIcon = (format: string) => {
    if (documentFormats.includes(format.toLowerCase())) return <FileText className="h-4 w-4" />;
    if (imageFormats.includes(format.toLowerCase())) return <Image className="h-4 w-4" />;
    if (audioFormats.includes(format.toLowerCase())) return <Music className="h-4 w-4" />;
    if (videoFormats.includes(format.toLowerCase())) return <Video className="h-4 w-4" />;
    return <File className="h-4 w-4" />;
  };

  const getFileType = (fileName: string) => {
    const extension = fileName.split('.').pop()?.toLowerCase() || '';
    if (documentFormats.includes(extension)) return 'document';
    if (imageFormats.includes(extension)) return 'image';
    if (audioFormats.includes(extension)) return 'audio';
    if (videoFormats.includes(extension)) return 'video';
    return 'other';
  };

  const getAvailableFormats = (currentFormat: string) => {
    const type = getFileType(`file.${currentFormat}`);
    switch (type) {
      case 'document': return documentFormats;
      case 'image': return imageFormats;
      case 'audio': return audioFormats;
      case 'video': return videoFormats;
      default: return [];
    }
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      const extension = file.name.split('.').pop()?.toLowerCase() || '';
      setFromFormat(extension);
      setToFormat('');
    }
  };

  const simulateConversion = async (job: ConversionJob) => {
    const steps = [10, 25, 50, 75, 90, 100];
    
    for (const progress of steps) {
      await new Promise(resolve => setTimeout(resolve, 1000));
      setConversions(prev => prev.map(conv => 
        conv.id === job.id 
          ? { ...conv, progress, status: progress === 100 ? 'completed' : 'converting' }
          : conv
      ));
    }

    // Simular URL de download
    setConversions(prev => prev.map(conv => 
      conv.id === job.id 
        ? { 
            ...conv, 
            downloadUrl: `https://example.com/download/${job.fileName.replace(/\.[^/.]+$/, '')}.${job.toFormat}`,
            status: 'completed'
          }
        : conv
    ));
  };

  const handleConvert = async () => {
    if (!selectedFile || !fromFormat || !toFormat) {
      toast({
        title: "Erro",
        description: "Por favor, selecione um arquivo e os formatos de conversão.",
        variant: "destructive",
      });
      return;
    }

    setConverting(true);

    const newJob: ConversionJob = {
      id: Date.now().toString(),
      fileName: selectedFile.name,
      fromFormat,
      toFormat,
      status: 'converting',
      progress: 0
    };

    setConversions(prev => [newJob, ...prev]);

    try {
      await simulateConversion(newJob);
      
      toast({
        title: "Conversão concluída",
        description: `Arquivo convertido de ${fromFormat.toUpperCase()} para ${toFormat.toUpperCase()} com sucesso!`,
      });
    } catch (error) {
      setConversions(prev => prev.map(conv => 
        conv.id === newJob.id 
          ? { ...conv, status: 'error' }
          : conv
      ));
      
      toast({
        title: "Erro na conversão",
        description: "Ocorreu um erro durante a conversão do arquivo.",
        variant: "destructive",
      });
    } finally {
      setConverting(false);
      setSelectedFile(null);
      setFromFormat('');
      setToFormat('');
    }
  };

  const getStatusColor = (status: ConversionJob['status']) => {
    switch (status) {
      case 'pending': return 'bg-gray-500';
      case 'converting': return 'bg-blue-500';
      case 'completed': return 'bg-green-500';
      case 'error': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const getStatusIcon = (status: ConversionJob['status']) => {
    switch (status) {
      case 'pending': return <RefreshCw className="h-4 w-4" />;
      case 'converting': return <RefreshCw className="h-4 w-4 animate-spin" />;
      case 'completed': return <Check className="h-4 w-4" />;
      case 'error': return <AlertCircle className="h-4 w-4" />;
      default: return <RefreshCw className="h-4 w-4" />;
    }
  };

  return (
    <div className="min-h-screen bg-black text-white p-8 pt-24">
      <div className="container mx-auto max-w-4xl">
        <div className="mb-8">
          <h1 className="text-3xl font-bold gradient-text mb-2">
            Conversor de Arquivos
          </h1>
          <p className="text-gray-400">
            Converta documentos, imagens, áudios e vídeos entre diferentes formatos
          </p>
        </div>

        <Tabs defaultValue="converter" className="space-y-6">
          <TabsList className="grid w-full grid-cols-2 bg-darker">
            <TabsTrigger value="converter" className="data-[state=active]:bg-electric data-[state=active]:text-black">
              Converter Arquivo
            </TabsTrigger>
            <TabsTrigger value="history" className="data-[state=active]:bg-electric data-[state=active]:text-black">
              Histórico
            </TabsTrigger>
          </TabsList>

          <TabsContent value="converter">
            <Card className="glass-effect border-white/10">
              <CardHeader>
                <CardTitle className="text-white flex items-center">
                  <RefreshCw className="mr-2 h-5 w-5 text-electric" />
                  Converter Arquivo
                </CardTitle>
                <CardDescription className="text-gray-400">
                  Selecione um arquivo e escolha o formato de destino
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div>
                  <Label htmlFor="file" className="text-white mb-2 block">Selecionar Arquivo</Label>
                  <div className="border-2 border-dashed border-white/20 rounded-lg p-8 text-center hover:border-electric/50 transition-colors">
                    <Input
                      id="file"
                      type="file"
                      onChange={handleFileSelect}
                      className="hidden"
                      accept=".pdf,.doc,.docx,.txt,.jpg,.jpeg,.png,.gif,.mp3,.wav,.mp4,.avi,*"
                    />
                    <Label htmlFor="file" className="cursor-pointer">
                      <Upload className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                      <p className="text-white mb-2">
                        {selectedFile ? selectedFile.name : 'Clique para selecionar um arquivo'}
                      </p>
                      <p className="text-gray-400 text-sm">
                        Suporte para documentos, imagens, áudios e vídeos
                      </p>
                    </Label>
                  </div>
                </div>

                {selectedFile && (
                  <div className="grid md:grid-cols-2 gap-4">
                    <div>
                      <Label className="text-white">Formato Original</Label>
                      <div className="flex items-center p-3 bg-darker rounded-lg mt-2">
                        {getFormatIcon(fromFormat)}
                        <span className="ml-2 text-white uppercase">{fromFormat}</span>
                      </div>
                    </div>
                    
                    <div>
                      <Label className="text-white">Converter Para</Label>
                      <Select value={toFormat} onValueChange={setToFormat}>
                        <SelectTrigger className="bg-darker border-white/20 text-white mt-2">
                          <SelectValue placeholder="Selecione o formato" />
                        </SelectTrigger>
                        <SelectContent className="bg-dark border-white/20">
                          {getAvailableFormats(fromFormat).map((format) => (
                            <SelectItem key={format} value={format} className="text-white hover:bg-white/10">
                              <div className="flex items-center">
                                {getFormatIcon(format)}
                                <span className="ml-2 uppercase">{format}</span>
                              </div>
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                )}

                <Button
                  onClick={handleConvert}
                  disabled={!selectedFile || !toFormat || converting}
                  className="w-full bg-gradient-to-r from-electric to-tech hover:from-electric/80 hover:to-tech/80"
                >
                  {converting ? (
                    <>
                      <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                      Convertendo...
                    </>
                  ) : (
                    <>
                      <RefreshCw className="mr-2 h-4 w-4" />
                      Converter Arquivo
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="history">
            <Card className="glass-effect border-white/10">
              <CardHeader>
                <CardTitle className="text-white flex items-center">
                  <FileText className="mr-2 h-5 w-5 text-electric" />
                  Histórico de Conversões
                </CardTitle>
                <CardDescription className="text-gray-400">
                  Acompanhe suas conversões recentes
                </CardDescription>
              </CardHeader>
              <CardContent>
                {conversions.length === 0 ? (
                  <div className="text-center py-8">
                    <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-400">Nenhuma conversão realizada ainda</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {conversions.map((job) => (
                      <div key={job.id} className="p-4 bg-darker/50 rounded-lg border border-white/10">
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center space-x-3">
                            {getFormatIcon(job.fromFormat)}
                            <span className="text-white font-medium">{job.fileName}</span>
                            <Badge variant="outline" className="text-xs">
                              {job.fromFormat.toUpperCase()} → {job.toFormat.toUpperCase()}
                            </Badge>
                          </div>
                          
                          <div className="flex items-center space-x-2">
                            <Badge className={getStatusColor(job.status)}>
                              {getStatusIcon(job.status)}
                              <span className="ml-1 capitalize">{job.status}</span>
                            </Badge>
                            
                            {job.status === 'completed' && job.downloadUrl && (
                              <Button
                                size="sm"
                                variant="outline"
                                className="border-green-500/20 text-green-400 hover:bg-green-500/10"
                              >
                                <Download className="h-4 w-4 mr-1" />
                                Download
                              </Button>
                            )}
                          </div>
                        </div>
                        
                        {job.status === 'converting' && (
                          <Progress value={job.progress} className="h-2" />
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
