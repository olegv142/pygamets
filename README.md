# pygame-ts

GUI micro-framework with touch screen support for [Pygame](http://www.pygame.org) frame-buffer applications.
Designed for building simple GUI in embedded applications with focus on multi-threading.

## What it does
The touch screen events seen in /dev/mouse has incorrect position information so the touch screen support in pygame
seems to be broken unless running under x-windows. We have implemented separate input events handler reading them from /dev/input
raw events pipe. It is installed in place of pygame.event.get routine so any pygame application reading events from there will be
able to work with touch screen flawlessly.

The existing touch screen calibration applications are available for x-windows only. We created our own calibration tool which
should be executed before using aforementioned event reading engine.

The event reading hook is quite convenient place for adding additional functionality to event loop based GUI applications.
We added 2 useful facilities there:
- timers for scheduling callbacks after some time interval in one shot or periodic mode
- jobs for scheduling actions that must be executed ASAP in the context of the event loop

We provided GUI base classes to serve as generic building blocks for applications as well as several ready to use
GUI elements such as buttons, labels, progress and battery charge indicators.

The styles framework serves as a convenient way of setting various parameters in CSS-like manner. It separates
parameters storage from the code that using them which leads to cleaner code and simplify visual appearance tuning.

The demo application is provided as working example of building simple GUI in multi-threaded application.

![](https://github.com/olegv142/pygame-ts/demo.png)

## Author

Oleg Volkov (olegv142@gmail.com)
