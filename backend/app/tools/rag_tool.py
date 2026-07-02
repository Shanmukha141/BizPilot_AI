import os
import chromadb
from PyPDF2 import PdfReader

# 1. Initialize ChromaDB (This creates a local 'vector_db' folder in your backend)
db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'vector_db')
chroma_client = chromadb.PersistentClient(path=db_path)

# 2. Get or create a collection to store our document embeddings
collection = chroma_client.get_or_create_collection(name="business_docs")

def ingest_pdf(file_path: str):
    """Reads a PDF, chunks it into paragraphs, and saves it to ChromaDB."""
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        
        # Better chunking: Fixed-size chunks with overlap for better context retention
        chunk_size = 1000
        chunk_overlap = 200
        chunks = []
        
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end].strip()
            if len(chunk) > 50:
                chunks.append(chunk)
            start += (chunk_size - chunk_overlap)
        
        # Prepare IDs and Metadata for ChromaDB
        ids = [f"doc_{os.path.basename(file_path)}_{i}" for i in range(len(chunks))]
        metadatas = [{"source": os.path.basename(file_path)}] * len(chunks)
        
        # Add to ChromaDB (Chroma automatically handles the embeddings here)
        collection.add(
            documents=chunks,
            ids=ids,
            metadatas=metadatas
        )
        print(f"Success: Ingested {len(chunks)} chunks from {file_path}")
    except Exception as e:
        print(f"Error ingesting PDF: {str(e)}")

def search_business_documents(query: str) -> str:
    """Searches the company documents (SOPs, contracts, HR policies) to answer questions."""
    try:
        # The Retriever pulls the most relevant chunks based on the user's query
        results = collection.query(
            query_texts=[query],
            n_results=3 # Fetch the top 3 most relevant chunks
        )
        
        if not results['documents'][0]:
            return "No relevant business documents found for this query."
            
        # Combine the retrieved chunks into a single context string for Gemini
        context = "\n\n".join(results['documents'][0])
        return f"Found the following information in the internal documents:\n{context}"
    except Exception as e:
        return f"Error searching documents: {str(e)}"