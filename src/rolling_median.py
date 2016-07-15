import sys
import json
import statistics
import networkx as nx
from datetime import datetime

def main(argv):

    # Build Graph
    # ------------------------
    #     input_filename       = './insight_testsuite/tests/test-2-0-readme/venmo_input/venmo-trans.txt'
    #     output_filename      = 'venmo_output/output.txt'
    
    input_filename       = str(argv[1])
    output_filename      = str(argv[2])
    output_file          = open(output_filename, 'w')
    max_time_window_secs = 60
    date_format          = '%Y-%m-%dT%H:%M:%SZ'


    venmo_graph = nx.Graph() # create empty network graph

    with open(output_filename, 'w') as output_file:
        with open(input_filename, 'r') as json_file:
            for line in json_file:
                
                data        = json.loads(line)
                curr_target = data['target']
                curr_actor  = data['actor']
                curr_time   = data['created_time']

                # Error check missing fields:
                #  If any fields are missing data,
                #  Then skip line
                if curr_target and curr_actor and curr_time:
                
                    # Convert date-string to datetime object
                    curr_time = datetime.strptime( curr_time
                                                 , date_format)

                    # Save the 1st maximum timestamp, TIME_MAX
                    if venmo_graph.number_of_edges() <= 0:
                        time_max = curr_time

                        
                    # Check if current transaction is out of order by time 
                    
                    if curr_time > time_max:  # transaction IS in order
                        time_max = curr_time

                        # Add edge to graph
                        venmo_graph.add_edge(  curr_actor
                                             , curr_target
                                             , time = curr_time)

                        # Prune edges that are beyond the time window
                        edge_list = venmo_graph.edges(data=True)

                        # actor = Maryann-Berry,     target = Maddie-Franklin,     created_time: 2016-04-07T03:34:58Z
                        for edge_foo in edge_list:
                            time_check = edge_foo[2]['time']
                            time_diff  = (curr_time - time_check)

                            if time_diff.total_seconds() > max_time_window_secs:
                                venmo_graph.remove_edge(edge_foo[0],edge_foo[1])
                                
                        # Delete any orphaned nodes
                        prune_orphaned_nodes(venmo_graph)


                    else:  # Current transaction out of order by time

                        # Check if the curr_time is within the 60-time-window
                        time_win_check = (time_max - curr_time).total_seconds() <= max_time_window_secs
                        if time_win_check:
                            
                            # Current transaction IS w/n the max time window
                            # so add edge to graph
                            venmo_graph.add_edge(  curr_actor
                                                 , curr_target
                                                 , time = curr_time)
                        else: 
                            # Current transaction IS NOT w/n the max time window
                            #  So do not add it to graph 
                            pass


                    # Calculate the median degree of the graph
                    median_degree = calculate_median(venmo_graph)
                    
                    # Write median to output file: OUTPUT.TXT
                    output_file.write('%1.2f\n' % median_degree)

                    # Feedback
                    # print_graph(venmo_graph)
                    # print('Median degrees: %1.2f\n' % median_degree)
                    ########




def prune_orphaned_nodes(nx_graph):
    """ Return a networkx graph in which 
        any nodes that aren't connected to other nodes 
        (i.e. nodes w/ degree less than 1) are deleted
    """ 

    # Search through graph for every node w/ degree
    unconnected_nodes = [node for node,deg in nx_graph.degree_iter() if deg<1 ]
    
    nx_graph.remove_nodes_from(unconnected_nodes)
    
    return nx_graph


def calculate_median(nx_graph):
    """ Return the middle value (ie. median degree) a networkx graph.
    
    """
    
    # create list of all degrees in graph
    list_degrees = list((nx_graph.degree()).values()) 
    
    # sort list of degrees for median in ascending order
    list_degrees.sort()
    
    # calculate median
    median_degrees = statistics.median(list_degrees)
    # print(list_degrees)  
    return median_degrees


def print_graph(nx_graph):
    edge_list = nx_graph.edges(data=True)
    for edge_foo in edge_list:
        print([ "actor:  "+ edge_foo[0]  \
              , "target: "+ edge_foo[1] \
              , "time:   "+ str(edge_foo[2]['time'])])
    return


    
if __name__ == "__main__":
    main(sys.argv)