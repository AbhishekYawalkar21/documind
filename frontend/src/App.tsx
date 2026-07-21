import { useState } from 'react';
import './index.css';
import { DocumentUpload } from './components/DocumentUpload';
import { DocumentProcessing } from './components/DocumentProcessing';
import { AnalysisResults } from './components/AnalysisResults';
import { DocumentHistory } from './components/DocumentHistory';

function App() {
  const [currentDocument, setCurrentDocument] = useState<any>(null);
  const [step, setStep] = useState<
    'upload' | 'process' | 'analyze'
  >('upload');
  const [showSidebar, setShowSidebar] = useState(false);

  const handleUploadSuccess = (doc: any) => {
    setCurrentDocument(doc);
    setStep('process');
  };

  const handleProcessingComplete = () => {
    setStep('analyze');
  };

  const handleStartOver = () => {
    setCurrentDocument(null);
    setStep('upload');
  };

  const handleSelectDocument = (doc: any) => {
    setCurrentDocument(doc);
    setStep('analyze');
    setShowSidebar(false);
  };

  return (
    <div className="min-h-screen bg-linear-to-br from-blue-50 to-indigo-100 flex">
      {/* Sidebar Overlay */}
      {showSidebar && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={() => setShowSidebar(false)}
        />
      )}

      {/* Sidebar */}
      <div
        className={`fixed left-0 top-0 bottom-0 w-64 bg-white shadow-lg transform transition-transform z-50 lg:relative lg:transform-none ${showSidebar ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
          }`}
      >
        <div className="p-4 border-b">
          <button
            onClick={() => setShowSidebar(false)}
            className="lg:hidden text-gray-500 hover:text-gray-700 text-xl"
          >
            ✕
          </button>
          <h3 className="text-lg font-bold text-gray-900 mt-2">
            📚 History
          </h3>
        </div>

        <div className="p-4 overflow-y-auto max-h-[calc(100vh-80px)]">
          <DocumentHistory onSelectDocument={handleSelectDocument} />
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1">
        <div className="container">
          {/* Header */}
          <div className="mb-8 flex justify-between items-center">
            <div>
              <h1 className="text-4xl font-bold text-gray-900 mb-2">
                📄 DocuMind
              </h1>
              <p className="text-lg text-gray-600">
                AI-powered document intelligence with Ollama
              </p>
            </div>

            <button
              onClick={() => setShowSidebar(!showSidebar)}
              className="lg:hidden px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              📚 History
            </button>
          </div>

          {/* Progress Indicator */}
          {step !== 'upload' && (
            <div className="mb-8 flex justify-center gap-4">
              {[
                { step: 'upload', label: 'Upload', num: 1 },
                { step: 'process', label: 'Process', num: 2 },
                { step: 'analyze', label: 'Analyze', num: 3 },
              ].map((item, idx) => (
                <div key={item.step}>
                  <div
                    className={`flex flex-col items-center ${step === item.step ||
                        (step === 'process' && idx < 2) ||
                        step === 'analyze'
                        ? 'text-blue-600'
                        : 'text-gray-400'
                      }`}
                  >
                    <div
                      className={`w-10 h-10 rounded-full flex items-center justify-center font-bold text-white ${step === item.step ||
                          (step === 'process' && idx < 2) ||
                          step === 'analyze'
                          ? 'bg-blue-600'
                          : 'bg-gray-300'
                        }`}
                    >
                      {item.num}
                    </div>
                    <p className="text-sm mt-2">{item.label}</p>
                  </div>

                  {idx < 2 && (
                    <div className="w-12 h-1 bg-gray-300 self-start mt-5 mx-4" />
                  )}
                </div>
              ))}
            </div>
          )}

          {/* Main Content */}
          <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
            {step === 'upload' && (
              <div>
                <h2 className="text-2xl font-bold mb-6">
                  Upload PDF Document
                </h2>
                <DocumentUpload onUploadSuccess={handleUploadSuccess} />
              </div>
            )}

            {step === 'process' && currentDocument && (
              <div className="space-y-6">
                <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                  <p className="text-green-800">
                    ✅ Uploaded: {currentDocument.filename}
                  </p>
                </div>
                <DocumentProcessing
                  documentId={currentDocument.id}
                  onProcessingComplete={handleProcessingComplete}
                />
              </div>
            )}

            {step === 'analyze' && currentDocument && (
              <div className="space-y-6">
                <AnalysisResults documentId={currentDocument.id} />

                <button
                  onClick={handleStartOver}
                  className="btn-secondary w-full"
                >
                  ↻ Analyze Another Document
                </button>
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="text-center py-4 text-gray-600">
            <p>© 2026 DocuMind. All rights reserved.</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;