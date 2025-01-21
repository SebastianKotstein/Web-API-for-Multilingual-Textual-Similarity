from sentence_transformers import SentenceTransformer

class SModel:
    def __init__(self, model_path, batch_size = 32, token = None) -> None:
        self.model = SentenceTransformer(model_path,cache_folder="/cache/hf", token=token)
        self.batch_size = batch_size


    def encode(self, sentences):
        return self.model.encode(sentences,batch_size = self.batch_size)

    
