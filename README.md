## Overview 
A python client that replicates the implementation at  https://github.com/ggerganov/llama.cpp/blob/master/examples/server/chat.sh

The client connects to a llama server running on localhost and executes tasks concurrently where each task maps to a process thread.

## Example

 ```echo "i want to hike in the alps in -20 degrees" | python3 entity-extraction.py```