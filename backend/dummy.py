import mysql.connector
from mysql.connector import Error
import numpy as np
from sentence_transformers import SentenceTransformer
import csv
import sys
import json

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
        print("Successfully connected to the database.")
        return connection
    except Error as e:
        print(f"Error connecting to the database: {e}")
        return None

# Function to encode the embeddings
def encode_embedding(embedding):
    return embedding.astype(np.float32).tobytes()

# Model for generating embeddings
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

def extract_content_data(data):
    content_string = list(data.values())[0]
    content_parts = content_string.split('\t')

    # Extracted Fields
    # print(content_string)
    category = None
    title = None
    content = None
    if (len(content_parts) >= 4):
        category = content_parts[0]
        filename = content_parts[1]
        title = content_parts[2]
        content = content_parts[3] + ''.join(data[None])

    return category, title, content

def insert_data_from_dict(title, category, content):
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()

            # Check if the table exists
            # cursor.execute("SHOW TABLES LIKE 'documents'")
            # result = cursor.fetchone()
            # if not result:
            #     print("Error: 'documents' table does not exist in the database.")
            #     return

            # Get table structure
            # cursor.execute("DESCRIBE documents")
            # table_structure = cursor.fetchall()
            # print("Table structure:", table_structure)

            # Extract category, title, and content from the dictionary
            # category, title, content = extract_content_data()
            
            if (title == None or category == None or content == None):
                return
            # print(category, title, content)
            
            
            # return 

            if not content:
                print("Skipping data with empty content.")
                return

            try:
                # Generate embeddings
                embedding = model.encode(content)
                embedding_bytes = encode_embedding(embedding)

                # Insert document into the database
                doc_query = "INSERT INTO documents (title, content, embedding, category) VALUES (%s, %s, %s, %s)"
                cursor.execute(doc_query, (title, content, embedding_bytes, category))
                # print("Data inserted successfully.")

            except Exception as e:
                print(f"Error processing the data: {e}")

            connection.commit()
            # print("Committed changes to the database.")
        except Error as e:
            connection.rollback()
            # print(f"Error during database operation: {e}")
        finally:
            cursor.close()
            connection.close()
            # print("Database connection closed.")
    else:
        print("Failed to connect to the database.")

# Function to insert data from CSV
# def insert_data_from_csv(csv_file_path):
#     connection = create_connection()
#     if connection:
#         try:
#             cursor = connection.cursor()

#             # Check if the table exists
#             # cursor.execute("SHOW TABLES LIKE 'documents'")
#             # result = cursor.fetchone()
#             # if not result:
#             #     print("Error: 'documents' table does not exist in the database.")
#             #     return

#             # # Get table structure
#             # cursor.execute("DESCRIBE documents")
#             # table_structure = cursor.fetchall()
#             # print("Table structure:", table_structure)

#             with open(file_path, 'r') as file:
#                 data = json.load(file)

#             # Extracting the fields from each object
#             for article in data:
#                 title = article.get('headline', 'N/A')
#                 category = article.get('category', 'N/A')
#                 content = article.get('short_description', 'N/A')
                
                
#             connection.commit()
#             # print(f"Processed {row_count} rows. Committing changes to the database.")
#         except Error as e:
#             connection.rollback()
#             print(f"Error during database operation: {e}")
#         finally:
#             cursor.close()
#             connection.close()
#             print("Database connection closed.")
#     else:
#         print("Failed to connect to the database.")
file_path = 'abc.json'
# Path to your CSV file
json_objects = []

# Open and read the file line by line
with open(file_path, 'r') as file:
    for line in file:
        try:
            # Parse each line as a JSON object
            json_object = json.loads(line)
            json_objects.append(json_object)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON on line: {line}\n{e}")

# Print the extracted objects
for obj in json_objects:
    # link = obj.get('link', 'N/A')
    title = obj.get('headline', 'N/A')
    category = obj.get('category', 'N/A')
    content = obj.get('short_description', 'N/A')
    # authors = obj.get('authors', 'N/A')
    # date = obj.get('date', 'N/A')
    
    insert_data_from_dict(title, category, content)

# Print any error output
print("Error output:", file=sys.stderr)
sys.stderr.flush()