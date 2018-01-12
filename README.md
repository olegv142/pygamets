# pygamets

![](https://github.com/olegv142/pygamets/blob/master/demo.png)
![](https://github.com/olegv142/pygamets/blob/master/progress.png)
![](https://github.com/olegv142/pygamets/blob/master/plotter.png)
![](https://github.com/olegv142/pygamets/blob/master/log_view.png)

GUI micro-framework with touch screen support for [Pygame](http://www.pygame.org) frame-buffer applications.
Designed for building simple GUI in embedded applications with focus on multi-threading.

## What it does
The touch screen events seen in /dev/input/mouse has incorrect position information so the touch screen support in pygame
seems to be broken unless running under x-windows. We have implemented separate input events handler reading them from /dev/input/event
raw events pipe. It is installed in place of pygame.event.get routine so any pygame application reading events from there will be
able to work with touch screen flawlessly.

The existing touch screen calibration applications are available for x-windows only. We created our own calibration tool which
should be executed before using aforementioned event reading engine.

The event reading hook is quite convenient place for adding additional functionality to event loop based GUI applications.
We added 2 useful facilities there:
- timers for scheduling callbacks after some time interval in one shot or periodic mode
- jobs for scheduling actions that must be executed ASAP in the context of the event loop

We provided GUI base classes to serve as generic building blocks for applications as well as several ready to use
GUI elements such as buttons, labels, progress and battery charge indicators, graph plotter and log viewer.

The styles framework serves as a convenient way of setting various parameters in CSS-like manner. It separates
parameters storage from the code using them which leads to cleaner code and simplify visual appearance tuning.

The textual elements rely on the global text translation table for the sake of GUI localization.

The log viewer widget is collecting last log records using standard logging module. So the application
developer can get all necessary debugging information right on the screen without using remote terminal access to the target system.
The data plotter widget helps to visualize arbitrary data represented as array of (x,y) samples.

The demo application is provided as working example of building simple GUI in multi-threaded application.
To launch demo execute `python demo.py` or (on linux) `./demo.py`.

## Environment
Tested on Raspberry Pi zero W with Stretch lite installed equipped with 4inch 320×480
[LCD screen](https://www.waveshare.com/product/mini-pc/raspberry-pi/displays/4inch-rpi-lcd-a.htm).
Also works on windows without any modifications.

## Author

Oleg Volkov (olegv142@gmail.com)
