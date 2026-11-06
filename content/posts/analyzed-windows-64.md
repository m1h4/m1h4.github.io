---
title: "Analyzed for Windows 64-bit"
date: 2014-05-04T00:00:00+02:00
---

I’ve finally dug-up the source-code for the **Analyzed** Windows Media Player plugin from my old Windows PC and managed to
open it in **Visual Studio 2013**. The last modified file was from **2007** :) It’s been **7** years, and the original was writen
when I was just starting my first year of college.

I was amazed to see the old **Visual Studio 2005** project open up without issues in the latest **2015 IDE** and compile without
any errors with the newest toolset. Also, creating a **x64** build and compiling it went without a hitch, just a couple of
uncarefull casts needed to be fixed to get rid of warnings.

So, at first hand I’m just releasing a **64-bit** compatibile version of **Analyzed** which you can find [here]({{< relref "apps/analyzed.md" >}}). But now, since I
have everything setup for work again, you can expect updates to the actual plugin – as soon as I find time to work on it ;)