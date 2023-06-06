# import  win32com.client
# client = win32com.client.Dispatch('Graybox.Simulator') 

# # Perform the operation
# # value = client.ReadItemValue('', 'pocserversim.Instansw.1', 'IntegerValue.Integer')
# value = client.ReadItemValue('', 'Device2', 'Tag1')

# # Display results
# print('value: ', value)

from openopc2.da_client import OpcDaClient
from openopc2.config import OpenOpcConfig

config=OpenOpcConfig()
# self.OPC_HOST: str = 'localhost'
# self.OPC_SERVER: str = os.environ.get('OPC_SERVER', 'Matrikon.OPC.Simulation')
# self.OPC_CLIENT: str = 'OpenOPC'
# self.OPC_GATEWAY_HOST: str = os.environ.get('OPC_GATE_HOST', '192.168.0.115')
# self.OPC_GATEWAY_PORT: int = int(os.environ.get('OPC_GATE_PORT', 7766))
# self.OPC_CLASS: str = os.environ.get('OPC_CLASS', 'Graybox.OPC.DAWrapper')
# self.OPC_MODE: Literal["GATEWAY", "COM"] = os.environ.get('OPC_MODE', "gateway")
# self.OPC_TIMEOUT: int = os.environ.get('OPC_TIMEOUT', 1000)
# config.OPC_SERVER='Graybox.Simulator'
config.OPC_SERVER='NAPOPC.Svr'
config.OPC_MODE="COM"
client=OpcDaClient(config)
client.connect()
result=client.read('Tag1','Group')
print(result)
client.close()

pass



    # OPC connection
# from opc import OpenOPC
# opc=OpenOPC.client()
# b=opc.connect('opc.opcserversim.Instance.1')
# #opc.connect('Kepware.KEPServerEX.V5','localhost')


# print(opc.read( ('IntegerValue') ))

# opc.close()

# import sys
# sys.path.insert(0, "..")


# from opcua import Client


# if __name__ == "__main__":

#     # client = Client("opc.tcp://localhost:4840/freeopcua/server/")
#     client = Client("opc.opcserversim.Instance.1")
#     # client = Client("opc.tcp://admin@localhost:4840/freeopcua/server/") #connect using a user
#     try:
#         client.connect()

#         # Client has a few methods to get proxy to UA nodes that should always be in address space such as Root or Objects
#         root = client.get_root_node()
#         print("Objects node is: ", root)

#         # Node objects have methods to read and write node attributes as well as browse or populate address space
#         print("Children of root are: ", root.get_children())

#         # get a specific node knowing its node id
#         #var = client.get_node(ua.NodeId(1002, 2))
#         #var = client.get_node("ns=3;i=2002")
#         #print(var)
#         #var.get_data_value() # get value of node as a DataValue object
#         #var.get_value() # get value of node as a python builtin
#         #var.set_value(ua.Variant([23], ua.VariantType.Int64)) #set node value using explicit data type
#         #var.set_value(3.9) # set node value using implicit data type

#         # Now getting a variable node using its browse path
#         myvar = root.get_child(["0:Objects", "2:MyObject", "2:MyVariable"])
#         obj = root.get_child(["0:Objects", "2:MyObject"])
#         print("myvar is: ", myvar)
#         print("myobj is: ", obj)

#         # Stacked myvar access
#         # print("myvar is: ", root.get_children()[0].get_children()[1].get_variables()[0].get_value())

#     finally:
#         client.disconnect()