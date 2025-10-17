from flask import jsonify
import traceback

def handle_exception(error):
    traceback.print_exc()
    return jsonify({'error': 'An error occurred', 'details': str(error)}), 500