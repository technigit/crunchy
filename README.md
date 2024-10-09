## Crunchy Report Generator
[Crunchy Report Generator](archive/HISTORY.md) is a Python package that accepts a loosely/specially formatted set of data and generates a report.

In the spirit of the acronym, "Crunch Really Useful Numbers Coded Hackishly," the guiding principle is for the data input format to be as reasonably readable, flexible, and maintainable as possible.  For example, instead of a CSV format that can be a bit unwieldy to read, the data can be freely spread out by spaces to arrange it by columns.  Directives can be added to specify what the report should look like.  Plugins can be used to provide additional functionality such as running totals, averages, row/column sums, graphs, data science, and more.

## Prerequisites
* Python 3.0+

## Getting Started
Example `helloworld` file:
```
&print Hello, World!
```

Usage and output:
```
$ python3 crunchy.py helloworld
Hello, World!
$ cat helloworld | python3 crunchy.py
Hello, World!
$ python3 crunchy.py

Crunchy Report Generator aka Crunch Really Useful Numbers Coded Hackishly
v0.0.10

To get help, enter &help
To exit interactive mode, use Ctrl-D

&read helloworld
<i> Reading file helloworld.
Hello, World!
<i> Finished reading file helloworld.


```

Example `minimal-example` file:
```
&init 2013.12
&set decfield 2
&set clrfield 3
&set incfield 4
Check|5     Date|10   Payment8  Clear1   Deposit8  Description<22  Actual8  Cleared8
      -  11/01/2023      10.45       *          -  Wordpress hosting
      -  11/01/2023      48.77       *          -  Torchy's
      -  11/01/2023          -       *    1500.00  paycheck
      -  11/01/2023     745.00       -          -  apartment
```

Usage and output:
```
$ python3 crunchy.py minimal-example
<i> Initializing balance to 2013.12.
<i> Setting decrement field to 2.
<i> Setting clear field to 3.
<i> Setting increment field to 4.
Check    Date     Payment C  Deposit Description              Actual  Cleared
      11/01/2023    10.45 *          Wordpress hosting       2002.67  2002.67
      11/01/2023    48.77 *          Torchy's                1953.90  1953.90
      11/01/2023          *  1500.00 paycheck                3453.90  3453.90
      11/01/2023   745.00            apartment               2708.90  3453.90
$
```

Getting help:
```
$ python3 crunchy.py -h
--
Help Topic: Usage

   Usage: crunchy.py [<options>] [<files>] [-h [<topic>] | --help [<topic>] | ... ]

   Help topics: usage, data-format, directives, files, map, options, read, set, testing

   For more information, use -h or &help followed by one of the help topics listed above.

$ python3 crunchy.py

Crunchy Report Generator aka Crunch Really Useful Numbers Coded Hackishly
v0.0.10

To get help, enter &help
To exit interactive mode, use Ctrl-D

&help
--
Help Topic: Usage

   Usage: crunchy.py [<options>] [<files>] [-h [<topic>] | --help [<topic>] | ... ]

   Help topics: usage, data-format, directives, files, map, options, read, set, testing

   For more information, use -h or &help followed by one of the help topics listed above.


```

## Authors
* **Andy Warmack** - *Initial work* - [technigit](https://github.com/technigit)

## License
[MIT License](LICENSE)
