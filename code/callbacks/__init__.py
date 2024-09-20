from .upload_callbacks import register_upload_callbacks
from .llm_callbacks import register_llm_callbacks
from .report_callbacks import register_report_callbacks
from .model_callbacks import register_model_callbacks
from .chat_callbacks import register_chat_callbacks

def register_callbacks(app):
    register_upload_callbacks(app)
    register_llm_callbacks(app)
    register_report_callbacks(app)
    register_model_callbacks(app)
    register_chat_callbacks(app)
