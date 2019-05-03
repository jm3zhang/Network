import math
import random
import time

def arrivalTimeGenerator(arrival_rate):
	return -math.log(1.0 - random.random())/arrival_rate

# find the corresponding index of node with the minimum arrival time 
def sender_detector(node_array):
    min_a = min(node_array)
    node_index = node_array.index(min_a)
    return node_index
    
#find out the nodes that will collide with the sender
def collision_detector(node_array, sender_index, T_prop):
    collided_nodes = []
    for i in range(len(node_array)):
        if i!= sender_index:
            if node_array[i] <= abs(sender_index -i) * T_prop + node_array[sender_index]:
                collided_nodes.append(i)

    if len(collided_nodes) != 0:
        collided_nodes.append(sender_index)
        
    return collided_nodes

#handle busy in non-persistent mode
def handle_busy_non_persistent(busy_counter, arrivalTime_NodesInLAN, sender_index, T_prop, T_trans, A, stacked_packet_counter, bit_time):
    for i in range(len(busy_counter)):
        T_full_prop = arrivalTime_NodesInLAN[sender_index] + abs(i-sender_index)*T_prop
        T_full = T_full_prop + T_trans
        if arrivalTime_NodesInLAN[i] > T_full_prop and arrivalTime_NodesInLAN[i] < T_full:
            
            busy_counter[i] += 1
            pushed_time = arrivalTime_NodesInLAN[i]
            T_wait = generate_Twait(busy_counter[i], bit_time)
            T_full_non_persistent =  arrivalTime_NodesInLAN[i] + T_wait
            while pushed_time < T_full_non_persistent:
                
                pushed_time += arrivalTimeGenerator(A)
                if pushed_time < T_full_non_persistent:
                    stacked_packet_counter[i] += 1
            
            arrivalTime_NodesInLAN[i] = T_full_non_persistent
        else:
            busy_counter[i] = 0 
    return arrivalTime_NodesInLAN, stacked_packet_counter, busy_counter

    
#handle busy in persistent mode
def handle_busy_persistent(node_array, sender_index, T_prop, T_trans, A, stacked_packet_counter):
    for i in range(len(node_array)):

        T_full_prop = node_array[sender_index] + abs(i-sender_index)*T_prop
        T_full = T_full_prop + T_trans
        if node_array[i] > T_full_prop and node_array[i] <  T_full:
            
            pushed_time = node_array[i]
            while pushed_time < T_full:
                
                pushed_time += arrivalTimeGenerator(A)
                if pushed_time < T_full:
                    stacked_packet_counter[i] += 1
            
            node_array[i] = T_full
    return node_array, stacked_packet_counter

#generate Twait time for exponential backoff
def generate_Twait(i, bit_time):
    return random.randint(0, 2 ** i - 1) * 512 * bit_time

#exponential backoff for the collided nodes
def handle_collision(collided_nodes, nodes_collision_counter, arrivalTime_NodesInLAN, bit_time, A, sender_index, T_trans, T_prop,  stacked_packet_counter):
    
    for i in  collided_nodes:
        nodes_collision_counter[i] += 1
        if nodes_collision_counter[i] < 10:
           
            T_wait = generate_Twait(nodes_collision_counter[i], bit_time)
                
            pushed_time = 0
            while pushed_time < T_wait:
                
                pushed_time += arrivalTimeGenerator(A)
                if pushed_time < T_wait:
                    # print("pushed time:"+str(pushed_time))
                    stacked_packet_counter[i] += 1
            arrivalTime_NodesInLAN[i] += T_wait
            # print(arrivalTime_NodesInLAN[i])
        else:
           
            nodes_collision_counter[i] = 0
            if stacked_packet_counter[i] == 0:
                arrivalTime_NodesInLAN[i] += arrivalTimeGenerator(A)
            else:    
                stacked_packet_counter[i] -= 1
            
    return nodes_collision_counter, arrivalTime_NodesInLAN

def CSMA_simulator(N, A, R, L, D, S, T_sim, persistent):
    # N: The number of nodes/computers connected to the LAN (variable).
    # A: Average packet arrival rate (packets/second) (variable). Data packets arrive at the MAC layer following a Poisson process at all nodes.
    # R: The speed of the LAN/channel/bus (fixed).
    # L: Packet length (fixed).
    # D: Distance between adjacent nodes on the bus/channel.
    # S: Propagation speed.
    # T_sim: time stamp of the simulation

    arrivalTime_NodesInLAN = []
    T_prop = D/S
    # T_prop = 0.001
    bit_time = 1/R
    T_trans = L/R
    successfully_transmitted = 0
    transmitted = 0
    
    # generate a list, each element is the arrival time of the first packets in each node. We do not generate all of the packets for each node at the beginning.
    
    for _ in range(N):
        new_arrival_time = arrivalTimeGenerator(A)
        arrivalTime_NodesInLAN.append(new_arrival_time)

  
    stacked_packet_counter = [1] * N
    nodes_collision_counter = [0] * N
    busy_counter = [0] * N
    
    allTransmittionDone = 0
    

    while allTransmittionDone == 0:
        
        #detect sender
        sender_index = sender_detector(arrivalTime_NodesInLAN) 
        
        send_time = arrivalTime_NodesInLAN[sender_index]
        # if send_time%20 < 0.1:
        #     print(send_time)
        if send_time > T_sim:
            allTransmittionDone = 1
            continue
        
        # get the collided nodes
        collided_nodes = collision_detector(arrivalTime_NodesInLAN, sender_index, T_prop)
        
        #handle the busy packets
        if persistent:
            arrivalTime_NodesInLAN, stacked_packet_counter = handle_busy_persistent(arrivalTime_NodesInLAN, sender_index, T_prop, T_trans, A, stacked_packet_counter)
        else:
            arrivalTime_NodesInLAN, stacked_packet_counter, busy_counter = handle_busy_non_persistent(busy_counter,arrivalTime_NodesInLAN, sender_index, T_prop, T_trans, A, stacked_packet_counter, bit_time)
       
        #check whether the packet is transmitted successfully
        
        if  len(collided_nodes) != 0:
            for node in collided_nodes:
                transmitted += stacked_packet_counter[node]
            
            nodes_collision_counter,arrivalTime_NodesInLAN = handle_collision(collided_nodes, nodes_collision_counter, arrivalTime_NodesInLAN, bit_time, A, sender_index, T_trans, T_prop,stacked_packet_counter)
            
        else:

            transmitted += stacked_packet_counter[sender_index]
            successfully_transmitted += stacked_packet_counter[sender_index]
            stacked_packet_counter[sender_index] = 1
            nodes_collision_counter[sender_index] = 0
            arrivalTime_NodesInLAN[sender_index] += arrivalTimeGenerator(A)
       
    print("transmitted:"+str(transmitted))
    print("successfully transmitted:"+ str(successfully_transmitted))
    print("efficiency:"+str(successfully_transmitted/transmitted))
    print('throughput:' + str(successfully_transmitted * L / T_sim / 10 ** 6))
    print("trans:"+ str(T_trans))
    print("prop:"+ str(T_prop))
    

    return True

N = 100
A = 5
R = 1000000
L = 1500
D = 10
S = 2*100000000
T_sim = 1000

print("here is persistent")
for A in [7, 10,20]:
    print("we have A:"+str(A))
    for N in [20,40,60,80,100]:
        print("we have a new N:"+str(N))
        CSMA_simulator(N, A, R, L, D, S, T_sim, True)

print("here is non-persistent")
for A in [7, 10,20]:
    print("we have A:"+str(A))
    for N in [20,40,60,80,100]:
        print("we have a new N:"+str(N))
        CSMA_simulator(N, A, R, L, D, S, T_sim, False)
        