import importlib

# Task Factories know about all types of tasks that can be created and creates the appropriate instance when called
# Abstracts the creation logic, and all of the library importing away from the user

###################################################################################################
# NodeFactory: Abstracts the creation logic for new nodes
# Singleton Factory pattern, so no instantiation needed
###################################################################################################
class NodeFactory:
    """Create new nodes based on a type id"""

    registered_nodes = {}

    ###############################################################################################
    # Register Node (Class Method) : Registers a new node under a specified name/id
    ###############################################################################################
    @classmethod
    def register_node(cls, type_id, type_class):
        """register a new node into the factory

        Args:
            type_id:
            type_class:
        """
        cls.registered_nodes[type_id] = type_class

    ###############################################################################################
    # Create Node (Class Method) : Returns a new instance of the specifed node
    ###############################################################################################
    @classmethod
    def create_node(cls, node_id, type_id):
        """create a new node based on type id

        Args:
            node_id:
            type_id:
        """
        node = cls.registered_nodes[type_id](node_id)
        return node

    ###############################################################################################
    # Import Node (Class Method) : Imports the python class associated with a node and register it
    ###############################################################################################
    @classmethod
    def import_node(cls, type_id, toolkit_id, class_name):
        """import the class for a new node and register it

        Args:
            type_id:
            toolkit_id:
            class_name:
        """
        if type_id not in cls.registered_nodes:
            module_name = "toolkits." + toolkit_id + "." + class_name
            module = importlib.import_module(module_name)
            cls.register_node(type_id, getattr(module, class_name))

        return cls.registered_nodes[type_id]
