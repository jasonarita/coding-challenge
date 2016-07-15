import sys
import json 
import networkx as nx
from datetime import datetime

def main(argv):

    # Building the Venmo Graph
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
                data = json.loads(line)

                # Error check missing fields
                #  Skip line if any fields are missing


                # Convert date-string to datetime object
                data['created_time'] = datetime.strptime(  data['created_time'] \
                                                         , date_format)

                time_curr = data['created_time']

                # Save the first maximum timestamp
                if venmo_graph.number_of_edges() == 0:
                    time_max = time_curr        


                if time_curr > time_max:
                    time_max = time_curr

                    ########
                    # Add edge + time-info to graph
                    venmo_graph.add_edge(  data['actor'] \
                                         , data['target']\
                                         , time = data['created_time'])
                    ########

                    ########
                    # Prune

                    edge_list = venmo_graph.edges(data=True)

                    # actor = Maryann-Berry,     target = Maddie-Franklin,     created_time: 2016-04-07T03:34:58Z
                    time_curr = data['created_time']
                    for edge_foo in edge_list:
                        time_check = edge_foo[2]['time']
                        time_diff  = (time_curr - time_check)

                        if time_diff.total_seconds() > max_time_window_secs:
                            venmo_graph.remove_edge(edge_foo[0],edge_foo[1])
                    prune_unconnected_nodes(venmo_graph)
                    

                    ########
                else:
                    # Out of order

                    # if the curr_time is within the 60-time-window
                    time_diff = time_max - time_curr

                    if time_diff.total_seconds() <= max_time_window_secs:
                        ########
                        # Add edge + time-info to graph
                        venmo_graph.add_edge(  data['actor'] \
                                             , data['target']\
                                             , time = data['created_time'])
                        ########


                ########
                ## Output: Print median
                median_degree = calculate_median(venmo_graph)
                output_file.write('%1.2f\n' % median_degree)
                
                print_graph(venmo_graph)
                print('Median degrees: %1.2f\n' % median_degree)

                ########

def print_graph(nx_graph):
    edge_list = nx_graph.edges(data=True)
    for edge_foo in edge_list:
        print([ "actor:  "+ edge_foo[0]  \
              , "target: "+ edge_foo[1] \
              , "time:   "+ str(edge_foo[2]['time'])])
    return


def prune_unconnected_nodes(nx_graph):
    unconnected_nodes =[n for n,d in nx_graph.degree_iter() if d<1 ]
    nx_graph.remove_nodes_from(unconnected_nodes)
    return nx_graph


def calculate_median(nx_graph):
    import statistics
    list_degrees = list((nx_graph.degree()).values()) # list of degrees
    list_degrees.sort() # sort the list of degrees
    median_degrees = statistics.median(list_degrees)
    print(list_degrees)
    return median_degrees

    
if __name__ == "__main__":
    main(sys.argv)