import yaml

def load_config():
    with open('config.yaml', 'r') as f:
        data = yaml.safe_load(f)
        return data