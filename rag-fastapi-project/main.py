
from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic_models import QueryInput, QueryResponse, DocumentInfo, DeleteFileRequest
from langchain_utils import conversational_rag_chain
from chroma_utils import get_vector_store, load_and_split_document
from db_utils import get_db_connection
import os
import uuid

app = FastAPI()

UPLOAD_DIR = "./uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@app.post("/chat", response_model=QueryResponse)
async def chat(query: QueryInput):
    result = conversational_rag_chain.invoke(
        {"input": query.query},
        config={
            "configurable": {"session_id": query.session_id}
        },
    )
    return QueryResponse(response=result["answer"], session_id=query.session_id)

@app.post("/upload-doc", response_model=DocumentInfo)
async def upload_doc(file: UploadFile = File(...)):
    try:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())
        
        doc_id = str(uuid.uuid4())
        chunks = load_and_split_document(file_path)
        get_vector_store().add_documents(chunks, ids=[doc_id] * len(chunks))
        
        conn = get_db_connection()
        conn.execute("INSERT INTO documents (doc_id, filename) VALUES (?, ?)", (doc_id, file.filename))
        conn.commit()
        conn.close()
        
        return DocumentInfo(filename=file.filename, doc_id=doc_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/list-docs", response_model=list[DocumentInfo])
async def list_docs():
    conn = get_db_connection()
    cursor = conn.execute("SELECT filename, doc_id FROM documents")
    docs = [DocumentInfo(filename=row["filename"], doc_id=row["doc_id"]) for row in cursor.fetchall()]
    conn.close()
    return docs

@app.post("/delete-doc")
async def delete_doc(request: DeleteFileRequest):
    try:
        conn = get_db_connection()
        conn.execute("DELETE FROM documents WHERE doc_id = ?", (request.doc_id,))
        conn.commit()
        conn.close()
        
        get_vector_store().delete(ids=[request.doc_id])
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
