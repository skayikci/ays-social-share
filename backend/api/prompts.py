from flask import Blueprint, request, jsonify
from services.prompt_service import PromptService
from bson import json_util

prompts_bp = Blueprint('prompts', __name__)

prompt_service = PromptService()

@prompts_bp.route('/prompts', methods=['POST'])
def create_prompt():
    """
    Endpoint to create a new prompt.
    """
    prompt = request.json.get('prompt')
    if not prompt:
        return jsonify({'status': 'error', 'message': 'Prompt is required'}), 400

    prompt_id = prompt_service.save_prompt(prompt)
    return jsonify({'status': 'success', 'prompt_id': str(prompt_id)})

@prompts_bp.route('/latest', methods=['GET'])
def get_latest_prompt(): 
    """
    Endpoint to get the latest prompt.
    """
    latest_prompt = prompt_service.get_latest_prompt()
    if not latest_prompt:
        return jsonify({'status': 'error', 'message': 'No prompts found'}), 404

    
    return jsonify({
        'status': 'success',
        'prompt': latest_prompt['content'],
        'created_at': latest_prompt['timestamp']
    })

@prompts_bp.route('/', methods=['GET'])
def get_all_prompts(): 
    """
    Endpoint to get all prompts.
    """
    all_prompts = prompt_service.get_all_prompts()
    if not all_prompts:
        return jsonify({'status': 'error', 'message': 'No prompts found'}), 404

    
    return json_util.dumps(all_prompts)


@prompts_bp.route('/prompts/<prompt_id>', methods=['GET'])
def get_prompt(prompt_id):
    """
    Endpoint to get a specific prompt by its ID.
    """
    prompt = prompt_service.get_prompt_by_id(prompt_id)
    if not prompt:
        return jsonify({'status': 'error', 'message': 'Prompt not found'}), 404
    
    return jsonify({'status': 'success', 'prompt': prompt['content'], 'created_at': prompt['created_at']})

@prompts_bp.route('/prompts/<prompt_id>', methods=['PUT'])
def update_prompt(prompt_id):
    """
    Endpoint to update a prompt's content.
    """
    new_content = request.json.get('content')
    if not new_content:
        return jsonify({'status': 'error', 'message': 'New content is required'}), 400
    
    result = prompt_service.update_prompt(prompt_id, new_content)
    if result.matched_count == 0:
        return jsonify({'status': 'error', 'message': 'Prompt not found'}), 404
    
    return jsonify({'status': 'success', 'message': 'Prompt updated successfully'})

@prompts_bp.route('/prompts/<prompt_id>', methods=['DELETE'])
def delete_prompt(prompt_id):
    """
    Endpoint to delete a prompt by its ID.
    """
    result = prompt_service.delete_prompt(prompt_id)
    if result.deleted_count == 0:
        return jsonify({'status': 'error', 'message': 'Prompt not found'}), 404

    return jsonify({'status': 'success', 'message': 'Prompt deleted successfully'})
