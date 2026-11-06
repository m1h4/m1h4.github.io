---
title: "Android's New Runtime"
date: 2014-02-16T00:00:00+02:00
---

There has been a lot of talk recently about Google’s new **ART** runtime for Android which debuted with the recent **Android 4.4** update.
**ART** (which stands for **Android Runtime**) means to replace **Dalvik**, the current runtime on top of which (most) Android applications execute.
**Dalvik** has been a part of Android since the beginning, being one of the core components of the whole operating system.


As user applications on Android are meant to be written in **Java** (see Google having issues with Oracle about this), the runtime is the
component which runs the compiled **Java** applications on the device and connects them with the rest of the operating system (applications
are not much fun by themselves if they do not use the graphics system to display user interfaces, the networking system to send and receive data etc).

## What’s a runtime

![Android](/img/Androids-ART-Runtime.png#floatright)

Android StructureThe core components of the operating system are run in native code which means they are a series of instructions
understood by the underlying processor of the device on which they are installed. This is the normal mode in which programs are expected
to run on a system in order to best exploit the speed, power efficiency and available features. There are many languages that can be
compiled into native code, but C and C++ are de facto standard in the area of operating systems and supporting libraries.

When looking at the user application layer of the Android stack, a simpler, higher-level language makes more sense that these complicated
lower-level languages. Java attracts a much wider audience of developers: it’s easier to learn, simpler to work with, has all the power
necessary for user applications, has lots of libraries that handle various complex tasks if needed and has lots of useful information and
support available all over the Internet. But by its cross-platform nature Java is not compiled into native code and as such is less efficient
that native languages (a drawback greatly surpassed by the aforementioned benefits).

It was Dalviks job to serve as the “processor” of the Java compiled application code (Java programs are compiled into “bytecode” which serves
as instructions for the runtime, just like native languages are compiled into machine code which is a series of instructions for processors)
all the way from the first version of Android released with the HTC Dream in 2008. With Android 2.2 released in 2010. Google implemented
Just-In-Time compilation of application bytecode which meant that some parts of user applications were being compiled to native code while
running the application. This was possible to do with the faster mobile processors and more available memory at that time. The runtime evolved
with the hardware and brought increased performance in applications, especially in the ones which had program parts that did lots of computation.
Till 2013. this mechanism didn’t change much apart from continuous optimizations to speed up the whole process (concurrent garbage collection is
noteworthy, again with the evolution of hardware, since multicore became commonplace). The core concept of having machine independent code stored
on the phone and eventually converting parts of it into native code during runtime stayed the same.

## A different approach

Enter ART, the new runtime which changes the old concept: instead of keeping the installed application in a machine independent format,
compile it into a native, machine-optimized form upon installation. This makes perfect sense for a number of reasons:

Applications on Android allways have to be installed before they are used, this is the perfect opportunity to optimize them to run as
best as they can on the given device. Have NEON available? Get those compute loops to work better. Have a 64-bit CPU? Do those large
integer operations in less instructions.

It is expected that an installation takes some time, since it happens only once, the drawback of making it a bit longer (keep in mind
we are talking seconds here, not minutes or hours) is greatly outweighed by the benefit of the final application starting faster,
running smoother, being more responsive and using less battery. These are the things you experience every day, contrast that with the
installation, which you experience only once, and app updates which occur only occasionally, but you are in control over when that
happens and if you have that set to automatic it will probably happen without you even noticing (without you consciously waiting for
it to finish and annoy you that is).

The compiled code might take a bit more space to accommodate all the extra information needed for debugging and whatnot, but we are
talking about kilobytes or megabytes here. A lot of articles would have you think that a 20mb application would be a couple of
percentages larger while in fact only the smaller portion of the application size is program code (which is the part that increases
a couple of percentages). Other parts are graphics files, sound files, configuration files, or other resources which are not affected
by the compilation. So do you really care about a couple of megabytes of extra storage in total being used by your apps on your
gigabytes-of-storage phone for the benefit of smoothness and better battery life?
Since compilation is done at a phase when compilation time is not critical, more advanced optimizations and analysis can take place,
resulting in programs that take much better advantage of special instructions and features supported by modern mobile processors.
Dalviks interpretation of bytecode and just-in-time compilation have to make compromises to not take too much time for live compilation and cause jitter.
So it is clear that ART is the next evolutionary phase of how the Android operating system will deal with running user applications.
As much as it is an obvious improvement for which one might ask “why just now?”, it is a major engineering effort. What better time to
finally undertake it than now, in the period when Google is taking the platform lead and is trying to focus on making Android more
efficient and friendly towards lower cost devices.

## Still experimental

Sadly, it’s not all bells and whistles yet. The current distribution of the runtime (minorly updated with Android 4.4.1) is still a
work-in-progress. A very impressive work-in-progress I might add, since the number of issues I’ve experienced with it is astonishingly
low, considering that it’s the first public release of a complete replacement of a core Android operating system pillar. There are only
a couple of issues that I’ve experienced so far:

Applications are much slower while debugging. This most certainly has to do with the massive translation needed to be done to correspond
the compiled native code to the developers Java code. I was wondering how well this would have been done and it is clear that there’s still
work needed to be done to make it as usable as it was with Dalvik.
Serializing and deserializing objects into/from streams is slow (painfully slow when debugging, see above). As a user you’ll notice this in
some applications which load initialization data this way: the startup freeze of the Google Analytics app, the IMDB app and maybe others but
these are concrete examples that I’ve had experience with.
The above issues primarily concern developers and I would recommend developers stick to debugging their applications in Dalvik for the most
reliable and least frustrating experience. As for end users, if you are not an expert user or developer, please do not switch to ART for the
time being. Developers don’t need to be hassled with issues you might be (consciously or unconsciously) having with an experimental
work-in-progress runtime. I’ve seen people bash applications and give bad reviews for problems that were obviously caused by them switching
their phone to ART (probably by following some ultra-cool Android tweaking website) and then forgetting that applications might be having
problems because they’re using experimental operating system features and not because it’s the developers fault.

I was planning on supplementing this article with some concrete measurements and performance comparisons between Dalvik and ART
execution/debugging but didn’t manage to find the time to settle on a satisfactory methodology and actually do them. As such, the
article began to gather dust so I decided to publish it without the “scientific” data. If I find the time to do any measurements
I’ll publish and link them here.