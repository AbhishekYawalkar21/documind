import React, { useState, useRef } from 'react';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

interface UploadResponse {
  id: string;
  filename: string;
  file_size_bytes: number;
  status: string;
  created_at: string;
}

export const DocumentUpload: React.FC<{
  onUploadSuccess: (doc: UploadResponse) => void;
}> = ({ onUploadSuccess }) => {
  const [dragging, setDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragEnter = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragging(false);

    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFileSelect(files[0]);
    }
  };

  const handleFileSelect = async (file: File) => {
    if (!file.name.endsWith('.pdf')) {
      setError('Only PDF files allowed');
      return;
    }

    if (file.size > 50 * 1024 * 1024) {
      setError('File size must be < 50MB');
      return;
    }

    setError(null);
    setUploading(true);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await axios.post(
        `${API_URL}/documents/upload`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );

      onUploadSuccess(response.data);
    } catch (err: any) {
      setError(
        err.response?.data?.detail ||
        'Upload failed. Try again.'
      );
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto">
      <div
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`border-2 border-dashed rounded-lg p-12 text-center transition cursor-pointer ${
          dragging
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-300 bg-gray-50 hover:border-gray-400'
        }`}
      >
        <div className="space-y-4">
          <div className="text-4xl">📄</div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900">
              Drop your PDF here
            </h3>
            <p className="text-gray-500 mt-2">
              or click to select a file
            </p>
            <p className="text-sm text-gray-400 mt-1">
              Max file size: 50MB
            </p>
          </div>

          <button
            onClick={() => fileInputRef.current?.click()}
            className="btn-primary"
            disabled={uploading}
          >
            {uploading ? 'Uploading...' : 'Choose File'}
          </button>

          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf"
            onChange={(e) => {
              if (e.target.files?.[0]) {
                handleFileSelect(e.target.files[0]);
              }
            }}
            className="hidden"
          />
        </div>
      </div>

      {error && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-800">❌ {error}</p>
        </div>
      )}
    </div>
  );
};