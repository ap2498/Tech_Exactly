### Python Version: 3.11.14

### Application Overview:
Uses Langchain and llama-3.1-8b-instant to summarize documents. The google drive folder is linked to our code with o-auth 2 credentials. The application at start downloads all files from the hardcoded folder id on google drive and saves it locally. Then according to the format of the file **(supported types: pdf, doc, rtf, txt, csv)** the contents are scanned and passed to the LLM which summarizes the content and saves them in an array which is later converted to a csv file with pandas. The output can be checked by postman by visitng the **summarizerBot** route with **GET** method.

### Step by Step Guide:
0.)You can download the o-auth 2 credentials file and .env file from here 

https://drive.google.com/drive/folders/187vUfUPnI0RUFMQQqk3YPXwKBZDIpX2w?usp=drive_link 

I have sent the credentials.json and .env file via email. Please paste those files here as uploading these files in github will make them stop working due to GitGuardian. I have the sent the files to hr@techexactly.com. Please download fthem and paste them in the root folder. Make sure the **"."** is there in the **.env** file as downloading it will remove the **".""** so just rename it.

1.) Open terminal/cmd with this project folder as root.

2.) Start your python virtual environment

3.) From the same terminal/cmd run "pip install -r requirements.txt"

4.) Then from the same terminal run "python app.py"

5.) You will see a url in the cmd. Copy it and open postman. It will look like something like this **http://127.0.0.1:3000**

5.) Once the link is copied open postman and paste it in the address bar. then after the port add **/summarizerBot**.
It will look something like this **http://127.0.0.1:3000/summarizerBot**

6.) Make sure the **GET** method is selected.

7.) Hit **Send** and wait for the result.


### Output Fomat:
The output will have keys **"status"**: which is the response status of the API **"message"**: which contaitns a generic message **"outputFilePath"** : which is the path of the output csv summary report file and **"list"**: which is a dictionary that has keys **"originalFileName"**: which is the name of the orginal file, **"originalFilePath"**:which is the path of the orginal file and **"summarizedContent"**: which is the summarized content of the file and **"goolgleDriveLink"**: which will contain the link of the file on google drive. These fields are there in te final csv output file in key **"outputFilePath"**.

### Important:
I have sent the service_account.json and .env file via email. Please paste those files here as uploading these files in github will make them stop working due to GitGuardian. I have the sent the files to hr@techexactly.com. Please download fthem and paste them in the root folder. Make sure the **"."** is there in the **.env** file as downloading it will remove the **".""** so just rename it.

If the app crashes or stops in between please restart the app. It should work fine after that.