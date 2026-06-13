import React, { useState } from 'react';
import { Search, AlertTriangle, CheckCircle, Activity, Link as LinkIcon, Upload, Database, FileText } from 'lucide-react';

interface AnalysisStep {
  step: string;
  status: string;
  message: string;
  details: {
    before: string;
    after: string;
  } | null;
}

interface AnalysisResult {
  isFake: boolean;
  confidence: number;
  wordCount: number;
  processed: string;
  source: string;
  analysisSteps: AnalysisStep[];
}

const FakeNewsDetector: React.FC = () => {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [uploading, setUploading] = useState(false);

  const handleAnalyze = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setResult(null);

    const isUrl = query.startsWith('http');
    const endpoint = isUrl ? '/analyze-url' : '/analyze';
    const payload = isUrl ? { url: query } : { text: query };

    try {
      const response = await fetch(`http://localhost:5000${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error('Gagal menganalisis. Pastikan model sudah ditrain dan server berjalan.');
      }

      const data = await response.json();
      setResult({
        isFake: data.prediction === 'fake',
        confidence: data.confidence * 100,
        wordCount: data.word_count,
        processed: data.processed_text,
        source: data.source,
        analysisSteps: data.analysis_steps || []
      });
    } catch (error: any) {
      alert(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:5000/upload-dataset', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error('Upload gagal');
      alert('Dataset berhasil diupload!');
    } catch (error: any) {
      alert(`Error: ${error.message}`);
    } finally {
      setUploading(false);
      e.target.value = '';
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800 p-6 md:p-12 font-sans">
      <div className="max-w-4xl mx-auto space-y-10">
        
        <div className="text-center space-y-4 pt-8">
          <h1 className="text-4xl md:text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600 tracking-tight">
            CNN Fake News Detector
          </h1>
          <p className="text-gray-500 text-lg">
            Deteksi kebenaran berita berbahasa Indonesia dengan teknologi Deep Learning (Convolutional Neural Network)
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white rounded-3xl shadow-xl shadow-blue-900/5 p-8 border border-gray-100 flex flex-col h-full hover:shadow-2xl transition-shadow duration-300">
            <div className="mb-6 text-center">
              <div className="mx-auto w-16 h-16 bg-blue-50 rounded-full flex items-center justify-center mb-4">
                <LinkIcon className="w-8 h-8 text-blue-500" />
              </div>
              <h2 className="text-xl font-bold text-gray-800 mb-2">Analisis Teks / URL</h2>
            </div>
            
            <div className="flex-1 flex flex-col justify-center relative">
              <textarea
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Tempel teks atau URL di sini..."
                className="w-full bg-slate-50 rounded-2xl p-4 text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none h-32 border border-slate-200 mb-4 transition-all"
              />
              <button
                onClick={handleAnalyze}
                disabled={loading || !query.trim()}
                className="w-full bg-blue-600 text-white rounded-2xl px-6 py-4 font-bold shadow-lg shadow-blue-600/30 hover:shadow-xl hover:scale-[1.02] hover:bg-blue-700 transition-all disabled:opacity-50 flex items-center justify-center"
              >
                {loading ? <Activity className="w-5 h-5 mr-2 animate-spin" /> : <Search className="w-5 h-5 mr-2" />}
                {loading ? 'Memproses dengan CNN...' : 'Analisis Sekarang'}
              </button>
            </div>
          </div>

          <div className="bg-white rounded-3xl shadow-xl shadow-purple-900/5 p-8 border border-gray-100 flex flex-col h-full hover:shadow-2xl transition-shadow duration-300 text-center">
            <div className="mb-6">
              <div className="mx-auto w-16 h-16 bg-purple-50 rounded-full flex items-center justify-center mb-4">
                <Database className="w-8 h-8 text-purple-500" />
              </div>
              <h2 className="text-xl font-bold text-gray-800 mb-2">Upload Dataset</h2>
              <p className="text-sm text-gray-500">Unggah CSV/XLSX untuk menambahkan data training</p>
            </div>
            
            <div className="flex-1 flex flex-col justify-center space-y-4">
              <div className="relative overflow-hidden group w-full">
                <input 
                  type="file" 
                  accept=".csv,.xlsx" 
                  onChange={handleUpload}
                  disabled={uploading}
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer disabled:cursor-not-allowed z-20"
                />
                <button 
                  disabled={uploading}
                  className="w-full bg-purple-600 text-white rounded-2xl px-6 py-4 font-bold shadow-lg shadow-purple-600/30 hover:shadow-xl hover:scale-[1.02] hover:bg-purple-700 transition-all disabled:opacity-50 flex items-center justify-center"
                >
                  {uploading ? <Activity className="w-5 h-5 animate-spin mr-2" /> : <Upload className="w-5 h-5 mr-2" />}
                  {uploading ? 'Mengunggah...' : 'Upload Dataset Baru'}
                </button>
              </div>
            </div>
          </div>
        </div>

        {result && (
          <div className={`bg-white rounded-3xl shadow-2xl p-8 border-t-8 transition-all duration-500 ${result.isFake ? 'border-red-500 shadow-red-900/10' : 'border-teal-500 shadow-teal-900/10'}`}>
            <div className="flex flex-col md:flex-row items-center md:items-start gap-6">
              {result.isFake ? (
                <div className="bg-red-50 p-6 rounded-full"><AlertTriangle className="w-16 h-16 text-red-500" /></div>
              ) : (
                <div className="bg-teal-50 p-6 rounded-full"><CheckCircle className="w-16 h-16 text-teal-500" /></div>
              )}
              
              <div className="text-center md:text-left flex-1">
                <h2 className={`text-3xl md:text-4xl font-black mb-2 ${result.isFake ? 'text-red-600' : 'text-teal-600'}`}>
                  {result.isFake ? 'Terdeteksi Berita Palsu (Hoax)!' : 'Berita Tampak Valid'}
                </h2>
                <p className="text-gray-600 text-lg mb-6">
                  Model CNN kami memprediksi dengan tingkat keyakinan <strong className={result.isFake ? 'text-red-600' : 'text-teal-600'}>{result.confidence.toFixed(1)}%</strong>.
                </p>
                
                <div className="bg-gray-50 rounded-2xl p-6 border border-gray-100">
                  <h3 className="font-bold text-gray-700 mb-2 flex items-center"><FileText className="w-4 h-4 mr-2" /> Hasil Preprocessing Teks (Sastrawi)</h3>
                  <p className="text-sm text-gray-500 font-mono bg-white p-4 rounded-xl border border-gray-100 italic leading-relaxed">"{result.processed}"</p>
                  <p className="text-xs text-gray-400 mt-2 font-semibold">Total: {result.wordCount} kata diproses</p>
                </div>

                {result.analysisSteps && result.analysisSteps.length > 0 && (
                  <div className="mt-6 space-y-3">
                    <h3 className="font-bold text-gray-700 mb-4 flex items-center"><Activity className="w-5 h-5 mr-2 text-blue-500" /> Detail Langkah Pemrosesan (NLP Pipeline)</h3>
                    {result.analysisSteps.map((step, idx) => (
                      <div key={idx} className="bg-white border border-slate-200 p-4 rounded-xl shadow-sm">
                        <div className="flex justify-between items-start mb-2">
                          <span className="font-bold text-slate-800 text-sm">{step.step}</span>
                          <span className="bg-green-100 text-green-700 text-xs font-bold px-2 py-1 rounded-full">{step.status}</span>
                        </div>
                        <p className="text-sm text-slate-600 mb-3">{step.message}</p>
                        {step.details && (
                          <div className="grid grid-cols-1 gap-2 text-xs font-mono bg-slate-50 p-3 rounded-lg border border-slate-100">
                            <div><span className="text-red-500 font-bold">- Sebelum:</span> <span className="text-slate-500 break-words">{step.details.before}</span></div>
                            <div><span className="text-green-500 font-bold">+ Sesudah:</span> <span className="text-slate-700 break-words">{step.details.after}</span></div>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

      </div>
    </div>
  );
};

export default FakeNewsDetector;
