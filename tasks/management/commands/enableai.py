import os

from django.core.management import BaseCommand
import dotenv


# Command which runs pip install torch transformers
class Command(BaseCommand):
    def handle(self, *args, **options):
        # if windows
        if os.name == 'nt':
            os.system(' pip3 install --pre torch --index-url https://download.pytorch.org/whl/nightly/')
        else:
            os.system('pip3 install torch')
        os.system('pip3 install transformers')
        # set change .env file so that AI=1
        os.environ["AI"] = str(1)
        dotenv_file = dotenv.find_dotenv()
        dotenv.load_dotenv(dotenv_file)
        dotenv.set_key(dotenv_file, "AI", "1")
        print("AI Enabled")
