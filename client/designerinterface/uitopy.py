from PyQt5 import uic


designer_interfaces_to_compile = ['designerchatinterface', 'designerlogininterface']

for interface in designer_interfaces_to_compile:
    with open(f'client/designerinterface/{interface}.py', 'w') as interfacepy:
        uic.compileUi(f'client/designerinterface/{interface}.ui', interfacepy)

