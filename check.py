import pandas as pd
mgmt = pd.read_excel(r"c:\Users\Administrator\Desktop\线索\招商线索管理表.xlsx", sheet_name='线索明细')
print("线索有效性唯一值:", mgmt['线索有效性'].value_counts().to_dict())
