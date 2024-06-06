# Nutrition OCR

## Running the Models

These steps will guide you through setting up the environment, installing dependencies, and running the NutriLens Grade Models.

### **1. Set Up the Environment**

* Install `virtualenv`:

```bash
pip install virtualenv
```
* Set the python version:
```bash
virtualenv --python=python3.10 .venv
```
* Create Environment
```bash
python -m venv .venv
```
* Activate the Environment
```bash
.venv\Scripts\activate
```
* Deactivate the Environment
```bash
deactivate
```


### **2. Install the required dependencies** 
```bash
pip install -r requirements.txt
```

### **3. Test the Api use this command:**

```bash
cd app
uvicorn app:app --port 8006 
```
Note:

* Change the `pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'` in .app/model/model.py to `pytesseract.pytesseract.tesseract_cmd = '<your local tesseract path>'`
* Replace `<your local tesseract path>` with the path to your local Tesseract installation.
* Replace `<specified your port>` with the port number you want to use. 

After running the command, you should see output similar to:

```text
INFO:Uvicorn running on http://localhost:8006 (Press CTRL+C to quit)
```
This indicates that your FastAPI application is running and can be accessed at `http://localhost:8006` in your browser.

### **4. Built Docker Image**
```bash
docker build -t nutri-ocr .
```

### **5.Run Docker Container**
```bash
docker run -d -p 8006:8006 nutri-ocr
```