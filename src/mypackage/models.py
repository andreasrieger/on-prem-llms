def get_models():
    models = [
        {
            # Mistral
            "id": 0,
            "display_name": "Mistral",
            "model_description": "versatile use cases, european models",
            "name": "mistral"
        },{
            # StableLM2
            "id": 1,
            "display_name": "StableLM2",
            "model_description": "conversational use cases",
            "name": "stablelm2"
        },{
            # Salesforce Research embedding Mistral
            "id": 2,
            "display_name": "Salesforce Research embedding Mistral",
            "model_description": "embedding use cases",
            "name": "avr/sfr-embedding-mistral"
        }
    ]
    return models
