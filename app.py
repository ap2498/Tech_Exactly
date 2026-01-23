import os
import io
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from langchain_classic.document_loaders import PyPDFLoader, UnstructuredWordDocumentLoader, TextLoader, CSVLoader, UnstructuredRTFLoader
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
load_dotenv()
from flask import Flask, jsonify
import pandas as pd
import shutil

app=Flask(__name__)
model=ChatGroq(api_key=os.getenv("API_KEY"),model="llama-3.1-8b-instant")
LINK_DICT={}
FOLDER_ID = "1patwlkTc1-OeuzOXJ2NZ_s91WsXdtcWg"
CURRENT_DIRECTORY=os.getcwd()
DOWNLOAD_DIR = os.path.join(CURRENT_DIRECTORY,'downloads')
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

if os.path.exists(DOWNLOAD_DIR):
    shutil.rmtree(DOWNLOAD_DIR)

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

creds = None

# token.json stores user's access & refresh tokens
if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)

# If no valid credentials, do OAuth login
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            "credentials.json",
            SCOPES
        )
        creds = flow.run_local_server(port=0)

    # Save token for future runs
    with open("token.json", "w") as token:
        token.write(creds.to_json())

service = build("drive", "v3", credentials=creds)

query = f"'{FOLDER_ID}' in parents and trashed=false"

response = service.files().list(
    q=query,
    fields="files(id, name, mimeType,webViewLink, webContentLink)"
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
    link= file['webViewLink']

    print(f"Downloading: {name}")
    LINK_DICT[name]=link
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

print("Download complete")



@app.route('/summarizerBot',methods=['GET'])
def summarizer_bot():

    current=os.getcwd()
    files_path=os.path.join(current,'downloads')
    file_names=os.listdir(files_path)
    print(file_names)
    results=[]
    for file in file_names:
        if file not in LINK_DICT:
            print(f"Skipping File: {file}. Not present in Gdrive folder")
            continue
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

        g_drive_link=LINK_DICT.get(file) if LINK_DICT.get(file) else "Link not found. Please rerun the application."
        results.append({
            "summarizedContent": response.content,
            "originalFileName": file,
            'originalFilePath':os.path.join(files_path,file),
            'googleDriveLink':g_drive_link
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