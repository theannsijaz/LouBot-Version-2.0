import os
import aiml
from LouBot.settings import BASE_DIR

aiml_directory = os.path.join(BASE_DIR, 'Data')
kernel = aiml.Kernel()

def init_kernel():
    kernel = aiml.Kernel()
    for file_name in os.listdir(aiml_directory):
        if file_name.endswith('.aiml'):
            file_path = os.path.join(aiml_directory, file_name)
            kernel.learn(file_path)

    kernel.setBotPredicate("name", "Anns Ijaz")
    kernel.setBotPredicate("master", "Anns Ijaz")       # shows up in replies
    kernel.setBotPredicate("botmaster", "Anns Ijaz")
    return kernel