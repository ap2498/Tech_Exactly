import os
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from langchain_classic.document_loaders import PyPDFLoader, UnstructuredWordDocumentLoader, TextLoader, CSVLoader, UnstructuredRTFLoader
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
load_dotenv()
from flask import Flask, jsonify
import pandas as pd

app=Flask(__name__)
model=ChatGroq(api_key=os.getenv("API_KEY"),model="llama-3.1-8b-instant")
SERVICE_ACCOUNT_FILE = "service_account.json"
FOLDER_ID = "1patwlkTc1-OeuzOXJ2NZ_s91WsXdtcWg"
DOWNLOAD_DIR = "downloads"

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

os.makedirs(DOWNLOAD_DIR, exist_ok=True)


credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=SCOPES
)

service = build("drive", "v3", credentials=credentials)


query = f"'{FOLDER_ID}' in parents and trashed=false"

response = service.files().list(
    q=query,
    fields="files(id, name, mimeType)"
).execute()

files = response.get("files", [])

print(f"files:{files}")

if not files:
    print("No files found.")
    exit()


for file in files:
    file_id = file["id"]
    name = file["name"]
    mime = file["mimeType"]

    print(f"Downloading: {name}")

    # Google Docs → export
    if mime.startswith("application/vnd.google-apps"):
        request = service.files().export_media(
            fileId=file_id,
            mimeType="application/pdf"
        )
        name += ".pdf"
    else:
        request = service.files().get_media(fileId=file_id)

    path = os.path.join(DOWNLOAD_DIR, name)

    with io.FileIO(path, "wb") as fh:
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            if status:
                print(f"  {int(status.progress() * 100)}%")

print("✅ Download complete")



@app.route('/summarizerBot',methods=['GET'])
def summarizer_bot():

    current=os.getcwd()
    files_path=os.path.join(current,'downloads')
    file_names=os.listdir(files_path)
    print(file_names)
    results=[]
    for file in file_names:
        f_name,ext=os.path.splitext(file)
        print(ext)
        if ext=='.pdf':
            loader=PyPDFLoader(os.path.join(files_path,file))
            documents=loader.load()
        elif ext=='.docx':
            loader=UnstructuredWordDocumentLoader(os.path.join(files_path,file))
            documents=loader.load()
        elif ext=='.txt':
            loader=TextLoader(os.path.join(files_path,file))
            documents=loader.load()
        elif ext=='.csv':
            loader=CSVLoader(os.path.join(files_path,file))
            documents=loader.load()
        elif ext=='.rtf':
            loader=UnstructuredRTFLoader(os.path.join(files_path,file))
            documents=loader.load()
        docs=documents
        document_text = "\n\n".join(doc.page_content for doc in documents if doc.page_content.strip())
        prompt_text='You are a helpful assistant expert in summarizing documents. You will be given contents of a document. Summarize the contents of the document.'

        prompt=ChatPromptTemplate.from_messages(
            [
                ('system',prompt_text),
                ('user','{input}')
            ]
        )
        chain=prompt | model
        response=chain.invoke({'input':document_text})

        results.append({
            "summarizedContent": response.content,
            "originalFileName": file,
            'originalFilePath':os.path.join(files_path,file)
        })

    df=pd.DataFrame(results)
    output_file=os.path.join(current,'summaries.csv')
    df.to_csv(output_file,index=False)


    return jsonify({
        'status':200,
        'message':"Files Summarized Succesfully",
        'outputFilePath':output_file,
        'list':results
    })

if __name__=="__main__":
    app.run(debug=True, host="0.0.0.0", port=3000)