import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    @staticmethod
    def get_instance_config():
        # Determine how many instances are configured
        num_instances = int(os.getenv('NUM_INSTANCES', 1))

        instances = []
        for i in range(1, num_instances + 1):
            access_token = os.getenv(f'MASTODON_ACCESS_TOKEN_{i}')
            base_url = os.getenv(f'MASTODON_API_BASE_URL_{i}')
            collection_name = os.getenv(f'MASTODON_API_BASE_URL_{i}')  # Generate a JSON file name dynamically

            if access_token and base_url:
                instances.append({
                    'access_token': access_token,
                    'base_url': base_url,
                    'collection_name': collection_name
                })

        return instances


