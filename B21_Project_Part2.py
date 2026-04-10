# Group #: B21
# Student names: Anna Bartl and Conor O'Neill
 
import threading
import queue
import time, random

# Global variable definitions
NUMBER_OF_CONSUMERS = 5
NUMBER_OF_PRODUCERS = 4
TOTAL_ITEMS = 22
RANDOM_PRODUCER_SLEEP = (0.1, 0.5) # seconds
RANDOM_CONSUMER_SLEEP = (0.1, 0.5) # seconds

def consumerWorker (q) -> None: #q is the passed queue object
    """target worker for a consumer thread"""
    while True:
        item = q.get()
        q.task_done() 
        if item is None: # check for sentinel value to know when to stop
            break
        print(f"{threading.current_thread().name} consumed: {item}")
        time.sleep(random.uniform(*RANDOM_CONSUMER_SLEEP))
  
def producerWorker(q, items_to_produce: int) -> None: #q is the passed queue object
    """target worker for a producer thread"""
    for i in range(items_to_produce):

        item = f"{threading.current_thread().name} Item {i + 1}"
        print(f"{threading.current_thread().name} produced: {item}")
        q.put(item)
        time.sleep(random.uniform(*RANDOM_PRODUCER_SLEEP))

if __name__ == "__main__":
    buffer = queue.Queue()

    producer_threads = []

    base_items = TOTAL_ITEMS // NUMBER_OF_PRODUCERS
    extra_items = TOTAL_ITEMS % NUMBER_OF_PRODUCERS

    for i in range(NUMBER_OF_PRODUCERS):
        items_for_this_producer = base_items + (1 if i < extra_items else 0)
        t = threading.Thread(target=producerWorker, args=(buffer, items_for_this_producer), name=f"PROD-{i}")
        t.start()
        producer_threads.append(t)
    
    consumer_threads = []
    for i in range(NUMBER_OF_CONSUMERS):
        t = threading.Thread(target=consumerWorker, args=(buffer,),name=f"CONS-{i}", daemon=True)
        t.start()
        consumer_threads.append(t)

    #Wait for all producers to finish
    for t in producer_threads:
        t.join()
    #Add sentinel values to the queue to signal consumers to stop
    for _ in range(NUMBER_OF_CONSUMERS):
        buffer.put(None)
    print("All producers have finished. Waiting for consumers to finish...")
    
    buffer.join() # Wait until all items have been processed
    print("All producers and consumers have finished.")