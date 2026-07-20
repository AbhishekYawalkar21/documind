import { useState } from 'react';
import './index.css';
import { DocumentUpload } from './components/DocumentUpload';
import { DocumentProcessing } from './components/DocumentProcessing';
import { AnalysisResults } from './components/AnalysisResults';

function App() {
  const [currentDocument, setCurrentDocument] = useState<any>(null);
  const [step, setStep] = useState<'upload' | 'process' | 'analyze'>(
    'upload'
  );

  const handleUploadSuccess = (doc: any) => {
    setCurrentDocument(doc);
    setStep('process');
  };

  const handleProcessingComplete = () => {
    setStep('analyze');
  };

  return (
    <div className="min-h-screen bg-linear-to-br from-blue-50 to-indigo-100">
      <div className="container">
        {/* Header */}
        <div className="mb-12 text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            📄 DocuMind
          </h1>
          <p className="text-lg text-gray-600">
            AI-powered document intelligence
          </p>
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
        <div className="bg-white rounded-lg shadow-lg p-8">
          {step === 'upload' && (
            <div>
              <h2 className="text-2xl font-bold mb-6">Upload PDF Document</h2>
              <DocumentUpload onUploadSuccess={handleUploadSuccess} />
            </div>
          )}

          {step === 'process' && currentDocument && (
            <div className="space-y-6">
              <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                <p className="text-green-800">
                  ✅ Document uploaded: {currentDocument.filename}
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
                onClick={() => {
                  setCurrentDocument(null);
                  setStep('upload');
                }}
                className="btn-secondary w-full"
              >
                ↻ Analyze Another Document
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;