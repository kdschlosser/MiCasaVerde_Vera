MiCasaVerde_Vera


This is a simple code example with a console to enter python code into. You will need to change the IP_ADDRESS to match the
IP of your Vera. if you set the IP_ADDRESS variable to "" it will attempt a discovery of the Vera (provided you have upnp turned on). This process does take a bit to complete the Vera is not exactly in the road runner department. 

    IP_ADDRESS = '192.168.1.2'
    DEVICE_NUMBER = None
    SHOW_ALL_EVENTS = True
    
    import micasaverde_vera
    
    
    def test_callback(event):
        if SHOW_ALL_EVENTS:
            print event.event
    
        split_event = event.event.split('.')
    
        def check_event():
            if split_event[-1] == 'changed':
                print
                print '--------------------------------------------'
                print event.event
                attr_name = split_event[-2:][0]
                try:
                    print event.name
                except AttributeError:
                    print 'NO NAME'
                print attr_name, '=', getattr(event, attr_name)
                print'--------------------------------------------'
                print
    
        if split_event[0] == 'devices':
            if split_event[1] == str(DEVICE_NUMBER):
                check_event()
    
        elif split_event[0] == 'rooms':
            check_event()
    
    vera = micasaverde_vera.connect(IP_ADDRESS)
    event_handler = vera.bind('*', test_callback)
    vera.start_polling(0.2)
    
    while True:
        command = [
            raw_input('key in commands here. the last line must be RUN\n\n')
        ]
        while command[-1] != 'RUN' and not command[-1].endswith('RUN'):
            command += [raw_input('')]
        command = '\n'.join(command)[:-3]
    
        try:
            exec command
        except:
            import traceback
            traceback.print_exc()

in the console if you want to get a printout of all of the device names for example

    for device in vera.devices:
        print device.name
        
 
 or say you want a prinout of what devices are in what rooms.
 
     for room in vera.rooms:
         print room.name
         for device in room:
             print '   ', device.name
             
             
  how about get a list of devices a plugin has installed
  
      for plugin in vera.installed_plugins:
          print plugin.name
          for device in plugin:
              print '   ', device.name
              
              
             
The best way to go about identifying any vera objects is by it's ID, these id's never get reissued and are unique to an object. You are able to access a device/room/plugin by it's id just as you would a list index. It does not matter if the numbers are not in sequence. You are also able to access using the device name like you would a dictionary.

There is a single convience method that allows for attrubite access to a room/device from the vera object. No unicode and the attribute representation of the room and device are all lowercase with any spaces replaces with an underscore. no numbers or special characters.

if i want to access room Living Room and the device Overhead Light

    vera.living_room.overhead_light
    
    












