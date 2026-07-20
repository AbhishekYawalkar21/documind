import React, { useState } from 'react';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

interface QAItem {
  qa_id: string;
  question: string;
  answer: string;
  confidence: number;
}

export const DocumentQA: React.FC<{
  documentId: string;
}> = ({ documentId }) => {
  const [question, setQuestion] = useState('');
  const [qaHistory, setQaHistory] = useState<QAItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAskQuestion = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!question.trim()) {
      setError('Please enter a question');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await axios.post(
        `${API_URL}/documents/${documentId}/question`,
        { question }
      );

      const qaItem: QAItem = {
        qa_id: response.data.qa_id,
        question: response.data.question,
        answer: response.data.answer,
        confidence: response.data.confidence_score,
      };

      setQaHistory([qaItem, ...qaHistory]);
      setQuestion('');
    } catch (err: any) {
      setError(
        err.response?.data?.detail ||
        'Failed to get answer'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card space-y-6">
      <div>
        <h3 className="text-xl font-semibold mb-2">💬 Ask Questions</h3>
        <p className="text-gray-600">
          Ask anything about the document
        </p>
      </div>

      {/* Question Form */}
      <form onSubmit={handleAskQuestion} className="space-y-3">
        <div className="flex gap-2">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask a question..."
            disabled={loading}
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            type="submit"
            disabled={loading || !question.trim()}
            className="btn-primary"
          >
            {loading ? 'Loading...' : 'Ask'}
          </button>
        </div>

        {error && (
          <p className="text-red-600 text-sm">❌ {error}</p>
        )}
      </form>

      {/* Q&A History */}
      {qaHistory.length > 0 && (
        <div className="space-y-3 border-t pt-4">
          <h4 className="font-semibold text-gray-900">
            Questions Asked
          </h4>

          {qaHistory.map((item) => (
            <div
              key={item.qa_id}
              className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition"
            >
              <div className="flex justify-between items-start gap-4 mb-2">
                <p className="font-medium text-gray-900">
                  Q: {item.question}
                </p>
                <span
                  className={`px-2 py-1 text-xs font-semibold rounded ${
                    item.confidence > 0.8
                      ? 'bg-green-100 text-green-800'
                      : item.confidence > 0.6
                      ? 'bg-yellow-100 text-yellow-800'
                      : 'bg-orange-100 text-orange-800'
                  }`}
                >
                  {(item.confidence * 100).toFixed(0)}%
                </span>
              </div>

              <p className="text-gray-700 text-sm">
                A: {item.answer}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};