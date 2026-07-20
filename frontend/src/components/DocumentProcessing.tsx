import React, { useState } from 'react';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export const DocumentProcessing: React.FC<{
  documentId: string;
  onProcessingComplete: () => void;
}> = ({ documentId, onProcessingComplete }) => {
  const [processing, setProcessing] = useState(false);
  const [processStatus, setProcessStatus] = useState<string>('');
  const [error, setError] = useState<string | null>(null);

  const handleProcess = async () => {
    setProcessing(true);
    setError(null);

    try {
      setProcessStatus('Extracting text from PDF...');

      const response = await axios.post(
        `${API_URL}/documents/${documentId}/process`
      );

      setProcessStatus(
        `✅ Successfully created ${response.data.chunks_created} chunks`
      );

      setTimeout(() => {
        onProcessingComplete();
      }, 1000);
    } catch (err: any) {
      setError(
        err.response?.data?.detail ||
        'Processing failed. Try again.'
      );
      setProcessStatus('');
    } finally {
      setProcessing(false);
    }
  };

  return (
    <div className="card space-y-4">
      <h3 className="text-lg font-semibold">Step 2: Process Document</h3>
      <p className="text-gray-600">
        Extract text from PDF and split into chunks
      </p>

      <button
        onClick={handleProcess}
        disabled={processing}
        className="btn-primary w-full"
      >
        {processing ? 'Processing...' : 'Process PDF'}
      </button>

      {processStatus && (
        <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <p className="text-blue-800">{processStatus}</p>
        </div>
      )}

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-800">❌ {error}</p>
        </div>
      )}
    </div>
  );
};