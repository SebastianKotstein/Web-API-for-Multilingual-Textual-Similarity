from sentence_transformers import SentenceTransformer
import tensorflow as tf

class SModel:
    def __init__(self, model_path, batch_size = 32) -> None:
        print(tf.config.list_physical_devices('GPU'))
        self.model = SentenceTransformer(model_path)
        self.batch_size = batch_size


    def encode(self, sentences):
        return self.model.encode(sentences,batch_size = self.batch_size)

    
