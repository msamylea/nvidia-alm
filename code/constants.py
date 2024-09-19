LOGO_ICON = 'assets/logo.jpg'
LLM_PROVIDERS = {
    "HuggingFace": "huggingface-openai",
    "NVIDIA": "nvidia",
    "Google Gemini": "gemini",
}

LLM_PROVIDER_OPTIONS = [{"label": key, "value": value} for key, value in LLM_PROVIDERS.items()]

DATETIME_FORMATS = ['datetime64[s]', 'datetime64[ms]', 'datetime64[us]', 'datetime64[ns]', 'datetime64']
CATEGORICAL_DTYPES = ['string', 'object']
NUMERIC_DTYPES = ['int8', 'int16', 'int32', 'int64', 'float16', 'float32', 'float64']

MODEL_CHOICES = {
    "Random Forest": "rf",
    "Exponential Smoothing": "es",
    "Linear Regression": "lr",
}

MODEL_CHOICES_OPTIONS = [{"label": key, "value": value} for key, value in MODEL_CHOICES.items()]

PPT_THEME_OPTIONS = ["BlackWhite", "BlueYellow", "Orange", "Teal", "BlueGrey", "RedGrey"]