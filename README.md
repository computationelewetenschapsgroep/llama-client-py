## Overview 
A python client that replicates the implementation at  https://github.com/ggerganov/llama.cpp/blob/master/examples/server/chat.sh

The client connects to a llama server running on localhost and executes tasks concurrently where each task maps to a process thread.

## Example

 ```echo "i want to hike in the alps in -20 degrees" | python3 entity-extraction.py```

### Dispatcher Pattern

Even though the client makes concurrent requests to the server, the server processes each request sequentially. Therefore even if the server takes approx 500ms (llama-server with qwen2.5-1.5b-instruct-q5_k_m.gguf) to run inference on a query. The overall time elapsed on the client to process 4 concurrent requests if 4 * 500ms . Therefore we wanted to try the idea of running separate instances of llama-server on 4 separate ports and use a route table in the client to map each request to an instance of the server running on a separate port. However this added to the execution time drastically rather than reducing it.. For example the elapsed time on the client increased 10x. It needs to be investigated where is the bottleneck! 
