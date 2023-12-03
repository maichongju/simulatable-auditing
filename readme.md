# Simulatable Auditing

This is a implementation of the Simulatable Auditing descried in paper [Simulatable Auditing](https://www.sciencedirect.com/science/article/pii/S002200001300113X). It implemented the classical compromise for `sum` and `max` simulatable auditing. 

## Installation

Install the dependencies in `requirements.txt` with `pip install -r requirements.txt`.

## Usage
```
usage: simulatableAuditing.py [-h] [-s] [-m] [-d [DATA ...]] [-f FILE]

Simulatable Auditing for sum and max queries

options:
  -h, --help            show this help message and exit
  -s, --sum             Use sum auditing
  -m, --max             Use max auditing
  -d [DATA ...], --data [DATA ...]
                        Dataset
  -f FILE, --file FILE  Dataset file
```

## Example

### sum auditing

```
python simulatableAuditing.py --sum --data 1 2 3 4 5 6
SUM AUDITING
Enter quit or q to quit
Enter query (use a command separator): 1
Denied
Enter query (use a command separator): 1,2,3
6.0
Enter query (use a command separator): 1,2,3,4
Denied
Enter query (use a command separator): q
```

### max auditing

```
python simulatableAuditing.py --max --data 1 2 3 4 5 6
MAX AUDITING
Enter quit or q to quit
Enter query (use a command separator): 1,2,3,4
4.0
Enter query (use a command separator): 1,2,3
Denied
Enter query (use a command separator): q
```
