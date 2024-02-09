from gathercore.databus.databus import DataBus
from gathercore.models import SourceData


    
if __name__ == '__main__':
    
    d=DataBus()
    a=d.add_data_holder(SourceData)
    d.set_data_holder(a, SourceData(id=11,))
    print(d.get_data_holder(a))