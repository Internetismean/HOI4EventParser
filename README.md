# HOI4EventParser
Python parser to transform the code of a draw.io diagram into a HOI4 event chain

Instructions:
-
For the program to work, the diagram must have the following format:
1. Events use a container and a rounded rectangle
2. Options use a normal rectangle
3. Unions are done with arrows
To create an event box get a container and a rounded rectangle and drag the rounded rectangle into the container until merge; I suggest making the rounded rectangle not touch the walls of the container because arrows have to connect to the container and having the rectangle touch the container can cause arrows to connect to them instead. The text of the container top will be the title and the text of the rectangle will be used as the description. 
For the option, grab a normal rectangle. The text inside it will be used as the text of said option. If you want the event that option triggers to be triggered for a certain tag, write the tag between parenthesis. The parenthesis and the tag will not appear in the final text. You can't use parenthesis otherwise for option text, although I don't think they are used much to begin with.
Unite the container of an event with its options with arrows, same with an option and the container of the event it triggers.
The program has a GUI where you have to input the namespace of the events, the starting number (so setting it to 1 will make event be numbered 1,2,3,...) and the code from the diagram, that can be extracted from Extras > Edit diagram in the draw.io page.
The program outputs two files: a txt file with all the event code created and a yml file with all the loc. 
