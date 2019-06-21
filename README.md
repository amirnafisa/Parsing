# Parsing

There are two widely known parsers, one of which is Earley's. This project gives an implementation of the same.

It can be run via the gui interface as well as commandline.

To use the gui:
python3 interface_tool.py

To use the command line utility:
python3 parse2.py <grammar file> <Sentence2Parse>

![Alt text](./assets/interface.png?raw=true "GUI Interface")

Example Usage:
python3 parse2.py wallstreet.gr 'The fan is working .'
