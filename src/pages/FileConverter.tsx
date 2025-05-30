
import { useState, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useDropzone } from "react-dropzone";
import { 
  FileText, 
  Image, 
  Music, 
  RefreshCcw, 
  Download, 
  ArrowRight, 
  Upload, 
  FileInput,
  FilePlus2,
  FileOutput,
  FileCode
} from "lucide-react";

// Mock function to simulate file conversion (in a real app you would use actual conversion libraries)
const mockConvert = async (file: File, targetFormat: string) => {
  // Simulate conversion delay
  await new Promise(resolve => setTimeout(resolve, 2000));
  
  // Create a mock output file (in reality, this would be the converted file)
  const mockOutput = new File(
    [file], 
    `converted_file.${targetFormat}`,
    { type: `application/${targetFormat}` }
  );
  
  return mockOutput;
};

const FileConverter = () => {
  const [activeTab, setActiveTab] = useState("documents");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [convertedFile, setConvertedFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [selectedFormat, setSelectedFormat] = useState("");
  const [error, setError] = useState("");
  
  // Configuration for different conversion types
  const conversionTypes = {
    documents: {
      title: "Conversor de Documentos",
      description: "Converta entre formatos como PDF, DOCX, TXT e mais",
      icon: <FileText className="w-10 h-10 text-blue-400" />,
      acceptedFiles: ".pdf,.doc,.docx,.txt,.rtf,.odt",
      formats: ["pdf", "docx", "txt", "rtf"]
    },
    images: {
      title: "Conversor de Imagens",
      description: "Transforme entre formatos de imagem como JPG, PNG, WEBP",
      icon: <Image className="w-10 h-10 text-purple-400" />,
      acceptedFiles: ".jpg,.jpeg,.png,.webp,.gif,.bmp,.tiff",
      formats: ["jpg", "png", "webp", "gif"]
    },
    audio: {
      title: "Conversor de Áudio",
      description: "Converta arquivos de áudio entre MP3, WAV, FLAC e outros",
      icon: <Music className="w-10 h-10 text-green-400" />,
      acceptedFiles: ".mp3,.wav,.flac,.aac,.ogg",
      formats: ["mp3", "wav", "flac", "ogg"]
    },
    code: {
      title: "Formatador de Código",
      description: "Formatar e converter arquivos de código",
      icon: <FileCode className="w-10 h-10 text-yellow-400" />,
      acceptedFiles: ".js,.ts,.jsx,.tsx,.html,.css,.json",
      formats: ["format", "minify", "beautify"]
    }
  };

  // Get current configuration based on active tab
  const currentConfig = conversionTypes[activeTab as keyof typeof conversionTypes];
  
  // Handle file drop
  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      setSelectedFile(acceptedFiles[0]);
      setConvertedFile(null);
      setError("");
    }
  }, []);
  
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      [currentConfig.acceptedFiles]: []
    },
    maxFiles: 1
  });
  
  // Handle file conversion
  const handleConvert = async () => {
    if (!selectedFile || !selectedFormat) {
      setError("Por favor selecione um arquivo e um formato de destino");
      return;
    }
    
    setLoading(true);
    setError("");
    
    try {
      const result = await mockConvert(selectedFile, selectedFormat);
      setConvertedFile(result);
    } catch (err) {
      console.error("Error converting file:", err);
      setError("Ocorreu um erro ao converter o arquivo");
    } finally {
      setLoading(false);
    }
  };
  
  // Handle format change
  const handleFormatChange = (format: string) => {
    setSelectedFormat(format);
  };
  
  // Handle file download
  const handleDownload = () => {
    if (!convertedFile) return;
    
    // Create a download link
    const url = URL.createObjectURL(convertedFile);
    const a = document.createElement("a");
    a.href = url;
    a.download = convertedFile.name;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };
  
  // Reset the converter
  const handleReset = () => {
    setSelectedFile(null);
    setConvertedFile(null);
    setSelectedFormat("");
    setError("");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">
            Conversor de Arquivos
          </h1>
          <p className="text-blue-200">Converta arquivos em diferentes formatos facilmente</p>
        </div>
        
        <Tabs
          value={activeTab}
          onValueChange={setActiveTab}
          className="space-y-6"
        >
          <TabsList className="bg-black/40 backdrop-blur-md border-white/20 grid grid-cols-4 w-full max-w-3xl mx-auto">
            <TabsTrigger value="documents" className="text-white">
              <FileText className="w-4 h-4 mr-2" />
              Documentos
            </TabsTrigger>
            <TabsTrigger value="images" className="text-white">
              <Image className="w-4 h-4 mr-2" />
              Imagens
            </TabsTrigger>
            <TabsTrigger value="audio" className="text-white">
              <Music className="w-4 h-4 mr-2" />
              Áudio
            </TabsTrigger>
            <TabsTrigger value="code" className="text-white">
              <FileCode className="w-4 h-4 mr-2" />
              Código
            </TabsTrigger>
          </TabsList>
          
          {Object.keys(conversionTypes).map(type => (
            <TabsContent key={type} value={type}>
              <Card className="bg-black/40 backdrop-blur-md border-white/20">
                <CardHeader className="text-center">
                  <div className="flex justify-center mb-3">
                    {conversionTypes[type as keyof typeof conversionTypes].icon}
                  </div>
                  <CardTitle className="text-2xl text-white">
                    {conversionTypes[type as keyof typeof conversionTypes].title}
                  </CardTitle>
                  <p className="text-blue-200">
                    {conversionTypes[type as keyof typeof conversionTypes].description}
                  </p>
                </CardHeader>
                <CardContent className="space-y-6">
                  {/* File Upload Area */}
                  {!selectedFile ? (
                    <div
                      {...getRootProps()}
                      className={`
                        border-2 border-dashed rounded-lg p-10 text-center cursor-pointer
                        transition-all
                        ${isDragActive ? "border-blue-500 bg-blue-500/10" : "border-white/20 hover:border-blue-400/50 hover:bg-black/20"}
                      `}
                    >
                      <input {...getInputProps()} />
                      <Upload className="w-12 h-12 text-blue-400 mx-auto mb-4" />
                      <p className="text-white font-medium mb-1">Arraste e solte um arquivo aqui ou clique para selecionar</p>
                      <p className="text-sm text-blue-200">
                        Tipos suportados: {conversionTypes[activeTab as keyof typeof conversionTypes].acceptedFiles.replace(/\./g, "").toUpperCase()}
                      </p>
                    </div>
                  ) : (
                    <div className="space-y-6">
                      {/* Selected File Details */}
                      <div className="bg-black/20 rounded-lg p-4 flex items-center justify-between border border-white/10">
                        <div className="flex items-center">
                          <FileInput className="w-10 h-10 text-blue-400 mr-3" />
                          <div>
                            <p className="text-white font-medium">{selectedFile.name}</p>
                            <p className="text-sm text-blue-200">
                              {(selectedFile.size / 1024).toFixed(2)} KB • {selectedFile.type || "Arquivo"}
                            </p>
                          </div>
                        </div>
                        <Button
                          variant="outline" 
                          size="sm"
                          className="border-white/30 text-white hover:bg-white/10"
                          onClick={handleReset}
                        >
                          Alterar
                        </Button>
                      </div>
                      
                      {/* Conversion Options */}
                      <div>
                        <Label className="text-white block mb-3">Formato de Saída</Label>
                        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                          {conversionTypes[activeTab as keyof typeof conversionTypes].formats.map(format => (
                            <Button
                              key={format}
                              variant={selectedFormat === format ? "default" : "outline"}
                              className={`
                                ${selectedFormat === format 
                                  ? "bg-gradient-to-r from-blue-600 to-purple-600" 
                                  : "border-white/30 text-white hover:bg-white/10"}
                              `}
                              onClick={() => handleFormatChange(format)}
                            >
                              {format.toUpperCase()}
                            </Button>
                          ))}
                        </div>
                      </div>
                      
                      {/* Convert Button */}
                      <div className="flex justify-center">
                        <Button
                          className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 px-6 py-6 text-lg"
                          disabled={loading || !selectedFormat}
                          onClick={handleConvert}
                        >
                          {loading ? (
                            <>
                              <RefreshCcw className="w-5 h-5 mr-2 animate-spin" />
                              Convertendo...
                            </>
                          ) : (
                            <>
                              <ArrowRight className="w-5 h-5 mr-2" />
                              Converter para {selectedFormat.toUpperCase()}
                            </>
                          )}
                        </Button>
                      </div>
                    </div>
                  )}
                  
                  {/* Error Message */}
                  {error && (
                    <div className="bg-red-500/20 border border-red-500/30 text-red-300 p-3 rounded-md">
                      {error}
                    </div>
                  )}
                  
                  {/* Conversion Result */}
                  {convertedFile && (
                    <div className="mt-8 space-y-4">
                      <div className="bg-green-500/10 border border-green-500/20 rounded-lg p-4 text-center">
                        <FilePlus2 className="w-12 h-12 text-green-400 mx-auto mb-2" />
                        <p className="text-white font-medium">Conversão Concluída!</p>
                        <p className="text-sm text-blue-200 mb-4">Seu arquivo foi convertido com sucesso</p>
                        <Button
                          className="bg-gradient-to-r from-green-600 to-teal-600 hover:from-green-700 hover:to-teal-700"
                          onClick={handleDownload}
                        >
                          <Download className="w-4 h-4 mr-2" />
                          Baixar Arquivo Convertido
                        </Button>
                      </div>
                      
                      <div className="text-center">
                        <Button
                          variant="outline"
                          className="border-white/30 text-white hover:bg-white/10"
                          onClick={handleReset}
                        >
                          <RefreshCcw className="w-4 h-4 mr-2" />
                          Converter Outro Arquivo
                        </Button>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>
          ))}
        </Tabs>
        
        {/* Additional Tools */}
        <div className="mt-10">
          <h2 className="text-xl font-bold text-white mb-4 text-center">Outras Ferramentas</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card className="bg-black/40 backdrop-blur-md border-white/20">
              <CardContent className="pt-6">
                <div className="text-center">
                  <FileOutput className="w-10 h-10 text-cyan-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-white">Compressor de Arquivos</h3>
                  <p className="text-sm text-blue-200 mb-4">Reduza o tamanho dos seus arquivos sem perder qualidade</p>
                  <Button variant="outline" className="border-white/30 text-white hover:bg-white/10">
                    Em Breve
                  </Button>
                </div>
              </CardContent>
            </Card>
            <Card className="bg-black/40 backdrop-blur-md border-white/20">
              <CardContent className="pt-6">
                <div className="text-center">
                  <Image className="w-10 h-10 text-pink-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-white">Editor de Imagens</h3>
                  <p className="text-sm text-blue-200 mb-4">Edite suas imagens diretamente no navegador</p>
                  <Button variant="outline" className="border-white/30 text-white hover:bg-white/10">
                    Em Breve
                  </Button>
                </div>
              </CardContent>
            </Card>
            <Card className="bg-black/40 backdrop-blur-md border-white/20">
              <CardContent className="pt-6">
                <div className="text-center">
                  <FileText className="w-10 h-10 text-yellow-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-white">OCR - Texto em Imagens</h3>
                  <p className="text-sm text-blue-200 mb-4">Extraia texto de imagens e documentos escaneados</p>
                  <Button variant="outline" className="border-white/30 text-white hover:bg-white/10">
                    Em Breve
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FileConverter;
