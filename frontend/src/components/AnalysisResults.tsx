import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { DocumentQA } from './DocumentQA';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

interface AnalysisData {
  summary: string;
  topics: string[];
  entities: Record<string, string[]>;
  compliance_flags: Array<{
    type: string;
    severity: string;
    description: string;
    location: string;
  }>;
  knowledge_graph: Array<{
    entity1: string;
    relation: string;
    entity2: string;
  }>;
}

export const AnalysisResults: React.FC<{
  documentId: string;
}> = ({ documentId }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [, setAnalysisId] = useState<string | null>(null);
  const [analysis, setAnalysis] = useState<AnalysisData | null>(null);
  const [processingTime, setProcessingTime] = useState<number | null>(null);
  const [activeTab, setActiveTab] = useState<
    'summary' | 'entities' | 'compliance' | 'graph'
  >('summary');

  useEffect(() => {
    const startAnalysis = async () => {
      try {
        setLoading(true);
        setError(null);

        // Step 1: Start analysis
        const startResponse = await axios.post(
          `${API_URL}/documents/${documentId}/analyze`
        );

        const newAnalysisId = startResponse.data.analysis_id;
        setAnalysisId(newAnalysisId);

        // Step 2: Poll for results
        let attempts = 0;
        const maxAttempts = 120;

        while (attempts < maxAttempts) {
          const resultsResponse = await axios.get(
            `${API_URL}/documents/${documentId}/analysis/${newAnalysisId}`
          );

          if (resultsResponse.data.status === 'completed') {
            setAnalysis(resultsResponse.data.analysis);
            setProcessingTime(
              resultsResponse.data.processing_time_seconds
            );
            setLoading(false);
            return;
          }

          if (resultsResponse.data.status === 'failed') {
            throw new Error(
              resultsResponse.data.error ||
              'Analysis failed'
            );
          }

          await new Promise((resolve) => setTimeout(resolve, 1000));
          attempts++;
        }

        throw new Error('Analysis timeout');
      } catch (err: any) {
        setError(
          err.response?.data?.detail ||
          err.message ||
          'Failed to analyze'
        );
        setLoading(false);
      }
    };

    startAnalysis();
  }, [documentId]);

  if (loading) {
    return (
      <div className="card text-center py-12">
        <div className="inline-block animate-spin mb-4">
          <div className="text-4xl">⚙️</div>
        </div>
        <h3 className="text-xl font-semibold mt-4">
          Analyzing with Ollama...
        </h3>
        <p className="text-gray-500 mt-2">
          This may take 1-2 minutes. Please wait.
        </p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card">
        <p className="text-red-800 p-4 bg-red-50 rounded">
          ❌ Error: {error}
        </p>
      </div>
    );
  }

  if (!analysis) {
    return (
      <div className="card">
        <p className="text-gray-600">No analysis data</p>
      </div>
    );
  }

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical':
        return 'bg-red-100 border-red-300 text-red-900';
      case 'high':
        return 'bg-orange-100 border-orange-300 text-orange-900';
      case 'medium':
        return 'bg-yellow-100 border-yellow-300 text-yellow-900';
      case 'low':
        return 'bg-blue-100 border-blue-300 text-blue-900';
      default:
        return 'bg-gray-100 border-gray-300 text-gray-900';
    }
  };

  return (
    <div className="space-y-6">
      {/* Metadata */}
      <div className="card bg-linear-to-r from-blue-50 to-indigo-50">
        <div className="flex justify-between items-center">
          <div>
            <h3 className="text-lg font-semibold">Analysis Complete</h3>
            <p className="text-sm text-gray-600 mt-1">
              ✅ Document analyzed successfully
            </p>
          </div>
          {processingTime && (
            <div className="text-right">
              <p className="text-2xl font-bold text-blue-600">
                {processingTime.toFixed(2)}s
              </p>
              <p className="text-sm text-gray-600">Processing time</p>
            </div>
          )}
        </div>
      </div>

      {/* Tabs */}
      <div className="card">
        <div className="flex gap-2 mb-6 border-b">
          {[
            { id: 'summary', label: '📄 Summary' },
            { id: 'entities', label: '👥 Entities' },
            { id: 'compliance', label: '⚠️ Compliance' },
            { id: 'graph', label: '🔗 Relationships' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() =>
                setActiveTab(
                  tab.id as
                  | 'summary'
                  | 'entities'
                  | 'compliance'
                  | 'graph'
                )
              }
              className={`px-4 py-2 font-medium border-b-2 transition ${activeTab === tab.id
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-600 hover:text-gray-900'
                }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Summary Tab */}
        {activeTab === 'summary' && (
          <div className="space-y-4">
            <div>
              <h4 className="font-semibold text-gray-900 mb-2">
                Summary
              </h4>
              <p className="text-gray-700 leading-relaxed">
                {analysis.summary}
              </p>
            </div>

            <div>
              <h4 className="font-semibold text-gray-900 mb-3">
                Topics
              </h4>
              <div className="flex flex-wrap gap-2">
                {analysis.topics.map((topic, idx) => (
                  <span
                    key={idx}
                    className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
                  >
                    {topic}
                  </span>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Entities Tab */}
        {activeTab === 'entities' && (
          <div className="space-y-4">
            {Object.entries(analysis.entities).map(
              ([entityType, values]) => {
                if (!values || values.length === 0) return null;

                return (
                  <div key={entityType}>
                    <h4 className="font-semibold text-gray-900 mb-2 capitalize">
                      {entityType.replace(/_/g, ' ')}
                    </h4>
                    <div className="space-y-1">
                      {values.map((value, idx) => (
                        <div
                          key={idx}
                          className="px-3 py-2 bg-gray-50 border border-gray-200 rounded text-sm text-gray-700"
                        >
                          {value}
                        </div>
                      ))}
                    </div>
                  </div>
                );
              }
            )}
          </div>
        )}

        {/* Compliance Tab */}
        {activeTab === 'compliance' && (
          <div className="space-y-3">
            {analysis.compliance_flags.length === 0 ? (
              <div className="p-4 bg-green-50 border border-green-200 rounded-lg text-center">
                <p className="text-green-800">✅ No compliance issues</p>
              </div>
            ) : (
              analysis.compliance_flags.map((flag, idx) => (
                <div
                  key={idx}
                  className={`p-4 border rounded-lg ${getSeverityColor(
                    flag.severity
                  )}`}
                >
                  <div className="flex justify-between items-start gap-4">
                    <div>
                      <h5 className="font-semibold">
                        {flag.type}
                      </h5>
                      <p className="text-sm mt-1">
                        {flag.description}
                      </p>
                      {flag.location && (
                        <p className="text-xs opacity-75 mt-2">
                          📍 {flag.location}
                        </p>
                      )}
                    </div>
                    <span
                      className={`px-2 py-1 rounded text-xs font-semibold ${flag.severity === 'critical'
                        ? 'bg-red-200'
                        : flag.severity === 'high'
                          ? 'bg-orange-200'
                          : flag.severity === 'medium'
                            ? 'bg-yellow-200'
                            : 'bg-blue-200'
                        }`}
                    >
                      {flag.severity.toUpperCase()}
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {/* Graph Tab */}
        {activeTab === 'graph' && (
          <div className="space-y-3">
            {analysis.knowledge_graph.length === 0 ? (
              <div className="text-center py-6 text-gray-500">
                <p>No relationships found</p>
              </div>
            ) : (
              analysis.knowledge_graph.map((rel, idx) => (
                <div
                  key={idx}
                  className="p-3 bg-gray-50 border border-gray-200 rounded flex items-center gap-3"
                >
                  <div className="flex-1 text-right font-semibold text-gray-700">
                    {rel.entity1}
                  </div>
                  <div className="px-3 py-1 bg-blue-100 text-blue-800 rounded text-sm font-medium">
                    {rel.relation}
                  </div>
                  <div className="flex-1 font-semibold text-gray-700">
                    {rel.entity2}
                  </div>
                </div>
              ))
            )}
          </div>
        )}
      </div>
      {/* Q&A Section */}
      <DocumentQA documentId={documentId} />
    </div>
  );
};