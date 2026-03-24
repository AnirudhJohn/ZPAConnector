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
        <img src="data:image/png;base64,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" alt="ZPA Logo">

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

