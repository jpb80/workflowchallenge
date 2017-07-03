import os, sys

FILE_PATH = os.path.realpath(__file__)
head, tail = os.path.split(FILE_PATH)
sys.path.insert(0, head + "/src/workflowapp/")

import workflow

def main():
    workflow.run()

if __name__ == "__main__":
    main()
