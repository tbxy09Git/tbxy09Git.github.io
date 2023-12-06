import string
import random
from pathlib import Path

from pydantic import BaseModel, Field
from typing import List

from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles


def generate_random_string(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits,
                                  k=length))


class FileSchema(BaseModel):
    name: str = Field(..., description="Name of the upload file")
    content: str = Field(..., description="Content of the upload file")


class UploadFilesSchema(BaseModel):
    files: List[FileSchema] = Field(
        ..., description="Array of upload files object with name and content")


app = FastAPI()

# Dictionary to store random string and file path mapping
path_mapping = {}

# Mount a static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.post("/uploadCode")
async def upload_files(files: UploadFilesSchema):
    random_string = generate_random_string()
    save_directory = Path('static') / random_string
    save_directory.mkdir(parents=True, exist_ok=True)

    for file in files.files:
        file_path = save_directory / file.name
        # Ensure the directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(file.content)

    # Store the mapping
    path_mapping[random_string] = str(save_directory)
    return {
        "message":
        f"Files uploaded successfully. uniqueid: {random_string}. please form your url with end_point c/{random_string}"
    }


@app.get("/c/{random_string}")
async def serve_index(random_string: str):
    if random_string in path_mapping:
        file_path = Path(path_mapping[random_string]) / 'index.html'
        if file_path.is_file():
            return FileResponse(str(file_path))
        else:
            raise HTTPException(status_code=404, detail="Index file not found")
    else:
        raise HTTPException(status_code=404, detail="Random string not found")


@app.get("/privacy", response_class=HTMLResponse)
async def privacy_policy():
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Privacy Policy</title>
</head>
<body>

    <header>
        <h1>Privacy Policy for Cloner to remote deployment</h1>
    </header>

    <main>
        <section>
            <p>Effective date: 12/7/2023</p>

            <h2>1. Introduction</h2>
            <p>
                Thank you for using Cloner Service. This privacy policy ("Policy") describes our practices regarding the collection, use, and sharing of your information through the use of our FastAPI endpoint, which is accessible at https://clonerapi.replit.app ("Service"). 
            </p>

            <h2>2. Information We Do Not Collect</h2>
            <p>
                We do not collect or store any personal information from the users of our Service. The Service does not require any form of registration or submission of personal data. 
            </p>

            <h2>3. How We Use Information</h2>
            <p>
                Since we do not collect personal information, we do not use any such data in any way. Our Service is designed to be used without the necessity of providing any personal or identifiable information.
            </p>

            <h2>4. Sharing Of Information</h2>
            <p>
                We do not share any personal information simply because we do not collect any. There is no sharing of personal data with third parties, advertisers, or other users.
            </p>

            <h2>5. Data Security</h2>
            <p>
                The security of potential data is important to us. Even though we do not collect personal information, we strive to use commercially acceptable means to protect our Service and maintain the privacy of our users.
            </p>

            <h2>6. Changes to This Privacy Policy</h2>
            <p>
                We may update our Privacy Policy from time to time. We will notify you of any changes by posting the new Privacy Policy on this page. You are advised to review this Privacy Policy periodically for any changes.
            </p>

            <h2>7. Contact Us</h2>
            <p>
                If you have any questions about this Privacy Policy, please contact us:
                <ul>
                    <li>Via twitter: tbxy09@gmail.com</li>
                </ul>
            </p>
        </section>
    </main>

</body>
</html>
    """
    return Response(content=html_content, media_type="text/html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
