### Python Version: 3.11.14

### Application Overview:
Uses Langchain and llama-3.1-8b-instant to summarize documents. The google drive folder is linked to our code with service account credentials. The application at start downloads all files from the hardcoded folder id on google drive and saves it locally. Then according to the format of the file **(supported types: pdf, doc, rtf, txt, csv)** the contents are scanned and passed to the LLM which summarizes the content and saves them in an array which is later converted to a csv file with pandas. The output can be checked by postman by visitng the **summarizerBot** route with **GET** method.

### Step by Step Guide:
1.) Open terminal/cmd 

2.) Start your python virtual environment

3.) From the same terminal/cmd run "pip install -r requirements.txt"

4.) Then from the same terminal run "python app.py"

5.) You will see a url in the cmd. Copy it and open postman. It will look like something like this **http://127.0.0.1:3000**

5.) Once the link is copied open postman and paste it in the address bar. then after the port add **/summarizerBot**.
It will look something like this **http://127.0.0.1:3000/summarizerBot**

6.) Make sure the **GET** method is selected.

7.) Hit **Send** and wait for the result.

### Important:
If the app crashes or stops in between please restart the app. It should work fine after that.