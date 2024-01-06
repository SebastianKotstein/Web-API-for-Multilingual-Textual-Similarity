from .s_model import SModel
from .lru_cache import LRUCache

from scipy import spatial
import uuid


class InvalidRequestException(Exception):
    def __init__(self, message="Invalid request") -> None:
        self.message = message
        super().__init__(self.message)

class Pipeline:
    def __init__(self, model_checkpoint, cache_size = 1000) -> None:
        self.model = SModel(model_checkpoint)

        if cache_size:
            self.cache = LRUCache(cache_size,False)
        else:
            self.cache = None

    def process(self, input_dict, top = None):
        sentence_dict, is_cached_dict = self.json_to_sentence_dict(input_dict)
        batch = self.sentence_dict_to_batch(sentence_dict)
        if batch:
            embeddings = self.model.encode(batch)
            for i in range(len(batch)):
                sentence_dict[batch[i]] = embeddings[i]
                if self.cache:
                    self.cache.store(batch[i],embeddings[i])
        
        merged_output = self.merge_results_w_input_json(input_dict, sentence_dict, is_cached_dict)
        return self.limit_results(merged_output,top)


    def json_to_sentence_dict(self, input_dict):
        sentence_dict = dict()
        is_cached_dict = dict()

        if "jobs" not in input_dict:
            raise InvalidRequestException("The request does not contain a list of jobs, i.e., '$.jobs[*]'")
        if not len(input_dict["jobs"]):
            raise InvalidRequestException("The list of jobs, i.e., '$.jobs[*]', must contain at least one job item")

        for i,job in enumerate(input_dict["jobs"]):
            if "targetSentences" not in job:
                raise InvalidRequestException("The job '$.job["+str(i)+"]' has no property 'targetSentences'")
            if not len(job["targetSentences"]):
                raise InvalidRequestException("'$.jobs["+str(i)+"].targetSentences[*]' must contain at least one sentence item")
            if "jobId" not in job:
                job["jobId"] = str(uuid.uuid4())
            if "name" not in job:
                job["name"] = "job "+job["jobId"]
            
            if "sentences" not in job:
                raise InvalidRequestException("The job '$.jobs["+str(i)+"]' has no list of sentences, i.e., '$.jobs["+str(i)+"].sentences[*]'")
            if not len(job["sentences"]):
                raise InvalidRequestException("'$.jobs["+str(i)+"].sentences[*]' must contain at least one sentence item")
            
            for j,sentence in enumerate(job["sentences"]):
                if "value" not in sentence:
                    raise InvalidRequestException("The sentence '$.jobs["+str(i)+"].sentences["+str(j)+"]' has no property 'value'")
                if not sentence["value"]:
                    raise InvalidRequestException("'$.jobs["+str(i)+"].sentences["+str(j)+"].value' must not be empty")
                if "sentenceId" not in sentence:
                    sentence["sentenceId"] = str(uuid.uuid4())
                if "name" not in sentence:
                    sentence["name"] = "query "+sentence["sentenceId"]
                #if "verboseOutput" not in sentence:
                #    sentence["verboseOutput"] = False

                if sentence["value"] not in sentence_dict:
                    sentence_dict[sentence["value"]] = None
                    if self.cache and self.cache.has(sentence["value"]):
                        sentence_dict[sentence["value"]] = self.cache.load(sentence["value"])

            for target_sentence in job["targetSentences"]:
                sentence_dict[target_sentence] = None
                if self.cache and self.cache.has(target_sentence):
                    sentence_dict[target_sentence] = self.cache.load(target_sentence)
                    is_cached_dict[target_sentence] = True
                else:
                    is_cached_dict[target_sentence] = False
        return sentence_dict, is_cached_dict

    
    def sentence_dict_to_batch(self, sentence_dict):
        batch = []
        for key in sentence_dict.keys():
            if sentence_dict[key] is None:
                batch.append(key)
        return batch

    def merge_results_w_input_json(self, input_dict, results, is_cached):

        for job in input_dict["jobs"]:
            for sentence in job["sentences"]:
                sentence["similarities"] = []
                for target_sentence in job["targetSentences"]:
                    sentence["similarities"].append({
                        "targetSentence": target_sentence,
                        "distance": self.calculate_spatial_distance(results[sentence["value"]],results[target_sentence])
                    }) 
                sentence["similarities"] = sorted(sentence["similarities"], key=lambda x: x["distance"], reverse=False)
                for similarity in sentence["similarities"]:
                    similarity["distance"] = str(similarity["distance"])
        return input_dict

    def calculate_spatial_distance(self, a,b):
        #print(spatial.distance.cosine(a,b))
        return spatial.distance.cosine(a,b)
    
    def limit_results(self, input_dict, top = None):
        if top:
            for job in input_dict["jobs"]:
                for sentence in job["sentences"]:
                    if len(sentence["similarities"]) > top:
                        sentence["similarities"] = sentence["similarities"][0:top]
        return input_dict


                

                

                    
                
                

                

                 