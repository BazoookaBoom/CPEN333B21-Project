# Group #: B21
# Student names: Anna Bartl and Conor O'Neill
 
import threading
import queue
import time, random

# --- Global variable definitions --- #
NUMBER_OF_CONSUMERS: int = 5 # Number of consumers
NUMBER_OF_PRODUCERS: int = 4 # Number of producers 
TOTAL_ITEMS: int = 20           # Total number of items to be produced (must be >= NUMBER_OF_PRODUCERS)
RANDOM_PRODUCER_SLEEP: tuple[float, float] = (0.1, 0.5) # seconds for random sleep range for producers
RANDOM_CONSUMER_SLEEP: tuple[float, float] = (0.1, 0.5) # seconds for random sleep range for consumers

def consumerWorker (q): 
    """
        param q: the queue object from which to consume items

        target worker for a consumer thread
    """

    while True:
        item = q.get() # Consume item with a synchronize safe action that removes and returns the item
        
        if item is None: # Check none to know when to stop
            q.task_done() # Release the queue lock
            break
        print(f"{threading.current_thread().name} consumed: {item}")
        time.sleep(random.uniform(*RANDOM_CONSUMER_SLEEP)) # Random sleep time
        q.task_done() # Release the queue lock
  
def producerWorker(q): 
    """
        param q: the queue object to which to produce items
        param items_to_produce: the number of items this producer should produce

        target worker for a producer thread
    """

    def get_items_to_produce():
        """
            param: None

            returns: the number of items this producer should produce, 
            calculated based on the total items and index of the producer

            helper function to determine how many items this producer should produce
        """
        #Spread the total items to be produced as evenly as possible among the producers
        base_items = TOTAL_ITEMS // NUMBER_OF_PRODUCERS
        extra_items = TOTAL_ITEMS % NUMBER_OF_PRODUCERS #Extra items to distribute among the first few producers
        producer_index = int(threading.current_thread().name.split('-')[1]) # Extract index from thread name
        return base_items + (1 if producer_index < extra_items else 0) #Number of items to produce


    for i in range(get_items_to_produce()):

        item = f"P{i} Item {i + 1}" # Unique item name by producer and item index
        print(f"{threading.current_thread().name} produced: {item}")
        q.put(item) #Synchronize safe putting an item to the back of the queue 
        time.sleep(random.uniform(*RANDOM_PRODUCER_SLEEP)) #Random sleep time


if __name__ == "__main__":
    buffer = queue.Queue() #Main queue for synchronization between producers and consumers

    producer_threads = [] #List to keep track of producer threads for easy joining later

    for i in range(NUMBER_OF_PRODUCERS):
        t = threading.Thread(target=producerWorker, args=(buffer,), name=f"PROD-{i}")
        t.start()
        producer_threads.append(t) #Add the producer thread to the list of producer threads
    
    consumer_threads = []
    for i in range(NUMBER_OF_CONSUMERS):
        t = threading.Thread(target=consumerWorker, args=(buffer,),name=f"CONS-{i}")
        t.start()
        consumer_threads.append(t)

    #Wait for all producers to finish
    for t in producer_threads:
        t.join()

    #Once all producers are done, put None in the queue for each consumer to signal them to stop
    #Will stop each consumer using the break statement in the consumerWorker function when they consume None
    #Important for graceful shutdown of both the buffer and the consumer threads
    for _ in range(NUMBER_OF_CONSUMERS):
        buffer.put(None)
    print("All producers have finished. Waiting for consumers to finish...")
    
    buffer.join() # Wait until all items have been processed and all put() and task_done() calls are done
    print("All producers and consumers have finished.")