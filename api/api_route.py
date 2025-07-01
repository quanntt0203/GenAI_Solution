import sys
import os
sys.path.append(os.path.abspath("D:\\AI\\agent-ai-assistant\\chatbot"))
#sys.path.append(os.path.abspath("\src\chatbot"))

from flask import Flask, jsonify, request, redirect
from flasgger import Swagger
from chatbot.translate_run import translate_text  # Assuming you have a translation module

app_api = Flask(__name__)
app_api.config['SWAGGER'] = {
  'title': 'API Documentation - βeta', 'version': '1.0',
  'description': 'API for AI Assistant',
  'uiversion': 3
}
swagger = Swagger(app_api)

# @app_api.route('/apidocs', methods=['GET'])
# def swagger_ui():
#     """
#     Redirect to Swagger UI.
#     """
#     return jsonify({"swagger_url": "/apidocs"})
  
@app_api.route('/', methods=['GET'], endpoint='index')
def index():
    return redirect("/apidocs")
    return jsonify({"message": "Welcome to the API"}), 200

@app_api.route('/api/translate', methods=['POST'], endpoint='translate')
def translate():
    """
    Translation endpoint.
    ---
    parameters:
      - in: body
        required: true
        type: object
        properties:
          target:
            type: string
            description: The target language for the translation (optional)
          content:
            type: string
            description: The content to be translated
        description: JSON for translation
      
    responses:
      200:
        description: Returns a simple greeting message
        examples:
          application/json: {"message": "Hello, World!"}
    """
    #print(request.form)
    #print(request.data)

    content = request.form.get('content')
    if content is None:
        content = 'Hello, World!'
    target = request.form.get('target')
    if target is None:
        target = 'thai'

    # Here you would implement the translation logic using the content and target language
    if content is None:
        return jsonify({"error": "Content is required", "status": "error"}), 400
    
    response = translate_text(content, target)
    if response is None:
        return jsonify({"error": "Translation failed", "status": "error"}), 500
    # Assuming translate_text is a function that performs the translation 
    return jsonify({"response": response, "status": "success"}), 200

@app_api.route('/api/chat', methods=['POST'])
def chat():
    """
     Chat endpoint.
    ---
    parameters:
      - in: body
        required: true
        type: object
        properties:
          session_key:
            type: string
            description: UUID for the session
          question:
            type: string
            description: The question to ask the chatbot
        description: JSON for Q&A

    responses:
      200:
        description: Returns the response from the chatbot
        examples:
          application/txt: Hi! How can I help you today?
    """
    session_key = float(request.form.get('session_key'))
    quesion = float(request.form.get('quesion'))
    return jsonify({"response": quesion})

@app_api.route('/api/extract', methods=['POST'])
def extract():
    """
     Extraction endpoint.
    ---
    parameters:
      - in: body
        required: true
        type: object
        properties:
          from_date:
            type: string
            format: dd-mm-yyyy
            description: The start date for the report
          to_date:
            type: string
            format: dd-mm-yyyy
            description: The end date for the report
          products:
            type: string
            description: The product for the report
          bet_type:
            type: string
            description: The type of bet for the report
          sports:
            type: string
            description: The sport for the report
          report_type:
            type: string
            description: The type of report to generate
          session_key: 
            type: string
            description: UUID for the session 
        description: JSON for report generation
    responses:
      200:
        description: Returns the response from the chatbot
    """
    session_key = float(request.form.get('session_key'))
    quesion = float(request.form.get('quesion'))
    return jsonify({"response": quesion})


@app_api.route('/api/generate', methods=['POST'])
def generate():
    """
    Generation endpoint.
    ---
    responses:
      200:
        description: Returns a simple health check message
        examples:
          application/json: {"status": "ok"}
    """
    return jsonify({"status": "ok"}), 200


# if __name__ == '__main__':
#     app_api.run( debug=True, port=8080 )