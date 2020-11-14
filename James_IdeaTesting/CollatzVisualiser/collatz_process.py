import numpy as np
import time

# Code for the basic finding of collatz paths to 1
mem = {}

def collatz(val, max_step=10000):
    
    collatz_list = [val]
    step = 0
    current_val, new_val = val, 0

    while current_val > 1 and step < max_step:

        # Pull from memory if possible 
        if current_val in mem.keys():
            new_val = mem[current_val]
        
        # Update val by conjecture rules
        else:
            if current_val % 2 == 0:
                new_val = current_val / 2
            else:
                new_val = (3 * current_val) + 1
            
            # Store this to memory for speed!
            mem[current_val] = new_val

        # Add to list and update step
        current_val = new_val
        collatz_list.append(int(current_val))
        step += 1

    return(collatz_list)

def repeated_random_collatz(n, min_val=1, max_val=100000):
    multi_collatz = []
    for start_val in np.random.randint(min_val, max_val, size=(1, n))[0]:
        collatz_out = collatz(start_val)
        multi_collatz.append(collatz_out)

    return(multi_collatz)

start = time.time()
single_out = collatz(20)
print(single_out)
print(time.time()-start)

out = repeated_random_collatz(10)
