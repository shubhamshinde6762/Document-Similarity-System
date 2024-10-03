import mysql.connector
from mysql.connector import Error
from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
from sentence_transformers import SentenceTransformer, util
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string
from flask_cors import CORS

nltk.download('punkt')
nltk.download('stopwords')

app = Flask(__name__)
CORS(app)

model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

db_config = {
    'host': 'localhost',
    'user': 'shubham',
    'password': 'Sshubham@6762',
    'database': 'my_database'
}

def create_connection():
    """
    Establishes a connection to the MySQL database.
    Returns:
        mysql.connector.connection.MySQLConnection: Database connection object or None if failed.
    """
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except Error as e:
        return None

def create_tables():
    """
    Creates the 'documents' and 'keywords' tables in the database if they do not exist.
    """
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    content TEXT NOT NULL,
                    embedding BLOB NOT NULL,
                    category VARCHAR(50) DEFAULT 'Uncategorized',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS keywords (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    document_id INT NOT NULL,
                    keyword VARCHAR(100) NOT NULL,
                    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
                )
            """)
            connection.commit()
        except Error:
            connection.rollback()
        finally:
            connection.close()

create_tables()

def extract_keywords(text, top_k=5):
    """
    Extracts the top_k keywords from the given text using frequency distribution.
    
    Args:
        text (str): The input text from which to extract keywords.
        top_k (int): The number of top keywords to return.
        
    Returns:
        List[str]: A list of top_k keywords.
    """
    stop_words = set(stopwords.words('english'))
    word_tokens = word_tokenize(text.lower())
    filtered_tokens = [w for w in word_tokens if w not in stop_words and w not in string.punctuation]
    freq_dist = nltk.FreqDist(filtered_tokens)
    return [word for word, _ in freq_dist.most_common(top_k)]

def encode_embedding(embedding):
    """
    Serializes the embedding numpy array to bytes for storage in MySQL BLOB.
    
    Args:
        embedding (np.ndarray): The embedding vector.
        
    Returns:
        bytes: The serialized embedding.
    """
    return embedding.astype(np.float32).tobytes()

def decode_embedding(embedding_bytes):
    """
    Deserializes bytes back to a numpy array.
    
    Args:
        embedding_bytes (bytes): The serialized embedding.
        
    Returns:
        np.ndarray: The deserialized embedding vector.
    """
    return np.frombuffer(embedding_bytes, dtype=np.float32)

@app.route('/add_document', methods=['POST'])
def add_document():
    """
    Adds a new document to the database along with its embedding and extracted keywords.
    
    Returns:
        JSON response indicating success or error.
    """
    data = request.json
    title = data.get('title')
    content = data.get('content')
    category = data.get('category', 'Uncategorized')

    if not title or not content:
        return jsonify({"error": "Title and content are required"}), 400

    embedding = model.encode(content)
    embedding_bytes = encode_embedding(embedding)
    keywords = extract_keywords(content)

    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            doc_query = "INSERT INTO documents (title, content, embedding, category) VALUES (%s, %s, %s, %s)"
            cursor.execute(doc_query, (title, content, embedding_bytes, category))
            doc_id = cursor.lastrowid

            keyword_query = "INSERT INTO keywords (document_id, keyword) VALUES (%s, %s)"
            keyword_data = [(doc_id, keyword) for keyword in keywords]
            cursor.executemany(keyword_query, keyword_data)

            connection.commit()
            return jsonify({"message": "Document added successfully", "id": doc_id}), 201
        except Error:
            connection.rollback()
            return jsonify({"error": "Error adding document"}), 500
        finally:
            connection.close()
    else:
        return jsonify({"error": "Database connection failed"}), 500

@app.route('/query_similar', methods=['POST'])
def query_similar():
    """
    Queries for documents similar to the provided query text.
    
    Returns:
        JSON response with a list of similar documents.
    """
    data = request.json
    query_text = data.get('query')
    top_k = data.get('top_k', 5)
    category = data.get('category')

    if not query_text:
        return jsonify({"error": "Query text is required"}), 400

    query_embedding = model.encode(query_text)

    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            if category:
                cursor.execute("""
                    SELECT id, title, content, embedding, category
                    FROM documents
                    WHERE category = %s
                """, (category,))
            else:
                cursor.execute("SELECT id, title, content, embedding, category FROM documents")
            results = cursor.fetchall()

            similarities = []
            for row in results:
                id, title, content, embedding_bytes, doc_category = row
                doc_embedding = decode_embedding(embedding_bytes)
                similarity = util.cos_sim(query_embedding, doc_embedding).item()
                similarities.append((id, title, content, similarity, doc_category))

            similarities.sort(key=lambda x: x[3], reverse=True)
            top_results = similarities[:top_k]

            response = [
                {
                    "id": id,
                    "title": title,
                    "content": content[:100] + "..." if len(content) > 100 else content,
                    "similarity": similarity,
                    "category": doc_category
                }
                for id, title, content, similarity, doc_category in top_results
            ]

            return jsonify(response), 200
        except Error:
            return jsonify({"error": "Error querying similar documents"}), 500
        finally:
            connection.close()
    else:
        return jsonify({"error": "Database connection failed"}), 500

@app.route('/get_categories', methods=['GET'])
def get_categories():
    """
    Retrieves a list of distinct categories from the documents.
    
    Returns:
        JSON response with a list of categories.
    """
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT DISTINCT category FROM documents")
            categories = [row[0] for row in cursor.fetchall()]
            return jsonify(categories), 200
        except Error:
            return jsonify({"error": "Error fetching categories"}), 500
        finally:
            connection.close()
    else:
        return jsonify({"error": "Database connection failed"}), 500

@app.route('/get_document/<int:doc_id>', methods=['GET'])
def get_document(doc_id):
    """
    Retrieves a specific document by its ID along with its keywords.
    
    Args:
        doc_id (int): The ID of the document to retrieve.
        
    Returns:
        JSON response with document details or an error message.
    """
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT id, title, content, category, created_at
                FROM documents
                WHERE id = %s
            """, (doc_id,))
            document = cursor.fetchone()

            if document:
                cursor.execute("SELECT keyword FROM keywords WHERE document_id = %s", (doc_id,))
                keywords = [row['keyword'] for row in cursor.fetchall()]
                document['keywords'] = keywords
                return jsonify(document), 200
            else:
                return jsonify({"error": "Document not found"}), 404
        except Error:
            return jsonify({"error": "Error fetching document"}), 500
        finally:
            connection.close()
    else:
        return jsonify({"error": "Database connection failed"}), 500

@app.route('/update_document/<int:doc_id>', methods=['PUT'])
def update_document(doc_id):
    """
    Updates an existing document's title, content, and/or category.
    
    Args:
        doc_id (int): The ID of the document to update.
        
    Returns:
        JSON response indicating success or error.
    """
    data = request.json
    title = data.get('title')
    content = data.get('content')
    category = data.get('category')

    if not title and not content and not category:
        return jsonify({"error": "At least one field (title, content, or category) is required for update"}), 400

    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            update_fields = []
            update_values = []

            if title:
                update_fields.append("title = %s")
                update_values.append(title)
            if content:
                update_fields.append("content = %s")
                update_values.append(content)
                embedding = model.encode(content)
                embedding_bytes = encode_embedding(embedding)
                update_fields.append("embedding = %s")
                update_values.append(embedding_bytes)
            if category:
                update_fields.append("category = %s")
                update_values.append(category)

            update_values.append(doc_id)
            update_query = f"UPDATE documents SET {', '.join(update_fields)} WHERE id = %s"
            cursor.execute(update_query, update_values)

            connection.commit()
            return jsonify({"message": "Document updated successfully"}), 200
        except Error:
            connection.rollback()
            return jsonify({"error": "Error updating document"}), 500
        finally:
            connection.close()
    else:
        return jsonify({"error": "Database connection failed"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    CORS(app)
