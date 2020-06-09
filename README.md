# WhatsParse
A simple python parser for whatsapp chats. Now pretty performant, parsing ~250k messages a second on my machine.  

## Use Instructions
1. Clone this repository
2. Open whatsapp, navigate to the chat profile, and press export chat.
3. Get this text file to your computer (in whatever way).
4. Place it in the cloned repository folder.
5. Open the "Whatsparse.py" file, and scroll to the bottom. Replace 'chat.txt' with the name of your exported text file.
6. Run 'Whatsparse.py'!

## Functionalities
Barely any, but very extensible.  
Messages can be accessed via the "msgs" property of a WhatsParse object.  
Each 'message' is a dictionary with "sender", "body", and "date" keys.  
A list of senders (people in the chat) can be accessed via the "senders" property of a WhatsParse object.  
An easy way to graph things over time, is to use the "graph_over_time" method, which takes a filter function.  
This filter function is called for every message, which is passed to the function, and should return a number.  
I.E a function to graph messages over time, this function should just return 1.  
The resulting graph will have separate series for each sender, be graphed for the duration of the chat's existance and will also have trendlines.  
