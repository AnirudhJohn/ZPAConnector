from flask import Flask, request, jsonify, render_template_string, redirect, url_for, session
import uuid, random, string
from urllib.parse import unquote

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set a secret key for session management

# Hardcoded login credentials (for demonstration purposes)
USERNAME = 'testuser'
PASSWORD = 'a9Xf$7Kd!r8Jw2Q'

# In-memory storage for scripts (for simplicity)
scripts = {}

# HTML template for the login page
login_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f6f9;
            color: #333;
            padding: 20px;
            margin: 0;
        }
        form {
            background: #fff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            max-width: 400px;
            margin: 50px auto;
        }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
        }
        input {
            width: calc(100% - 22px);
            padding: 10px;
            margin-bottom: 15px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        button {
            background-color: #007BFF;
            color: #fff;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            transition: background-color 0.3s ease;
            font-size: 16px;
        }
        button:hover {
            background-color: #0056b3;
        }
        p.error {
            color: red;
        }
    </style>
</head>
<body>
    <form method="POST">
        <h2>Login</h2>
        {% if error %}
            <p class="error">{{ error }}</p>
        {% endif %}
        <label for="username">Username:</label>
        <input type="text" name="username" required>
        <label for="password">Password:</label>
        <input type="password" name="password" required>
        <button type="submit">Login</button>
    </form>
</body>
</html>
"""

# HTML template for the form (with a logo and form structure)
form_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ZPA App Connector Deployments Automation</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f6f9;
            color: #333;
            padding: 20px;
            margin: 0;
        }
        .logo-container {
            text-align: center;
            margin-bottom: 20px;
        }
        .logo-container img {
            max-width: 100%;
            height: auto;
            max-height: 100px;
        }
        h1 {
            color: #007BFF;
            text-align: center;
            margin-bottom: 20px;
        }
        .instructions {
            background: #fff;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            max-width: 600px;
            margin: 20px auto;
            line-height: 1.6;
        }
        .instructions h2 {
            color: #007BFF;
            margin-bottom: 10px;
            font-size: 18px;
        }
        .instructions p {
            margin: 8px 0;
        }
        form {
            background: #fff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            max-width: 600px;
            margin: 20px auto;
        }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
        }
        textarea {
            width: calc(100% - 20px);
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            margin-bottom: 15px;
            margin-right: 10px;
            resize: vertical;
            font-family: monospace;
            font-size: 14px;
            box-sizing: border-box;
        }
        button {
            background-color: #007BFF;
            color: #fff;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            transition: background-color 0.3s ease;
            font-size: 16px;
        }
        button:hover {
            background-color: #0056b3;
        }
        #result {
            background: #fff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            max-width: 600px;
            margin: 20px auto;
        }
        #result h3 {
            margin-top: 0;
            color: #007BFF;
        }
        #result p, #result pre {
            margin: 10px 0;
            word-wrap: break-word;
        }
        pre {
            background: #f1f1f1;
            padding: 10px;
            border-radius: 5px;
            overflow-x: auto;
        }
        code {
            font-family: monospace;
            font-size: 14px;
        }
        a {
            color: #007BFF;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
    </style>
    <script>
        function submitForm(event) {
            event.preventDefault();
            const form = event.target;
            const formData = new FormData(form);

            fetch('/generate_script', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                const resultDiv = document.getElementById('result');
                resultDiv.innerHTML = `
                    <h3>Generated Script URL:</h3>
                    <p><a href="${data.script_url}" target="_blank">${window.location.origin}${data.script_url}</a></p>
                    <h3>Command to run:</h3>
                    <pre><code>sudo su
curl ${window.location.origin}${data.script_url} | bash</code></pre>
                `;
            })
            .catch(error => {
                console.error('Error:', error);
            });
        }
    </script>
</head>
<body>
    <div class="logo-container">   
        <img src="https://media.licdn.com/dms/image/v2/D560BAQE78qDB-dKzPQ/company-logo_200_200/company-logo_200_200/0/1733520360748/epiccyber_logo?e=2147483647&v=beta&t=fTs11dpCGVG1I09wGs_shzk8_XjGPSv0F-0Wx6jHtBI" alt="ZPA Logo">
    </div>
    <h1>ZPA App Connector Deployments Automation</h1>
    <div class="instructions">
        <h2>Instructions:</h2>
        <p><strong>Step 1:</strong> Add the provisioning key from the ZPA Admin portal and enter it in the text area below.</p>
        <p><strong>Step 2:</strong> Run the generated commands on the app connector to provision the new connector.</p>
    </div>
    <form onsubmit="submitForm(event)">
        <label for="provisioning_key">Provisioning Key:</label>
        <textarea id="provisioning_key" name="provisioning_key" rows="8" required></textarea>
        <button type="submit">Generate Script</button>
    </form>
    <div id="result"></div>
</body>
</html>
"""

# Route for the login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == USERNAME and password == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            return render_template_string(login_template, error="Invalid credentials, please try again.")
    return render_template_string(login_template)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

# Route for the main page (requires login)
@app.route('/', methods=['GET'])
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template_string(form_html)

@app.route('/generate_script', methods=['POST'])
def generate_script():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    encoded_key = request.form.get('provisioning_key')
    provisioning_key = unquote(encoded_key)
    script_id = ''.join(random.choices(string.ascii_letters, k=4))

    script_content = f"""#!/bin/bash

FILE="/opt/zscaler/var"
PROVISION_KEY=""

# Ensure the script is run as root
if [ "$EUID" -ne 0 ]; then
    echo "Run as root!!"
    exit 1
fi

# Prompt user before proceeding
read -p "Proceed with ZPA Connector provisioning? (y/n): " confirm
if [[ "$confirm" != "y" ]]; then
    echo "Cancelling..."
    exit 0
fi

# Define the content for the Zscaler repository configuration
REPO_CONTENT="[zscaler]
name=Zscaler Private Access Repository
baseurl=https://yum.private.zscaler.com/yum/el9
enabled=1
gpgcheck=1
gpgkey=https://yum.private.zscaler.com/yum/el9/gpg"

REPO_FILE="/etc/yum.repos.d/zscaler.repo"

# Create or overwrite the repository file
echo "$REPO_CONTENT" | sudo tee "$REPO_FILE" > /dev/null

echo "********************************************************"
echo "*                                                      *"
echo "*         Provisioning ZPA Connector                   *"
echo "*                                                      *"
echo "********************************************************"
echo

echo "Zscaler repository added to $REPO_FILE"

# Install the Zscaler App Connector
yum install zpa-connector -y

echo
echo "Stopping the ZPA Process..."; sleep 2
systemctl stop zpa-connector
echo "ZPA process stopped."

echo
echo "Removing previous configuration..."; sleep 2
rm -rf "$FILE"/*
echo "Successfully removed!"

# Create new provisioning key file
touch "$FILE/provision_key"
chmod 644 "$FILE/provision_key"
echo "${provisioning_key}" > "$FILE/provision_key"

echo
echo "Starting the ZPA Connector service again..."; sleep 1
systemctl start zpa-connector
sleep 2

# Monitor service status
clear
watch -n 1 systemctl status zpa-connector
    """

    # Store the script content (this should be replaced with a database for production)
    scripts[script_id] = script_content

    # Generate the unique script URL using the same Flask host
    script_url = f"/{script_id}"
    return jsonify({'script_url': script_url, 'script_content': script_content})


@app.route('/<script_id>', methods=['GET'])
def get_script(script_id):
    # Fetch the script content by ID
    script_content = scripts.get(script_id)
    if script_content:
        return script_content, 200, {'Content-Type': 'text/plain'}
    else:
        return "Script not found", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

