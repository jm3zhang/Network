import math
import random
import time
from itertools import chain
from numpy import arange

def exponentialRandom(generatedParameter):
	return -math.log(1.0 - random.random())/generatedParameter

#calculate lambda
def mylambda(rho, l, c):
    return rho*c/l


#binary search used in MM1K
def binarySearch(arr, l, r, x):
    if arr[r][1] < x:
        return r
    while r - l > 1:
        midpoint = (l + r) // 2 
        if arr[midpoint][1] < x:
            l = midpoint
        else:
            r = midpoint   
    return str(r)


#generate arrival event
def generate_arrival(T, lamb):
    l = []
    arrival = 0 
    while True:
        a = exponentialRandom(lamb)
        arrival += a
        if arrival < T:
            l.append(arrival)
        else:
            break
    return l

# generate service time
def generate_service(L):
    l = []
    for _ in range(0, L):
        a = exponentialRandom(1/2000)
        l.append(a/1000000)
    return l

#generate departure events for mm1 only
def generate_departure(ari, ser):
    l = []
    sortedl = sorted(ari)
    last_departure = 0
    for i in range(0, len(ari)-1):    
        if sortedl[i] > last_departure:
            dep = sortedl[i]+ ser[i]
            # print(sortedl)
        else:
            dep = last_departure +ser[i]
        last_departure = dep
        l.append(last_departure)
        # print(last_departure)
    
    return l

#generate observer events 
def generate_observer(L):
    l = []
    for _ in range(L):
        obs = random.uniform(0, 1000)
        l.append(obs)
    return l

#insert arrival events, departure events and observer events into DES for MM1
def des_initization(ari, dep, obs):
    des = []
    for i in ari:
        des.append([0, i])
    for i in dep:
        des.append([1, i])
    for i in obs:
        des.append([2, i])
    return des

#insert arrival and observer into DES for MM1K
def mm1k_des_initialization(ari, obs):
    des = []
    for i in ari:
        des.append([0, i])
    for i in obs:
        des.append([2, i])
    return des

#go through the MM1 DES and calculate E[N] and pidle
def mm1_queue(sorted_queue, ob_length):
    queue = 0
    total_obs_queue = 0
    idle = 0
    
    for event in sorted_queue:
        #0 is arrival
        if event[0] == 0:
            queue += 1
        #1 is departure
        if event[0] == 1:
            queue -= 1
        #2 is observer
        if event[0] == 2:
            total_obs_queue += queue
            if queue == 0:
                idle += 1
        
    avg_time_queue = total_obs_queue/ob_length
    p_idle = idle/ob_length
    
    return avg_time_queue, p_idle

def MM1_simulator(T, rho, L, C):
    
    arievent = generate_arrival(T, mylambda(rho, L, C))
    
    number_of_arievent = len(arievent)
    service_time = generate_service(number_of_arievent)
    departure = generate_departure(arievent, service_time)
    observer = generate_observer(5*number_of_arievent)
    des_init = des_initization(arievent, departure, observer)
    sort_des_init = sorted(des_init, key = lambda x:(x[1]))
    avg_time_queue, p_idle = mm1_queue(sort_des_init, len(observer))
    result_pair = [avg_time_queue, p_idle]
    return result_pair

def MM1K_simulator(T, rho, L, C, k):
    #initialize the counter
    event_in_buffer,Narrival,Ndeparture,Nidle,Ndrop,Nobserver = 0,0,0,0,0,0
    arievent = generate_arrival(T, mylambda(rho, L, C))
    number_of_arievent = len(arievent)
    observer = generate_observer(5*number_of_arievent)
    #put arrival and observer into DES 
    sort_des_init = mm1k_des_initialization(arievent, observer)
    sort_des_init.sort(key = lambda x:(x[1]))
    total_obs_queue = 0
    start = time.time()
    leng = len(sort_des_init)
    #go through the event in DES 
    departure_list = {}
    for i in range(0, leng):
        event = sort_des_init[i]
        #check whether there are events depart the buffer between current event and last event 
        if str(i) in departure_list:
            stri = str(i)
            c = departure_list[stri]
            Ndeparture += c
            event_in_buffer = event_in_buffer - c
        #for arrival events, do the following:
        if event[0] == 0:
            Narrival += 1
            if event_in_buffer == k:
                Ndrop += 1
            else:
                service_time= exponentialRandom(1/2000)/1000000
                
                if event_in_buffer == 0:
                    departure_time = service_time + event[1]
                else: 
                    departure_time = service_time + last_departure
                last_departure = departure_time
                event_in_buffer = event_in_buffer + 1
                loc = binarySearch(sort_des_init, 0, len(sort_des_init)-1, last_departure)
                
                if loc in departure_list:
                    departure_list[loc] += 1
                else:
                    departure_list[loc] = 1 
        #for observer events, do the following:
        else:
            Nobserver += 1
            total_obs_queue = total_obs_queue + event_in_buffer
            if event_in_buffer == 0:
                Nidle += 1
        
   
        # del sort_des_init[0]
    end = time.time()
    print("time:"+str(end - start))
    print("arrival:"+str(Narrival), "departure:" + str(Ndeparture), "observer:" + str(Nobserver), "idle:" + str(Nidle), "drop:"+ str(Ndrop))
    print("total queue:"+ str(total_obs_queue))
    En = total_obs_queue/Nobserver
    Pi = Nidle/Nobserver*100
    Ploss = Ndrop/Narrival*100
   
    return En, Pi, Ploss
            
            

                


def main():
    T = 2000
    rho = 0.35
    L = 2000
    C = 1000000
    

    #question 1:
    q1list = []
    for _ in range(0, 1000): 
        q1list.append(exponentialRandom(75))
    mean = sum(q1list)/len(q1list)
    lenofq1 = len(q1list)
    variance = sum((mean - x) ** 2 for x in q1list) / lenofq1
    print("question 1:")
    print("mean:" + str(mean))
    print("variance:" + str(variance))
    

    #question2:
    arievent = generate_arrival(T, mylambda(rho, L, C))
    number_of_arievent = len(arievent)
    service_time = generate_service(number_of_arievent)
    departure = generate_departure(arievent, service_time)
    observer = generate_observer(5*number_of_arievent)
    des_init = des_initization(arievent, departure, observer)
    sort_des_init = sorted(des_init, key = lambda x:(x[1]))
    avg_time_queue, p_idle = mm1_queue(sort_des_init, len(observer))
    # print(len(arievent) + len(departure) + len(observer))
    

    #question3:
    print("question 3:")

    rho_list = [0.25, 0.35,0.45,0.55,0.65,0.75,0.85,0.95]
    for x in rho_list:
        result_pair = MM1_simulator(T, x, L, C)
        print("result for"+str(x)+":")
        print(str(result_pair))
        print("\n")
    
    

    #question4:
    print("question 4:")
    q3_result_pair = MM1_simulator(T, 1.2, L, C)
    print("The average number of packets in the queue: " + str(q3_result_pair[0]))
    print("The proportion of time the system is idle: " + str(q3_result_pair[1] * 100) + "%")

    #Question6: 
    print("question 6:")
    t_start = time.time()
    for rho in arange(0.4,1.6,0.1):
    # for rho in chain(arange(0.4,2.1,0.1), arange(2.2,5.2, 0.2), arange(5.4, 10, 0.4)):
        print("start simulation for " + str(rho))
        en,a,b = MM1K_simulator(T, rho, L, C, 50)
        print("en = " + str(en))
        print("Pi = " + str(a))
        print("Pl = " + str(b))
    t_end = time.time()
    print("total time:" + str(t_end - t_start))  
   
if __name__ == '__main__':
    main()