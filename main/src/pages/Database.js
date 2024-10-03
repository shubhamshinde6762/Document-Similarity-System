import React, { useState, useEffect } from 'react';
import { PlusIcon, SearchIcon, PencilIcon, TrashIcon } from 'lucide-react';

const API_URL = 'http://192.168.205.33:5000';

const Database = () => {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [category, setCategory] = useState('');
  const [queryText, setQueryText] = useState('');
  const [similarDocuments, setSimilarDocuments] = useState([]);
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [editingDocument, setEditingDocument] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    fetchCategories();
  }, []);

  const fetchCategories = async () => {
    try {
      const response = await fetch(`${API_URL}/get_categories`);
      if (response.ok) {
        const data = await response.json();
        setCategories(data);
      }
    } catch (error) {
      console.error('Error fetching categories:', error);
    }
  };

  const handleAddDocument = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`${API_URL}/add_document`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, content, category }),
      });
      if (response.ok) {
        alert('Document added successfully!');
        setTitle('');
        setContent('');
        setCategory('');
        fetchCategories();
      } else {
        alert('Error adding document');
      }
    } catch (error) {
      console.error('Error:', error);
      alert('Error adding document');
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuerySimilar = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`${API_URL}/query_similar`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: queryText, category: selectedCategory }),
      });
      if (response.ok) {
        const data = await response.json();
        setSimilarDocuments(data);
      } else {
        alert('Error querying similar documents');
      }
    } catch (error) {
      console.error('Error:', error);
      alert('Error querying similar documents');
    } finally {
      setIsLoading(false);
    }
  };

  const handleEditDocument = async (docId) => {
    setIsLoading(true);
    try {
      const response = await fetch(`${API_URL}/get_document/${docId}`);
      if (response.ok) {
        const data = await response.json();
        setEditingDocument(data);
        setTitle(data.title);
        setContent(data.content);
        setCategory(data.category);
      } else {
        alert('Error fetching document for editing');
      }
    } catch (error) {
      console.error('Error:', error);
      alert('Error fetching document for editing');
    } finally {
      setIsLoading(false);
    }
  };

  const handleUpdateDocument = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`${API_URL}/update_document/${editingDocument.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, content, category }),
      });
      if (response.ok) {
        alert('Document updated successfully!');
        setEditingDocument(null);
        setTitle('');
        setContent('');
        setCategory('');
        fetchCategories();
      } else {
        alert('Error updating document');
      }
    } catch (error) {
      console.error('Error:', error);
      alert('Error updating document');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteDocument = async (docId) => {
    if (window.confirm('Are you sure you want to delete this document?')) {
      setIsLoading(true);
      try {
        const response = await fetch(`${API_URL}/delete_document/${docId}`, {
          method: 'DELETE',
        });
        if (response.ok) {
          alert('Document deleted successfully!');
          setSimilarDocuments(similarDocuments.filter(doc => doc.id !== docId));
        } else {
          alert('Error deleting document');
        }
      } catch (error) {
        console.error('Error:', error);
        alert('Error deleting document');
      } finally {
        setIsLoading(false);
      }
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8 text-center text-indigo-600">Document Similarity System</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="bg-white shadow-md rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">{editingDocument ? 'Edit Document' : 'Add New Document'}</h2>
          <form onSubmit={(e) => { e.preventDefault(); editingDocument ? handleUpdateDocument() : handleAddDocument(); }}>
            <div className="mb-4">
              <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">Title</label>
              <input
                id="title"
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                required
              />
            </div>
            <div className="mb-4">
              <label htmlFor="content" className="block text-sm font-medium text-gray-700 mb-1">Content</label>
              <textarea
                id="content"
                value={content}
                onChange={(e) => setContent(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                rows="4"
                required
              />
            </div>
            <div className="mb-4">
              <label htmlFor="category" className="block text-sm font-medium text-gray-700 mb-1">Category</label>
              <input
                id="category"
                type="text"
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
            <button
              type="submit"
              className="w-full bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 flex items-center justify-center"
              disabled={isLoading}
            >
              {isLoading ? (
                <svg className="animate-spin h-5 w-5 mr-3" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
              ) : editingDocument ? (
                <PencilIcon className="w-5 h-5 mr-2" />
              ) : (
                <PlusIcon className="w-5 h-5 mr-2" />
              )}
              {editingDocument ? 'Update Document' : 'Add Document'}
            </button>
          </form>
        </div>

        <div className="bg-white shadow-md rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Query Similar Documents</h2>
          <form onSubmit={(e) => { e.preventDefault(); handleQuerySimilar(); }}>
            <div className="mb-4">
              <label htmlFor="queryText" className="block text-sm font-medium text-gray-700 mb-1">Query Text</label>
              <textarea
                id="queryText"
                value={queryText}
                onChange={(e) => setQueryText(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                rows="4"
                required
              />
            </div>
            <div className="mb-4">
              <label htmlFor="selectedCategory" className="block text-sm font-medium text-gray-700 mb-1">Filter by Category (optional)</label>
              <select
                id="selectedCategory"
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value="">All Categories</option>
                {categories.map((cat, index) => (
                  <option key={index} value={cat}>{cat}</option>
                ))}
              </select>
            </div>
            <button
              type="submit"
              className="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 flex items-center justify-center"
              disabled={isLoading}
            >
              {isLoading ? (
                <svg className="animate-spin h-5 w-5 mr-3" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
              ) : (
                <SearchIcon className="w-5 h-5 mr-2" />
              )}
              Find Similar Documents
            </button>
          </form>
        </div>
      </div>

      {similarDocuments.length > 0 && (
        <div className="mt-8">
          <h2 className="text-2xl font-semibold mb-4">Similar Documents</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {similarDocuments.map((doc) => (
              <div key={doc.id} className="bg-white shadow-md rounded-lg p-4">
                <h3 className="text-lg font-semibold mb-2">{doc.title}</h3>
                <p className="text-sm text-gray-600 mb-2">{doc.content}</p>
                <p className="text-xs text-gray-500 mb-2">Category: {doc.category}</p>
                <p className="text-xs text-indigo-600 mb-4">Similarity: {doc.similarity.toFixed(4)}</p>
                <div className="flex justify-end space-x-2">
                  <button
                    onClick={() => handleEditDocument(doc.id)}
                    className="bg-yellow-500 text-white py-1 px-2 rounded-md hover:bg-yellow-600 focus:outline-none focus:ring-2 focus:ring-yellow-500"
                  >
                    <PencilIcon className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => handleDeleteDocument(doc.id)}
                    className="bg-red-500 text-white py-1 px-2 rounded-md hover:bg-red-600 focus:outline-none focus:ring-2 focus:ring-red-500"
                  >
                    <TrashIcon className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default Database;