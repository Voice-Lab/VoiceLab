from Voicelab.pipeline.Node import Node

###################################################################################################
# Pipeline:
#
### The main process pipeline. Responsible for orchestrating a sequence of discrete tasks, as can
### be defined as an acyclic directed graph. Each node runs a singular operation then passes/flows
### it's results downstream onto the next. Data is collected within the node's themselves until all
### it's parents upstream have finished their own respective tasks. Some nodes can produce subsets
### of their own data, indicating that all nodes downstream from it should be run that many more
### times.
###################################################################################################


class Pipeline:
    """Proccess flow pipeline. Oversees/orchestrates the running of a directed
    graph of arbitrary tasks
    """

    # TODO: Validation step for initialization arguments
    def __init__(self, nodes=None, global_vars=None, roots=None):
        """Pipeline initialization. Optionally can initialize with nodes,
        global_vars, roots

        Args:
            nodes:
            global_vars:
            roots:
        """
        # tree of nodes, storing return value names and its subsequent children
        self.nodes = nodes if nodes is not None else {}
        # Nodes with no parents. Updated as needed when new tasks are added, reduces need to search the whole graph
        self.roots = roots if roots is not None else {}
        # Variables that are optionally shared accross nodes and batches/runs/passes
        self.global_vars = global_vars if global_vars is not None else {}
        #
        self.event_callbacks = {}
        #
        self.results = {}
        # Naive listener list for listening for run time updates
        self.listeners = []
        self.progress_start = 0
        self.progress_current = 0
        self.progress_end = 0

    ################################################################################################
    # Pipeline: Add
    # + node: the node that will be added to the pipeline
    ################################################################################################
    def add(self, node):
        """Add a new node to the pipeline

        Args:
            node:
        """

        self.nodes[node] = []
        self.roots[node] = node
        if len(node.event_callbacks) > 0:
            print(node.event_callbacks)
            for event_id in node.event_callbacks:
                event_callback = node.event_callbacks[event_id]
                if event_id not in self.event_callbacks:
                    self.event_callbacks[event_id] = []
                self.event_callbacks[event_id].append(event_callback)

    ################################################################################################
    # Pipeline: Connect
    # + parent: the node that will be upstream from the child
    # + child: the node that will be downstream from the parent
    # + parent_terminal: On what outgoing parameter is the parent node connecting
    # + child_terminal: On what incoming parameter is the child node connecting
    ################################################################################################
    def connect(self, parent=None, child=None):
        """Form a relationship between two nodes, from the parent data will be
        passed to child

        Args:
            parent:
            child:
        """

        parent_node, parent_terminal = parent
        child_node, child_terminal = child
        child_node.ready[child_terminal] = False
        child_node.default_ready[child_terminal] = False

        if parent_node not in self.nodes:
            self.nodes[parent_node] = []

        # if parent_terminal not in self.nodes[parent_node]:
        #     self.nodes[parent_node][parent_terminal] = []

        # self.nodes[parent_node][parent_terminal].append([child_node, child_terminal])
        self.nodes[parent_node].append((parent_terminal, child_terminal, child_node))

        if child_node in self.roots:
            self.roots.pop(child_node)

        return self.nodes[parent_node][-1]

    ###############################################################################################
    # Pipeline: Start:
    ###############################################################################################
    def start(self):
        """Initializes all the nodes and starts the first pass"""
        print(self.nodes)

        print("############################ Starting ############################")
        results = [{}]

        # runs each node's start function once at the beginning
        for node in self.nodes:
            batch_size = node.start()
            # estimate the run progress based on the size of the batch and how many nodes will run
            if batch_size is not None:
                self.initialize_progress(batch_size, len(self.nodes))

        if len(self.roots) > 0:
            results = self.run_pass(True, results=results)

        for node in self.nodes:
            results = node.end(results)

        return results

    ###############################################################################################
    # Pipeline: Run_Pass
    # + done: Indicates if more passes over the data need to be done
    #
    ### Recursively run passes over the pipeline until each node has processed all of its data.
    ### Since a pipeline can have input nodes that iteratively return parts of their data (batches)
    ### multiple runnings of these nodes must be performed (a pass). Each pass over the data runs
    ### all of the nodes from the start until they all report that they are done.
    ###############################################################################################

    def run_pass(self, done, results=None, i_pass=0):
        """Recursively runs all of the roots nodes until they report they are
        done

        Args:
            done:
            results:
            i_pass:
        """

        for root in self.roots:
            _done = self.run_node(root, results, i_pass)
            done = done and _done

        if not done:
            i_pass = i_pass + 1
            self.run_pass(True, results, i_pass)

        return results

    ################################################################################################
    # Pipeline: Process Node
    # + node_id: Unique identifier for retrieving the node to be processed
    #
    ### Recursive function to traverse the sequence of nodes (the graph) visiting each node once and
    ### running it's accompanied process function.
    ################################################################################################

    def run_node(self, node, results=None, i_pass=0):
        """Called on each node, and recursively on each child node

        Args:
            node:
            results:
            i_pass:
        """
        if results is None:
            results = [{}]
        if len(results) <= i_pass:
            results.append({})

        if all(node.ready.values()):

            node.global_vars = self.global_vars
            results[i_pass][node] = node.process()
            self.global_vars = node.global_vars

            # increment the progress by this node
            self.update_progress(node)

            if len(node.events_fired) > 0:
                for event_id in node.events_fired:
                    event_data = node.events_fired[event_id]
                    self.resolve_event(event_id, event_data)
                node.events_fired = {}

            if node in self.nodes:  # if this is a parent of another node
                for parent_terminal, child_terminal, child in self.nodes[node]:
                    if parent_terminal in results[i_pass][node]:
                        child.args[child_terminal] = results[i_pass][node][
                            parent_terminal
                        ]
                        child.ready[child_terminal] = True
                        self.run_node(child, results, i_pass)
            node.reset()

        return node.done

    def resolve_event(self, event_id, event_data):
        """
        Args:
            event_id:
            event_data:
        """
        if event_id in self.event_callbacks:
            for callback in self.event_callbacks[event_id]:
                callback(event_id, event_data)

    ###############################################################################################
    # update_progress: Naive method of tracking progress. Simply tracks progress as a product of
    # the number of runs times the number of functions
    ###############################################################################################
    def initialize_progress(self, m_runs, n_functions):
        """
        Args:
            m_runs:
            n_functions:
        """
        self.progress_start = 0
        self.progress_current = 0
        self.progress_end = m_runs * n_functions

    ###############################################################################################
    # update_progress: Naive method of tracking progress. Simply increments our progress by 1 and
    # tells our listener functions using the callback methods they provided
    ###############################################################################################
    def update_progress(self, node):
        """
        Args:
            node:
        """
        self.progress_current = self.progress_current + 1
        for listener in self.listeners:
            listener(
                node, self.progress_start, self.progress_current, self.progress_end
            )

    ###############################################################################################
    # listen: Naive method of listening for progress. Simply registers a callback
    ###############################################################################################
    def listen(self, callback):
        """
        Args:
            callback:
        """
        self.listeners.append(callback)

    ###############################################################################################
    # reset_progress: Naive method of reseting the progress. progress start cannot be anything but 0 for now
    ###############################################################################################
    def reset_progress(self):
        self.progress_current = self.progress_start
