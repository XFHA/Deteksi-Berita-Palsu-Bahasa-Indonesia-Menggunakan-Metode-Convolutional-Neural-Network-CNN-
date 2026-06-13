import React, { useState, useEffect } from 'react';
import { AlertCircle, CheckCircle, Search, BarChart3, Upload, Trash2, Shield, AlertTriangle, FileText, Clock, Award, Link as LinkIcon, Database, Loader } from 'lucide-react';

interface AnalysisHistory {
  id: number;
  text: string;
  result: 'fake' | 'real';
  confidence: number;
  timestamp: string;
  source: 'text' | 'url';
  url?: string;
}

interface PreprocessingSubstep {
  step: number;
  name: string;
  description: string;
  before?: string;
  after?: string;
  changes_count?: number;
  removed_count?: number;
  replaced_count?: number;
  examples?: string[];
}

interface AnalysisStepDetails {
  substeps?: PreprocessingSubstep[];
  keywords_found?: string[];
}

interface AnalysisStep {
  step: string;
  status: 'in_progress' | 'completed';
  message: string;
  details?: AnalysisStepDetails;
  method?: string;
}

interface AnalysisResult {
  isFake: boolean;
  confidence: number;
  fakeScore: number;
  realScore: number;
  wordCount: number;
  processed?: string;
  source?: string;
  analysisSteps?: AnalysisStep[];
  sourceInfo?: {
    url?: string;
    title?: string;
    authors?: string[];
    publish_date?: string;
  };
}

interface Dataset {
  filename: string;
  size: number;
  upload_date: string;
  original_filename: string;
}

const FakeNewsDetector: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'text' | 'url' | 'manage'>('text');
  const [manageSubTab, setManageSubTab] = useState<'dataset' | 'slang' | 'models' | 'examples'>('dataset');
  const [text, setText] = useState<string>('');
  const [url, setUrl] = useState<string>('');
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [analysisHistory, setAnalysisHistory] = useState<AnalysisHistory[]>([]);
  const [stats, setStats] = useState({ totalAnalysis: 0, fakeCount: 0, realCount: 0 });
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [uploading, setUploading] = useState<boolean>(false);
  const [training, setTraining] = useState<boolean>(false);
  const [exampleNews, setExampleNews] = useState<Array<{text: string, label: string, source: string}>>([]);
  const [expandedSteps, setExpandedSteps] = useState<{[key: string]: boolean}>({});
  const [portalUrls, setPortalUrls] = useState<string>('');
  const [maxArticles, setMaxArticles] = useState<number>(10);
  const [scraping, setScraping] = useState<boolean>(false);

  useEffect(() => {
    loadDatasets();
    loadExamples();
  }, []);

  const loadDatasets = async () => {
    try {
      const response = await fetch('http://127.0.0.1:5000/datasets');
      if (response.ok) {
        const data = await response.json();
        setDatasets(data.datasets || []);
      }
    } catch (error) {
      console.error('Error loading datasets:', error);
    }
  };

  const loadExamples = async () => {
    try {
      const response = await fetch('http://127.0.0.1:5000/examples');
      if (response.ok) {
        const data = await response.json();
        console.log('Loaded examples:', data.examples);
        setExampleNews(data.examples || []);
      } else {
        console.error('Failed to load examples:', response.status);
      }
    } catch (error) {
      console.error('Error loading examples:', error);
    }
  };

  const handleAnalyzeText = async () => {
    if (!text.trim()) {
      alert('Masukkan teks berita terlebih dahulu');
      return;
    }

    setLoading(true);
    setResult(null);

    try {
      const response = await fetch('http://127.0.0.1:5000/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text }),
      });

      if (!response.ok) throw new Error('Gagal koneksi ke server');

      const data = await response.json();

      const resultData = {
        isFake: data.prediction === 'fake',
        confidence: data.confidence * 100,
        fakeScore: data.fake_score || 0,
        realScore: data.real_score || 100 - (data.fake_score || 0),
        wordCount: data.word_count || text.split(' ').length,
        processed: data.processed_text,
        source: 'manual_text_input',
        analysisSteps: data.analysis_steps || [],
      };
      
      setResult(resultData);
      updateStats(resultData);
      addToHistory(text, resultData, 'text');
    } catch (error) {
      alert('Error: Pastikan backend Python (Flask) sedang berjalan di port 5000');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyzeUrl = async () => {
    if (!url.trim()) {
      alert('Masukkan URL terlebih dahulu');
      return;
    }

    setLoading(true);
    setResult(null);

    try {
      const response = await fetch('http://127.0.0.1:5000/analyze-url', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Gagal scraping URL');
      }

      const data = await response.json();

      const resultData = {
        isFake: data.prediction === 'fake',
        confidence: data.confidence * 100,
        fakeScore: data.fake_score || 0,
        realScore: data.real_score || 100 - (data.fake_score || 0),
        wordCount: data.word_count || 0,
        processed: data.processed_text,
        source: 'url_scraping',
        sourceInfo: data.source_info,
        analysisSteps: data.analysis_steps || [],
      };
      
      setResult(resultData);
      updateStats(resultData);
      addToHistory(data.source_info?.title || url, resultData, 'url', url);
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      alert(`Error: ${errorMessage}`);
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyze = () => {
    if (activeTab === 'text') {
      handleAnalyzeText();
    } else if (activeTab === 'url') {
      handleAnalyzeUrl();
    }
  };

  const updateStats = (resultData: AnalysisResult) => {
    setStats(prev => ({
      totalAnalysis: prev.totalAnalysis + 1,
      fakeCount: prev.fakeCount + (resultData.isFake ? 1 : 0),
      realCount: prev.realCount + (resultData.isFake ? 0 : 1)
    }));
  };

  const addToHistory = (content: string, resultData: AnalysisResult, source: 'text' | 'url', itemUrl?: string) => {
    setAnalysisHistory(prev => [{
      id: Date.now(),
      text: content.substring(0, 80) + (content.length > 80 ? '...' : ''),
      result: resultData.isFake ? 'fake' : 'real',
      confidence: resultData.confidence,
      timestamp: new Date().toLocaleTimeString('id-ID'),
      source,
      url: itemUrl,
    }, ...prev.slice(0, 9)]);
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const allowedExtensions = ['.csv', '.txt', '.json'];
    const fileExtension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
    
    if (!allowedExtensions.includes(fileExtension)) {
      alert('Format file tidak didukung. Gunakan CSV, TXT, atau JSON');
      return;
    }

    setUploading(true);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('http://127.0.0.1:5000/upload-dataset', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Gagal upload dataset');
      }

      const data = await response.json();
      alert(`Dataset berhasil diupload: ${data.filename}`);
      loadDatasets();
      
      // Reset file input
      event.target.value = '';
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      alert(`Error: ${errorMessage}`);
      console.error(error);
    } finally {
      setUploading(false);
    }
  };

  const handleDeleteDataset = async (filename: string) => {
    if (!confirm(`Hapus dataset "${filename}"?`)) return;

    try {
      const response = await fetch(`http://127.0.0.1:5000/delete-dataset/${encodeURIComponent(filename)}`, {
        method: 'DELETE',
      });

      if (!response.ok) throw new Error('Gagal menghapus dataset');

      alert('Dataset berhasil dihapus');
      loadDatasets();
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      alert(`Error: ${errorMessage}`);
      console.error(error);
    }
  };

  const handleTrainModel = async (datasetFilename: string) => {
    if (!confirm(`Latih model dengan dataset "${datasetFilename}"?\n\nProses ini membutuhkan waktu beberapa menit.`)) return;

    setTraining(true);

    try {
      const response = await fetch('http://127.0.0.1:5000/train', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ dataset_filename: datasetFilename }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Gagal memulai training');
      }

      const data = await response.json();
      alert(`✓ ${data.message}\n\nDataset: ${data.dataset}\n\n${data.note}`);
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      alert(`Error: ${errorMessage}`);
      console.error(error);
    } finally {
      setTraining(false);
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  const handleScrapePortal = async () => {
    if (!portalUrls.trim()) {
      alert('Masukkan minimal 1 URL portal berita');
      return;
    }

    const urls = portalUrls.split('\n').map(u => u.trim()).filter(u => u);
    
    if (urls.length === 0) {
      alert('URL portal tidak valid');
      return;
    }

    setScraping(true);

    try {
      const response = await fetch('http://127.0.0.1:5000/scrape-portal', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          portal_urls: urls,
          max_articles: maxArticles
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Gagal scraping portal');
      }

      const data = await response.json();
      alert(`✓ Scraping berhasil!\n\nTotal artikel: ${data.total_articles}\nDataset: ${data.filename}\n\nDataset tersimpan dan siap untuk di-label & training.`);
      
      // Reload datasets
      loadDatasets();
      
      // Clear form
      setPortalUrls('');
      setMaxArticles(10);
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      alert(`Error: ${errorMessage}`);
      console.error(error);
    } finally {
      setScraping(false);
    }
  };

  // Dynamic examples loaded from API + URL examples
  const textExamples = exampleNews.length > 0 
    ? exampleNews.map(ex => ({
        title: `Contoh Berita ${ex.label === 'fake' ? 'Palsu' : 'Asli'} (${ex.source})`,
        text: ex.text
      }))
    : [
        {
          title: "Contoh Berita Palsu",
          text: "VIRAL!!! HEBOH! Pemerintah akan melarang semua orang keluar rumah mulai besok! SEGERA SHARE sebelum dihapus!!!"
        },
        {
          title: "Contoh Berita Asli",
          text: "Menurut data Kementerian Kesehatan, tingkat vaksinasi COVID-19 di Indonesia telah mencapai 70% dari target populasi berdasarkan laporan resmi yang dirilis hari ini."
        }
      ];
  
  const urlExamples = [
    {
      title: "Contoh URL Berita",
      url: "https://www.detik.com/tag/berita-terkini"
    }
  ];

  return (
    <div className="min-h-screen bg-linear-to-br from-slate-950 via-indigo-950 to-slate-900 p-4 md:p-6">
      <div className="max-w-7xl mx-auto">
        
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-5xl font-bold bg-linear-to-r from-blue-600 via-purple-600 to-indigo-600 bg-clip-text text-transparent mb-3">
            Fake News Detector
          </h1>
          <p className="text-slate-400 text-lg">Deteksi Berita Palsu dengan AI - Text, URL & Dataset</p>
        </div>

        {/* Statistics Bar */}
        <div className="grid grid-cols-3 gap-3 mb-6">
          <div className="bg-linear-to-br from-blue-500 to-blue-600 rounded-xl shadow-lg p-4 text-white transform hover:scale-105 transition-all">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm opacity-90">Total Analisis</p>
                <p className="text-3xl font-bold">{stats.totalAnalysis}</p>
              </div>
              <FileText className="w-10 h-10 opacity-80" />
            </div>
          </div>
          
          <div className="bg-linear-to-br from-red-500 to-red-600 rounded-xl shadow-lg p-4 text-white transform hover:scale-105 transition-all">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm opacity-90">Berita Palsu</p>
                <p className="text-3xl font-bold">{stats.fakeCount}</p>
              </div>
              <AlertTriangle className="w-10 h-10 opacity-80" />
            </div>
          </div>
          
          <div className="bg-linear-to-br from-green-500 to-green-600 rounded-xl shadow-lg p-4 text-white transform hover:scale-105 transition-all">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm opacity-90">Berita Asli</p>
                <p className="text-3xl font-bold">{stats.realCount}</p>
              </div>
              <Shield className="w-10 h-10 opacity-80" />
            </div>
          </div>
        </div>

        {/* Main Card */}
        <div className="bg-slate-900/80 backdrop-blur-xl border border-slate-700/50 rounded-2xl shadow-2xl p-6 mb-6">
          
          {/* Tabs */}
          <div className="flex space-x-2 mb-6 border-b pb-2">
            <button
              onClick={() => setActiveTab('text')}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all ${
                activeTab === 'text'
                  ? 'bg-blue-900/300 text-white shadow-md'
                  : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
              }`}
            >
              <FileText className="w-5 h-5" />
              <span>Analisis Teks</span>
            </button>
            
            <button
              onClick={() => setActiveTab('url')}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all ${
                activeTab === 'url'
                  ? 'bg-blue-900/300 text-white shadow-md'
                  : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
              }`}
            >
              <LinkIcon className="w-5 h-5" />
              <span>Analisis URL</span>
            </button>
            
            <button
              onClick={() => setActiveTab('manage')}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all ${
                activeTab === 'manage'
                  ? 'bg-blue-900/300 text-white shadow-md'
                  : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
              }`}
            >
              <Database className="w-5 h-5" />
              <span>Kelola Data</span>
            </button>
          </div>

          {/* Text Analysis Tab */}
          {activeTab === 'text' && (
            <div>
              <textarea
                className="w-full border-2 border-slate-600 rounded-xl p-4 min-h-50 focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none text-slate-200"
                placeholder="Masukkan teks berita yang ingin dianalisis di sini..."
                value={text}
                onChange={(e) => setText(e.target.value)}
              />
              
              <div className="mt-4">
                <h3 className="text-sm font-semibold text-slate-200 mb-2">Contoh:</h3>
                <div className="grid md:grid-cols-2 gap-3">
                  {textExamples.map((example, index) => (
                    <button
                      key={index}
                      onClick={() => setText(example.text || '')}
                      className="text-left p-3 bg-slate-800/50 rounded-lg hover:bg-slate-800 transition-colors border border-slate-700"
                    >
                      <p className="text-xs font-semibold text-blue-600 mb-1">{example.title}</p>
                      <p className="text-xs text-slate-400 line-clamp-2">{example.text}</p>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* URL Analysis Tab */}
          {activeTab === 'url' && (
            <div>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-semibold text-slate-200 mb-2">
                    URL Berita
                  </label>
                  <input
                    type="url"
                    className="w-full border-2 border-slate-600 rounded-xl p-4 focus:ring-2 focus:ring-blue-500 focus:border-transparent text-slate-200"
                    placeholder="https://example.com/berita..."
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                  />
                </div>
                
                <div className="bg-blue-900/30 border border-blue-800/50 rounded-lg p-4">
                  <p className="text-sm text-blue-300">
                    <strong>Info:</strong> Sistem akan otomatis scraping konten dari URL dan menganalisisnya.
                    Pastikan URL mengarah ke halaman berita yang valid.
                  </p>
                </div>

                <div>
                  <h3 className="text-sm font-semibold text-slate-200 mb-2">Contoh URL:</h3>
                  <div className="space-y-2">
                    {urlExamples.map((example, index) => (
                      <button
                        key={index}
                        onClick={() => setUrl(example.url || '')}
                        className="w-full text-left p-3 bg-slate-800/50 rounded-lg hover:bg-slate-800 transition-colors border border-slate-700"
                      >
                        <p className="text-xs font-semibold text-blue-600 mb-1">{example.title}</p>
                        <p className="text-xs text-slate-400 truncate">{example.url}</p>
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Management Tab with Sub-tabs */}
          {activeTab === 'manage' && (
            <div>
              {/* Sub-tabs */}
              <div className="flex space-x-2 mb-6 border-b pb-2 overflow-x-auto">
                <button
                  onClick={() => setManageSubTab('dataset')}
                  className={`px-3 py-1.5 rounded text-sm transition-all whitespace-nowrap ${
                    manageSubTab === 'dataset'
                      ? 'bg-purple-900/300 text-white'
                      : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
                  }`}
                >
                  📊 Dataset Training
                </button>
                <button
                  onClick={() => setManageSubTab('slang')}
                  className={`px-3 py-1.5 rounded text-sm transition-all whitespace-nowrap ${
                    manageSubTab === 'slang'
                      ? 'bg-purple-900/300 text-white'
                      : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
                  }`}
                >
                  📝 Slang Dictionary
                </button>
                <button
                  onClick={() => setManageSubTab('models')}
                  className={`px-3 py-1.5 rounded text-sm transition-all whitespace-nowrap ${
                    manageSubTab === 'models'
                      ? 'bg-purple-900/300 text-white'
                      : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
                  }`}
                >
                  🤖 Models CNN
                </button>
                <button
                  onClick={() => setManageSubTab('examples')}
                  className={`px-3 py-1.5 rounded text-sm transition-all whitespace-nowrap ${
                    manageSubTab === 'examples'
                      ? 'bg-purple-900/300 text-white'
                      : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
                  }`}
                >
                  📰 Contoh Berita
                </button>
              </div>

              {/* Dataset Management Sub-tab */}
              {manageSubTab === 'dataset' && (
            <div>
              {/* Scrape from Portal */}
              <div className="mb-6 bg-gradient-to-r from-blue-50 to-purple-50 border-2 border-blue-700/50 rounded-xl p-6">
                <h3 className="text-lg font-bold text-slate-100 mb-3 flex items-center space-x-2">
                  <span>🌐</span>
                  <span>Scrape Dataset dari Portal Berita</span>
                </h3>
                <p className="text-sm text-slate-400 mb-4">
                  Scrape banyak artikel dari 1 atau lebih portal berita untuk dijadikan dataset training
                </p>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-semibold text-slate-200 mb-2">
                      URL Portal Berita (1 URL per baris)
                    </label>
                    <textarea
                      className="w-full border-2 border-slate-600 rounded-lg p-3 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                      placeholder="https://www.detik.com&#10;https://www.kompas.com&#10;https://www.tribunnews.com"
                      rows={4}
                      value={portalUrls}
                      onChange={(e) => setPortalUrls(e.target.value)}
                      disabled={scraping}
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-semibold text-slate-200 mb-2">
                      Maksimal Artikel per Portal
                    </label>
                    <input
                      type="number"
                      className="w-full border-2 border-slate-600 rounded-lg p-3 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      min="5"
                      max="100"
                      value={maxArticles}
                      onChange={(e) => setMaxArticles(parseInt(e.target.value))}
                      disabled={scraping}
                    />
                  </div>
                  
                  <button
                    onClick={handleScrapePortal}
                    disabled={scraping}
                    className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 px-6 rounded-lg font-semibold hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center space-x-2"
                  >
                    {scraping ? (
                      <>
                        <Loader className="w-5 h-5 animate-spin" />
                        <span>Scraping artikel...</span>
                      </>
                    ) : (
                      <>
                        <span>🌐</span>
                        <span>Mulai Scraping</span>
                      </>
                    )}
                  </button>
                </div>
              </div>

              {/* OR Divider */}
              <div className="relative mb-6">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-slate-600"></div>
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="px-4 bg-slate-900 text-slate-400 font-semibold">ATAU</span>
                </div>
              </div>

              {/* Upload Manual */}
              <div className="mb-6">
                <label className="flex items-center justify-center w-full border-2 border-dashed border-slate-600 rounded-xl p-8 cursor-pointer hover:bg-slate-800/50 transition-colors">
                  <div className="text-center">
                    {uploading ? (
                      <Loader className="w-12 h-12 mx-auto mb-3 text-blue-500 animate-spin" />
                    ) : (
                      <Upload className="w-12 h-12 mx-auto mb-3 text-gray-400" />
                    )}
                    <p className="text-sm font-semibold text-slate-200">
                      {uploading ? 'Mengupload...' : 'Click untuk upload dataset manual'}
                    </p>
                    <p className="text-xs text-slate-400 mt-1">
                      Format: CSV, TXT, JSON (Max 50MB)
                    </p>
                  </div>
                  <input
                    type="file"
                    className="hidden"
                    accept=".csv,.txt,.json"
                    onChange={handleFileUpload}
                    disabled={uploading}
                  />
                </label>
              </div>

              <div className="bg-yellow-900/30 border border-yellow-800/50 rounded-lg p-4 mb-6">
                <p className="text-sm text-yellow-300">
                  <strong>Format Dataset:</strong><br />
                  • CSV: kolom 'text' dan 'label' (0=real, 1=fake)<br />
                  • TXT: setiap baris format "teks|label"<br />
                  • JSON: array objek dengan key 'text' dan 'label'
                </p>
              </div>

              <h3 className="text-lg font-bold text-slate-100 mb-4">Dataset Tersedia ({datasets.length})</h3>
              
              {datasets.length === 0 ? (
                <div className="text-center py-12 text-slate-400">
                  <Database className="w-16 h-16 mx-auto mb-3 opacity-30" />
                  <p>Belum ada dataset. Upload dataset untuk mulai training.</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {datasets.map((dataset) => (
                    <div key={dataset.filename} className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <p className="font-semibold text-slate-100">{dataset.original_filename}</p>
                          <p className="text-sm text-slate-400 mt-1">
                            Ukuran: {formatFileSize(dataset.size)} • Upload: {new Date(dataset.upload_date).toLocaleString('id-ID')}
                          </p>
                        </div>
                        <div className="flex space-x-2">
                          <button
                            onClick={() => handleTrainModel(dataset.filename)}
                            className="p-2 bg-green-900/300 text-white rounded-lg hover:bg-green-600 transition-colors"
                            title="Train Model"
                            disabled={training}
                          >
                            <Award className="w-5 h-5" />
                          </button>
                          <button
                            onClick={() => handleDeleteDataset(dataset.filename)}
                            className="p-2 bg-red-900/300 text-white rounded-lg hover:bg-red-600 transition-colors"
                            title="Hapus Dataset"
                          >
                            <Trash2 className="w-5 h-5" />
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
              )}

              {/* Slang Dictionary Management */}
              {manageSubTab === 'slang' && (
                <div className="text-center py-12">
                  <p className="text-lg font-semibold text-slate-100 mb-2">📝 Kelola Slang Dictionary</p>
                  <p className="text-sm text-slate-400 mb-4">
                    File: backend/data/slang_dictionary.csv<br />
                    Total: 65+ kata slang
                  </p>
                  <div className="bg-blue-900/30 border border-blue-800/50 rounded-lg p-4 max-w-2xl mx-auto text-left">
                    <p className="text-sm text-blue-300">
                      <strong>📌 Petunjuk:</strong><br />
                      • Edit file <code className="bg-blue-900/50 px-1 rounded">backend/data/slang_dictionary.csv</code><br />
                      • Format: <code className="bg-blue-900/50 px-1 rounded">slang,formal</code><br />
                      • Contoh: <code className="bg-blue-900/50 px-1 rounded">gak,tidak</code><br />
                      • Restart backend setelah edit untuk apply changes
                    </p>
                  </div>
                </div>
              )}

              {/* Models Management */}
              {manageSubTab === 'models' && (
                <div className="text-center py-12">
                  <p className="text-lg font-semibold text-slate-100 mb-2">🤖 Kelola Model CNN</p>
                  <p className="text-sm text-slate-400 mb-4">
                    Model aktif: fake_news_cnn_model.h5<br />
                    Vectorizer: tfidf_vectorizer.pkl
                  </p>
                  <div className="bg-blue-900/30 border border-blue-800/50 rounded-lg p-4 max-w-2xl mx-auto text-left">
                    <p className="text-sm text-blue-300">
                      <strong>📌 Lokasi Model:</strong><br />
                      • <code className="bg-blue-900/50 px-1 rounded">backend/models/fake_news_cnn_model.h5</code><br />
                      • <code className="bg-blue-900/50 px-1 rounded">backend/models/tfidf_vectorizer.pkl</code><br />
                      • <code className="bg-blue-900/50 px-1 rounded">backend/models/training_metadata.json</code><br /><br />
                      <strong>🎯 Training Model Baru:</strong><br />
                      1. Upload dataset di tab &quot;Dataset Training&quot;<br />
                      2. Klik tombol Train Model pada dataset<br />
                      3. Model baru akan replace model lama secara otomatis
                    </p>
                  </div>
                </div>
              )}

              {/* Example News Management */}
              {manageSubTab === 'examples' && (
                <div className="text-center py-12">
                  <p className="text-lg font-semibold text-slate-100 mb-2">📰 Kelola Contoh Berita</p>
                  <p className="text-sm text-slate-400 mb-4">
                    File: backend/data/example_news.csv<br />
                    Total: {exampleNews.length} contoh berita
                  </p>
                  <div className="bg-blue-900/30 border border-blue-800/50 rounded-lg p-4 max-w-2xl mx-auto text-left mb-6">
                    <p className="text-sm text-blue-300">
                      <strong>📌 Petunjuk Edit:</strong><br />
                      • Edit file <code className="bg-blue-900/50 px-1 rounded">backend/data/example_news.csv</code><br />
                      • Kolom: <code className="bg-blue-900/50 px-1 rounded">text,label,source</code><br />
                      • Label: <code className="bg-blue-900/50 px-1 rounded">fake</code> atau <code className="bg-blue-900/50 px-1 rounded">real</code><br />
                      • Restart backend untuk melihat perubahan
                    </p>
                  </div>
                  {exampleNews.length > 0 && (
                    <div className="max-w-4xl mx-auto">
                      <h3 className="text-lg font-bold text-slate-100 mb-4 text-left">Contoh Berita Tersimpan:</h3>
                      <div className="space-y-3">
                        {exampleNews.map((news, index) => (
                          <div key={index} className="bg-slate-800/50 rounded-lg p-4 border border-slate-700 text-left">
                            <div className="flex items-start justify-between">
                              <div className="flex-1">
                                <span className={`inline-block px-2 py-1 rounded text-xs font-semibold mb-2 ${
                                  news.label === 'fake' ? 'bg-red-900/50 text-red-300' : 'bg-green-900/50 text-green-300'
                                }`}>
                                  {news.label === 'fake' ? '❌ Fake' : '✅ Real'}
                                </span>
                                <span className="ml-2 text-xs text-slate-400">({news.source})</span>
                                <p className="text-sm text-slate-200 mt-1">{news.text}</p>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {/* Analyze Button */}
          {(activeTab === 'text' || activeTab === 'url') && (
            <button
              onClick={handleAnalyze}
              disabled={loading}
              className="w-full mt-6 bg-linear-to-r from-blue-600 to-purple-600 text-white py-4 px-6 rounded-xl font-bold text-lg hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-xl transition-all transform hover:scale-[1.02] flex items-center justify-center space-x-2"
            >
              {loading ? (
                <>
                  <Loader className="w-6 h-6 animate-spin" />
                  <span>Menganalisis...</span>
                </>
              ) : (
                <>
                  <Search className="w-6 h-6" />
                  <span>Analisis Sekarang</span>
                </>
              )}
            </button>
          )}
        </div>

        {/* Result Card */}
        {result && (
          <div className={`bg-slate-900/80 backdrop-blur-xl border border-slate-700/50 rounded-2xl shadow-2xl p-6 mb-6 border-4 ${
            result.isFake ? 'border-red-500' : 'border-green-500'
          } animate-fade-in`}>
            <div className="flex items-center space-x-4 mb-6">
              {result.isFake ? (
                <div className="bg-red-900/50 p-4 rounded-full">
                  <AlertCircle className="w-12 h-12 text-red-600" />
                </div>
              ) : (
                <div className="bg-green-900/50 p-4 rounded-full">
                  <CheckCircle className="w-12 h-12 text-green-600" />
                </div>
              )}
              <div className="flex-1">
                <h2 className={`text-3xl font-bold ${result.isFake ? 'text-red-600' : 'text-green-600'}`}>
                  {result.isFake ? 'BERITA PALSU TERDETEKSI!' : 'BERITA TAMPAK KREDIBEL'}
                </h2>
                <p className="text-slate-400 mt-1">
                  Tingkat Keyakinan: <span className="font-bold">{result.confidence.toFixed(1)}%</span>
                </p>
              </div>
            </div>

            {/* Source Info */}
            {result.sourceInfo && (
              <div className="bg-blue-900/30 border border-blue-800/50 rounded-lg p-4 mb-4">
                <h3 className="text-sm font-bold text-blue-200 mb-2">Informasi Sumber:</h3>
                {result.sourceInfo.title && (
                  <p className="text-sm text-blue-300 mb-1">
                    <strong>Judul:</strong> {result.sourceInfo.title}
                  </p>
                )}
                {result.sourceInfo.url && (
                  <p className="text-sm text-blue-300 mb-1 truncate">
                    <strong>URL:</strong> <a href={result.sourceInfo.url} target="_blank" rel="noopener noreferrer" className="underline">{result.sourceInfo.url}</a>
                  </p>
                )}
                {result.sourceInfo.authors && result.sourceInfo.authors.length > 0 && (
                  <p className="text-sm text-blue-300 mb-1">
                    <strong>Penulis:</strong> {result.sourceInfo.authors.join(', ')}
                  </p>
                )}
                {result.sourceInfo.publish_date && (
                  <p className="text-sm text-blue-300">
                    <strong>Tanggal Publikasi:</strong> {result.sourceInfo.publish_date}
                  </p>
                )}
              </div>
            )}

            {/* Score Bars */}
            <div className="grid md:grid-cols-2 gap-4 mb-6">
              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-sm font-semibold text-slate-200">Skor Palsu</span>
                  <span className="text-sm font-bold text-red-600">{result.fakeScore.toFixed(1)}%</span>
                </div>
                <div className="h-3 bg-slate-700 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-linear-to-r from-red-500 to-red-600 transition-all duration-1000"
                    style={{ width: `${result.fakeScore}%` }}
                  />
                </div>
              </div>
              
              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-sm font-semibold text-slate-200">Skor Asli</span>
                  <span className="text-sm font-bold text-green-600">{result.realScore.toFixed(1)}%</span>
                </div>
                <div className="h-3 bg-slate-700 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-linear-to-r from-green-500 to-green-600 transition-all duration-1000"
                    style={{ width: `${result.realScore}%` }}
                  />
                </div>
              </div>
            </div>

            {/* Analysis Steps */}
            {/* Analysis Steps Timeline */}
            {result.analysisSteps && result.analysisSteps.length > 0 && (
              <div className="mb-6 bg-slate-900/80 backdrop-blur-xl border border-slate-700/50 rounded-2xl p-6 shadow-xl">
                <h3 className="text-xl font-bold text-slate-100 mb-6 flex items-center space-x-3">
                  <div className="bg-purple-900/50 p-2 rounded-lg">
                    <BarChart3 className="w-6 h-6 text-purple-400" />
                  </div>
                  <span>Detail Analisis Backend</span>
                </h3>
                
                <div className="relative border-l-2 border-slate-700/50 ml-4 space-y-8 pb-4">
                  {result.analysisSteps.map((step, index) => (
                    <div key={index} className="relative pl-8">
                      {/* Timeline Dot */}
                      <div className={`absolute -left-[17px] top-1 flex items-center justify-center w-8 h-8 rounded-full border-4 border-slate-900 ${
                        step.status === 'completed' ? 'bg-green-500' : 'bg-yellow-500'
                      } shadow-[0_0_15px_rgba(0,0,0,0.5)]`}>
                        {step.status === 'completed' ? (
                          <CheckCircle className="w-4 h-4 text-white" />
                        ) : (
                          <Loader className="w-4 h-4 text-white animate-spin" />
                        )}
                      </div>
                      
                      <div className="bg-slate-800/60 border border-slate-700 rounded-xl p-5 hover:bg-slate-800/80 transition-all shadow-lg">
                        <div className="mb-3">
                          <h4 className="text-lg font-bold text-slate-100 capitalize">{step.step}</h4>
                          <p className="text-slate-400 text-sm mt-1">{step.message}</p>
                        </div>
                        
                        {/* Details */}
                        {step.details && (
                          <div className="mt-4 pt-4 border-t border-slate-700/50 space-y-4">
                            
                            {/* Preprocessing Substeps */}
                            {step.details.substeps && (
                              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                                {step.details.substeps.map((substep: PreprocessingSubstep, subIndex: number) => (
                                  <div key={subIndex} className="bg-slate-900/80 rounded-lg p-4 border border-slate-700/50 hover:border-purple-500/30 transition-colors">
                                    <div className="flex items-start justify-between mb-2">
                                      <p className="text-sm font-bold text-purple-300">
                                        <span className="bg-purple-900/50 text-purple-200 px-2 py-0.5 rounded text-xs mr-2">{substep.step}</span>
                                        {substep.name}
                                      </p>
                                    </div>
                                    <p className="text-xs text-slate-400 mb-3">{substep.description}</p>
                                    
                                    <div className="flex flex-wrap gap-2 mb-3">
                                      {substep.changes_count !== undefined && (
                                        <span className="text-[10px] font-medium bg-slate-800 text-slate-300 px-2 py-1 rounded">
                                          {substep.changes_count} perubahan
                                        </span>
                                      )}
                                      {substep.removed_count !== undefined && (
                                        <span className="text-[10px] font-medium bg-red-900/30 text-red-300 px-2 py-1 rounded">
                                          {substep.removed_count} dihapus
                                        </span>
                                      )}
                                      {substep.replaced_count !== undefined && (
                                        <span className="text-[10px] font-medium bg-blue-900/30 text-blue-300 px-2 py-1 rounded">
                                          {substep.replaced_count} diganti
                                        </span>
                                      )}
                                    </div>
                                    
                                    {substep.before && substep.after && (
                                      <div className="grid grid-cols-1 gap-2 mt-2 bg-slate-950 rounded-md p-2 border border-slate-800">
                                        <div className="flex items-start space-x-2">
                                          <span className="text-[10px] font-bold text-red-400 mt-0.5 w-12 shrink-0">Before:</span>
                                          <span className="text-xs text-slate-500 truncate">{substep.before}</span>
                                        </div>
                                        <div className="flex items-start space-x-2">
                                          <span className="text-[10px] font-bold text-green-400 mt-0.5 w-12 shrink-0">After:</span>
                                          <span className="text-xs text-slate-300 truncate">{substep.after}</span>
                                        </div>
                                      </div>
                                    )}
                                  </div>
                                ))}
                              </div>
                            )}
                            
                            {/* Indicator Analysis Details */}
                            {step.details.keywords_found !== undefined && (
                              <div className="bg-slate-900/80 rounded-lg p-4 border border-slate-700/50">
                                <p className="text-sm font-bold text-red-400 mb-3 flex items-center space-x-2">
                                  <AlertTriangle className="w-4 h-4" />
                                  <span>Kata Kunci Hoax Terdeteksi ({step.details.keywords_found.length})</span>
                                </p>
                                {step.details.keywords_found.length > 0 ? (
                                  <div className="flex flex-wrap gap-2">
                                    {step.details.keywords_found.map((keyword: string, kwIndex: number) => (
                                      <span key={kwIndex} className="px-3 py-1 bg-red-500/10 border border-red-500/20 text-red-400 text-xs font-medium rounded-full shadow-sm">
                                        {keyword}
                                      </span>
                                    ))}
                                  </div>
                                ) : (
                                  <p className="text-xs text-green-400 font-medium bg-green-500/10 p-2 rounded inline-block">Tidak ada kata kunci hoax yang ditemukan. ✓</p>
                                )}
                              </div>
                            )}
                          </div>
                        )}
                        
                        {/* Prediction Method */}
                        {step.method && (
                          <div className="mt-3 inline-flex items-center space-x-2 bg-blue-900/30 border border-blue-800/50 px-3 py-1.5 rounded-lg">
                            <Database className="w-4 h-4 text-blue-400" />
                            <span className="text-xs font-semibold text-blue-300">
                              Metode: {step.method === 'cnn' ? 'CNN (Convolutional Neural Network)' : step.method === 'rule_based' ? 'Rule-Based Detection' : step.method}
                            </span>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="bg-slate-800/50 rounded-xl p-4">
              <p className="text-sm text-slate-400">
                <strong>Jumlah Kata:</strong> {result.wordCount} kata
              </p>
              {result.source && (
                <p className="text-sm text-slate-400 mt-1">
                  <strong>Sumber Analisis:</strong> {result.source === 'url_scraping' ? 'URL Scraping' : 'Input Manual'}
                </p>
              )}
            </div>
          </div>
        )}

        {/* History */}
        {analysisHistory.length > 0 && (
          <div className="bg-slate-900/80 backdrop-blur-xl border border-slate-700/50 rounded-2xl shadow-2xl p-6">
            <div className="flex items-center space-x-2 mb-4">
              <Clock className="w-6 h-6 text-purple-600" />
              <h2 className="text-2xl font-bold text-slate-100">Riwayat Analisis</h2>
            </div>
            
            <div className="space-y-3">
              {analysisHistory.map((item) => (
                <div key={item.id} className="flex items-center justify-between p-4 bg-slate-800/50 rounded-lg hover:bg-slate-800 transition-colors">
                  <div className="flex items-center space-x-4 flex-1">
                    {item.result === 'fake' ? (
                      <AlertCircle className="w-8 h-8 text-red-500 shrink-0" />
                    ) : (
                      <CheckCircle className="w-8 h-8 text-green-500 shrink-0" />
                    )}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-2 mb-1">
                        {item.source === 'url' ? (
                          <LinkIcon className="w-4 h-4 text-blue-500" />
                        ) : (
                          <FileText className="w-4 h-4 text-slate-400" />
                        )}
                        <p className="text-sm font-semibold text-slate-100 truncate">{item.text}</p>
                      </div>
                      <p className="text-xs text-slate-400">
                        {item.result === 'fake' ? 'Palsu' : 'Asli'} • {item.confidence.toFixed(1)}% • {item.timestamp}
                        {item.url && ` • ${item.url}`}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default FakeNewsDetector;
