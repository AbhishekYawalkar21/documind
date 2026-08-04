import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

interface Document {
    id: string;
    filename: string;
    file_size_bytes: number;
    status: string;
    created_at: string;
}

export const DocumentHistory: React.FC<{
    onSelectDocument: (doc: Document) => void;
}> = ({ onSelectDocument }) => {
    const [documents, setDocuments] = useState<Document[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchDocuments = async () => {
            try {
                const response = await axios.get(`${API_URL}/documents?skip=0&limit=10`);
                setDocuments(response.data);
                setLoading(false);
            } catch (err: any) {
                setError('Failed to load history');
                setLoading(false);
            }
        };

        fetchDocuments();
    }, []);

    const formatDate = (dateString: string) => {
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
        });
    };

    const formatFileSize = (bytes: number) => {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
        return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    };

    if (loading) {
        return (
            <div className="card text-center py-8">
                <p className="text-gray-600">Loading...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="card p-4 bg-red-50 border border-red-200">
                <p className="text-red-800">❌ {error}</p>
            </div>
        );
    }

    if (documents.length === 0) {
        return (
            <div className="card text-center py-8">
                <p className="text-gray-600">No documents yet</p>
            </div>
        );
    }

    return (
        <div className="card">
            {/* <h3 className="text-lg font-semibold mb-4">📚 History</h3> */}

            <div className="space-y-2 max-h-130 overflow-y-auto">
                {documents.map((doc) => {
                    const normalizedStatus = doc.status.toLowerCase();
                    const displayStatus =
                        normalizedStatus.charAt(0).toUpperCase() + normalizedStatus.slice(1);

                    return (
                        <div
                            key={doc.id}
                            className="p-3 border border-gray-200 rounded-lg hover:shadow-md transition cursor-pointer"
                            onClick={() => onSelectDocument(doc)}
                        >
                            <h4
                                className="font-semibold text-gray-900 text-sm wrap-break-word"
                                title={doc.filename}
                            >
                                {doc.filename}
                            </h4>

                            <span
                                className={`inline-block mt-1 px-2 py-0.5 rounded-full text-xs font-medium ${normalizedStatus === 'processed'
                                    ? 'bg-green-100 text-green-800'
                                    : normalizedStatus === 'processing'
                                        ? 'bg-blue-100 text-blue-800'
                                        : 'bg-gray-100 text-gray-800'
                                    }`}
                            >
                                {displayStatus}
                            </span>

                            <div className="mt-1 text-xs text-gray-600 space-y-0.5">
                                <div>{formatFileSize(doc.file_size_bytes)}</div>
                                <div>{formatDate(doc.created_at)}</div>
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
};