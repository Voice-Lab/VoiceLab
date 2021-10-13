import json
from Voicelab.pipeline.NodeFactory import NodeFactory

NODZ_SAVE_LOCATION = "./pipeline/saves/sample.json"

##################################################################################################
# NodzInterface: Compartmentalizes the importing of a save file from the nodz library. Singleton
##################################################################################################
class NodzInterface:

    ###############################################################################################
    # Load (static): loads a well formatted json save from nodz and returns an array of nodes and
    # the connections
    ###############################################################################################
    @staticmethod
    def load(file_location):

        """
        Args:
            file_location:
        """
        nodes_mapping = {}
        nodes = []
        connections = []
        global_vars = {}

        with open(file_location, "r") as f:
            data = json.load(f)

            if "NODES" in data:
                for node_id in data["NODES"]:
                    node = data["NODES"][node_id]
                    class_name = node["file"].split(".")[
                        0
                    ]  # extract the name of the class stored here as XXXX.py
                    NodeFactory.import_node(
                        node["type"], node["toolkit"], class_name
                    )  # uses the Nodefactory to do the import logic, this also registers it with the factory for creating new versions
                    node_instance = NodeFactory.create_node(
                        node_id, node["type"]
                    )  # Create a new instance of this node
                    node_instance.args = {
                        **node["variables"]
                    }  # Copies the variables into the node as default arguments/configurations
                    nodes.append(
                        [node_id, node_instance]
                    )  # Compact the id and instance for access later
                    nodes_mapping[
                        node_id
                    ] = (
                        node_instance
                    )  # we use a mapping of id to instance for use parsing connections later

            if "CONNECTIONS" in data:
                for connection in data["CONNECTIONS"]:
                    parent_id, parent_terminal = connection[0].split(
                        "."
                    )  # Stored in json as id.terminal
                    child_id, child_terminal = connection[1].split(".")
                    parent = nodes_mapping[parent_id]
                    child = nodes_mapping[child_id]
                    connections.append(
                        [(parent, parent_terminal), (child, child_terminal)]
                    )  # stores the nodes and terminals all together

            # TODO: parse the global variables contained in nodz
            if "GLOBALS" in data:
                for global_var in data["GLOBALS"]:
                    print(global_var)

            return nodes, connections, global_vars
