import os
from SagaApp.Container import Container
from SagaApp.Frame import Frame

framedict= {}
for cont in os.listdir('Container'):
    container = Container.LoadContainerFromYaml(os.path.join('Container',cont, 'containerstate.yaml'))
    print(container.filestomonitor)
    print(container.refframe)

    framedict[cont]=Frame.loadFramefromYaml(container.refframe, container.filestomonitor, '')
    # framedict[cont].writeoutFrameYaml(os.path.join('Container', cont, 'Main/Rev1.yaml'))

# framedict['ContainerC'].writeoutFrameYaml(os.path.join('Container','ContainerC', 'test.yaml'))