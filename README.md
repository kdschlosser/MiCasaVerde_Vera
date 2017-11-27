MiCasaVerde_Vera


Here is the quick and dirty. I will be providing better docs in the near future.

    from micasaverde_vera import Vera

If you have UPNP enabled on the Vera and want to try auto discovery.
This takes longer then directly entering the IP address.

    vera = Vera()

If you want to supply the IP address.

    vera = Vera('192.168.1.1')

The initial running of the library takes a while. the length of time all depends on how many
plugins and devices are installed. This is due to the dynamic nature of this API. It builds all
methods, properties and attributes from information gotten form the Vera. It allows for setting
any of the variables in the Vera (provided the Vera allows you to). It also exposes some hidden
functions/methods.

dir() is your best friend. I have it supply an altered output of information that lists off all
available methods, properties and attributes that a specific component supports. Reading the
generated code files can also help some. But not all of the methods, properties and attributes
may be supported. This is why it is best to use dir()

Devices can be retrieved one of the 3 following ways.

    device = vera.get_device(10)
    device = vera.get_device('10')
    device = vera.get_device('Some Device Name')

This same mechanism works for scenes, rooms, plugins and a few others.
To get scenes you would use.

    vera.get_scene()

for rooms.

    vera.get_room()

and so on and so forth

Say you want to change the name of a room

    room = vera.get_room('Media')
    room.name = 'Dining Room'

If you want to have real time updates to the information stored in the Vera
You will have to start the polling loop.

    vera.start_polling(float(seconds))

This will update the information to match what is stored on the Vera.
The updating process speed is as fast as you set the interval to. You have
to remember the Vera is not exactly what I would call "fast". So keep that
in mind when setting a low interval. The lower the number the faster the
library will ask for the information. and if you have a really burdened Vera
to start off with this is going to make it really really really slow if
you have the number set to low.

The biggest purpose for this library/API is to be able to offload some of
that burden from the Vera and also extend it's ability to control devices
that it would normally not be able to.

I changed the event system to make it far easier to use. the old way has
been completely removed.

the following will register for an event. this specific example is if you
do not know the device number but you know the device name. This will trigger
an event if the Status variable changes

    def callback(event):
        print event.name

    device = vera.get_device('My device')
    registered_event = vera.bind('Device.{0}.Status.Changed'.format(device.id), callback)

if you know the device number

    registered_event = vera.bind('Device.2.Status.Changed', callback)

if you want to register for an event for all devices where a specific variable changes
in this example it will trigger an event for any dimmer switch that changes value

    registered_event = vera.bind('Device.*.loadLevelStatus.Changed', callback)

if you need to unbind from an event

    registered_event.unbind()

a good way for you to get to learn the events would be

    def callback(event):
        print event.event

    vera.bind('*', callback)

If you are using events from the Vera to cause other things to take place
(Scenes Hint Hint) you need to create a never ending loop at the end of your script.

    while True:
        pass













