# Group #: B21
# Student names: Anna Bartl and Conor O'Neill
 
import threading
import queue
import time, random

# TODO 3 - no other imports allowed!

# TODO 6 - Global variable definitions
NUMBER_OF_CONSUMERS = 5
NUMBER_OF_PRODUCERS = 4
ITEMS_TO_PRODUCE = 5
RANDOM_PRODUCER_SLEEP = (0.1, 0.5) # seconds
RANDOM_CONSUMER_SLEEP = (0.1, 0.5) # seconds

def consumerWorker (queue):
    """target worker for a consumer thread"""
    # TODO - loop forever using while True    
    for _ in range(ITEMS_TO_PRODUCE * NUMBER_OF_PRODUCERS // NUMBER_OF_CONSUMERS + 1): # loop enough times to consume all items 
    # TODO - call q.get() to pull an item out (this blocks automatically if queue is empty)
        item = queue.get()
    # TODO - otherwise "process" the item (e.g. just print it)
        if item is None: # check for sentinel value to know when to stop
            break
        print(f"CONS {threading.current_thread().name} consumed: {item}")
    # TODO - call q.task_done() after processing each item (marks item as handled)
        q.task_done()
    # TODO - add a random sleep using RANDOM_CONSUMER_SLEEP to simulate processing time
        time.sleep(random.uniform(*RANDOM_CONSUMER_SLEEP))
  
def producerWorker(queue):
    """target worker for a producer thread"""
    # TODO - loop ITEMS_TO_PRODUCE times
    for i in range(ITEMS_TO_PRODUCE):

    # TODO - generate an item (e.g. a random float or string)
        item = f"Producer {threading.current_thread().name} produced item {i}"
        print(f"PROD {threading.current_thread().name} produced: {item}")
    # TODO - call q.put(item) to add it to the queue
        queue.put(item)
    # TODO - add a random sleep using RANDOM_PRODUCER_SLEEP to simulate production time
        time.sleep(random.uniform(*RANDOM_PRODUCER_SLEEP))

if __name__ == "__main__":
    buffer = queue.Queue()

    # TODO - create and start NUMBER_OF_PRODUCERS producer threads
    #      - each thread targets producerWorker, passing buffer as the argument
    #      - store them in a list so you can join() them later
    producer_threads = []
    for i in range(NUMBER_OF_PRODUCERS):
        t = threading.Thread(target=producerWorker, args=(buffer,))
        t.start()
        producer_threads.append(t)
    
    # TODO - create and start NUMBER_OF_CONSUMERS consumer threads
    #      - each thread targets consumerWorker, passing buffer as the argument
    #      - make them daemon threads (so they die automatically if main exits)
    #      - store them in a list
    consumer_threads = []
    for i in range(NUMBER_OF_CONSUMERS):
        t = threading.Thread(target=consumerWorker, args=(buffer,), daemon=True)
        t.start()
        consumer_threads.append(t)

    #Wait for all producers to finish
    for t in producer_threads:
        t.join()