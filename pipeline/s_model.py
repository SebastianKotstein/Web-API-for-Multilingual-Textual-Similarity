from sentence_transformers import SentenceTransformer
import tensorflow as tf
from scipy import spatial

class SModel:
    def __init__(self, model_path, batch_size) -> None:
        print(tf.config.list_physical_devices('GPU'))
        self.model = SentenceTransformer(model_path)
        self.batch_size = batch_size

    def predict(self):
        sentences = ["Web API for multilingual textual similarity","Web-API für mehrsprachige textuelle Ähnlichkeit","API web para la similitud textual multilingüe","API web per la similarità del testo multilingue","Mi chiamo Sebastian","Me llamo Sebastian"]
        embeddings = self.model.encode(sentences)
        for i in range(embeddings.shape[0]-1):
            print(1 - spatial.distance.cosine(embeddings[0],embeddings[i+1])," (",sentences[i+1],")")
            #print(dot(embeddings[0],embeddings[i])/(embeddings[0]*embeddings[i]))

