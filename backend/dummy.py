import mysql.connector
from mysql.connector import Error
import numpy as np
from sentence_transformers import SentenceTransformer
import random

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'shubham',
    'password': 'Sshubham@6762',
    'database': 'my_database'
}

# Function to create a connection to the database
def create_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except Error as e:
        print(f"Error: {e}")
        return None

# Function to encode the embeddings
def encode_embedding(embedding):
    return embedding.astype(np.float32).tobytes()

# Model for generating embeddings
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

# Function to insert dummy data
def insert_dummy_data():
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()

            # List of dummy documents (25 documents)
            dummy_docs = [
                {"title": "Introduction to AI", "content": "AI is the simulation of human intelligence in machines.", "category": "Technology"},
                {"title": "Quantum Computing", "content": "Quantum computers use qubits to represent and store data.", "category": "Technology"},
                {"title": "Climate Change and Global Warming", "content": "Climate change is caused by the increase in greenhouse gases.", "category": "Environment"},
                {"title": "The Solar System", "content": "Our solar system consists of the Sun, planets, and various celestial bodies.", "category": "Astronomy"},
                {"title": "History of the Internet", "content": "The Internet was developed as a communication network in the 1960s.", "category": "History"},
                {"title": "Nutrition and Health", "content": "A balanced diet includes carbohydrates, proteins, and fats.", "category": "Health"},
                {"title": "Machine Learning", "content": "Machine learning is a subset of AI where systems can learn from data.", "category": "Technology"},
                {"title": "Blockchain Technology", "content": "Blockchain is a decentralized ledger for recording transactions.", "category": "Technology"},
                {"title": "Basics of Python", "content": "Python is a popular high-level programming language.", "category": "Programming"},
                {"title": "Cybersecurity", "content": "Cybersecurity is the practice of protecting systems from digital attacks.", "category": "Technology"},
                {"title": "Renewable Energy", "content": "Renewable energy sources include solar, wind, and geothermal energy.", "category": "Environment"},
                {"title": "The Human Brain", "content": "The human brain is the central organ of the human nervous system.", "category": "Health"},
                {"title": "Artificial Neural Networks", "content": "Neural networks are computational models inspired by the human brain.", "category": "Technology"},
                {"title": "Big Data", "content": "Big data refers to the large volume of data that organizations generate.", "category": "Technology"},
                {"title": "Data Privacy and Ethics", "content": "Data privacy involves ensuring the privacy of user data.", "category": "Technology"},
                {"title": "History of Computers", "content": "The first modern computer was developed during World War II.", "category": "History"},
                {"title": "Sustainable Agriculture", "content": "Sustainable agriculture aims to meet society's food needs without harming the environment.", "category": "Environment"},
                {"title": "Cloud Computing", "content": "Cloud computing provides on-demand computing resources over the Internet.", "category": "Technology"},
                {"title": "Genetic Engineering", "content": "Genetic engineering is the manipulation of an organism's genes using biotechnology.", "category": "Biotechnology"},
                {"title": "5G Technology", "content": "5G is the latest generation of mobile network technology.", "category": "Technology"},
                {"title": "Mental Health Awareness", "content": "Mental health awareness aims to reduce stigma and support those with mental illness.", "category": "Health"},
                {"title": "Astronomy and Space Exploration", "content": "Space exploration is the discovery and exploration of outer space.", "category": "Astronomy"},
                {"title": "Cryptocurrency", "content": "Cryptocurrencies are digital assets secured by cryptography.", "category": "Technology"},
                {"title": "Renewable vs Non-renewable Energy", "content": "Non-renewable energy sources include coal and oil, while renewable sources include solar and wind.", "category": "Environment"},
                {"title": "Introduction to Data Science", "content": "Data science combines statistics, data analysis, and machine learning to extract insights from data.", "category": "Technology"}
            ]

            for doc in dummy_docs:
                title = doc['title']
                content = doc['content']
                category = doc['category']

                # Generate embeddings
                embedding = model.encode(content)
                embedding_bytes = encode_embedding(embedding)

                # Insert document into the database
                doc_query = "INSERT INTO documents (title, content, embedding, category) VALUES (%s, %s, %s, %s)"
                cursor.execute(doc_query, (title, content, embedding_bytes, category))

            connection.commit()
            print("25 dummy documents inserted successfully.")
        except Error as e:
            connection.rollback()
            print(f"Error inserting dummy documents: {e}")
        finally:
            connection.close()
    else:
        print("Failed to connect to the database.")

# Insert the dummy data
insert_dummy_data()
