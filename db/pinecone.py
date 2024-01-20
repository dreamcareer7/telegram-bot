import pinecone
import os
from ai.embeddings import create_embedding_with_ada

class Pinecone():
    def __init__(self):
        pinecone_api_key = os.getenv("PINECONE_KEY")
        pinecone_region = os.getenv("PINECONE_REGION", "us-east1-gcp")
        pinecone.init(api_key=pinecone_api_key, environment=pinecone_region)

        dimension = 1536
        metric = "cosine"
        pod_type = "p1"
        index_name = "users"
        # this assumes we don't start with memory.
        # for now this works.
        # we'll need a more complicated and robust system if we want to start with
        #  memory.
        self.vec_num = 0

        try:
            pinecone.whoami()
        except Exception as e:
            print("Failed to connect to Pinecone")
            exit(1)

        # Create table name if not exists
        if index_name not in pinecone.list_indexes():
            # TODO: for performance reasons, metadata config limits indexes to just these
            # TODO: can do this at end towards production release to prevent everything being index
            # metadata_config = {
            #     "indexed": ["_id", "disk"]
            # }
            pinecone.create_index(
                index_name, dimension=dimension, metric=metric, pod_type=pod_type
            )
        
        # Set index
        self.index = pinecone.Index(index_name)

    def add(self, data: str, metadata: dict = {}):
        try:
          vector = create_embedding_with_ada(data)
          
          # add raw_text to metadata dict
          metadata["raw_text"] = data

          self.index.upsert([(str(self.vec_num), vector, metadata)])

          return True
        except:
          print("Failed to add to Pinecone")
          return False

    def clear(self):
        self.index.delete(deleteAll=True)
        return "Cleared Pinecone"

    def get_relevant(self, data, metadata: dict = {}, num_relevant=3):
        """
        Returns all the data in the memory that is relevant to the given data.
        :param data: The data to compare to.
        :param num_relevant: The number of relevant data to return. Defaults to 3
        """
        query_embedding = create_embedding_with_ada(data)
        results = self.index.query(
            query_embedding, filter=metadata, top_k=num_relevant, include_metadata=True
        )
        sorted_results = sorted(results.matches, key=lambda x: x.score)
        # raw_text is the actual text stored with the embedding
        return [str(item["metadata"]["raw_text"]) for item in sorted_results]

    def get_stats(self):
        return self.index.describe_index_stats()

    def bookmark_message(self, message: str, _id: str, disk: str):
      """
      Bookmarks a message for a user
      :param message: The message to bookmark
      :param user_id: The user to bookmark the message for
      """

      self.add(message, {"_id": _id, "disk": disk, "type": "bookmark"});
      

        
