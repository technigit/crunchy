## Crunch Really Useful Numbers Coded Hackishly
For many years, the working title of this project was crunch, a [recursive acronym](https://en.wikipedia.org/wiki/Recursive_acronym) standing for "Crunch Really Useful Numbers Coded Hackishly." There is already a well-established tool called "crunch," [a wordlist generator](https://www.kali.org/tools/crunch/), so this project has to have a different name to avoid confusion.  **Crunchy Report Generator** is a script that takes a specially formatted set of data and generates a report of some kind.

Here is an early version that became something that I have used pretty regularly.  I found it rather awkward to type "crunch" all the time, so I decided to call it "fin," short for "financial."  I guess at one point, I was going to call it "mofi" (money financial, which is mentioned in the source) but it didn't really stick for me.  Carried from one computer system to the next over the years, this script has had the timestamp "Mar 25 13:01:30 2000" and a file size of 8685.  The code is a bit of a mess, but I wanted to leave it as is.

* [fin](fin)

I also came up with several interesting aliases along the way.  The idea is to monitor two bank accounts, so ```fina``` shows a report for bank account a, and ```finb``` shows a report for bank account b, while ```finab``` shows a (manually) combined report for the two.  The aliases defined therein were renamed for better context and readability.

* [aliases](aliases)

* [fin.vim](fin.vim)

## How it got started
One reason **Crunchy Report Generator** exists is to scratch an itch, and it is just simply a lot of fun to work on it.  It also makes my life easier by eliminating the guesswork of tracking my personal banking.

Admittedly, there are already plenty of ways to crunch financial numbers these days.  It is easy to find something that works, such as [ledger](https://ledger-cli.org/) for people who like command-line solutions, or [Mint](https://mint.intuit.com/) for people who prefer the more user-friendly solutions.  On the other hand, those are mostly budgeting and banking tools; the scope of **Crunchy Report Generator** is not necessarily limited to finances.

Anyway, back in 2000, or a bit before that, I wanted to track my bank activity and predict where my cash flow was going, but at the time, I was not aware of anything that could do exactly what I wanted.  To solve this problem, I decided to write a script in [Perl](https://www.perl.org/), and this project was the result.  I have been using it for many years without any further changes.  In 2022, I started porting it to [Python](https://www.python.org/) and I have some new ideas, so we will see where it goes from here.

## How it works
Using **Crunchy Report Generator** is kind of simple if you think like a programmer.  Just create an input file and fill it with formatted data.  Next, feed that input file into the crunchy.py script.

Here is an example `helloworld` file:
```
&print Hello, World!
```

Usage and output:
```
$ python3 crunchy.py helloworld
Hello, World!

$ cat helloworld | python3 crunchy.py
Hello, World!

$
```

A more detailed set of examples will be added later.

## Testing
Included in the archive directory is an informal set of tests to ensure that crunchy.py replicates the original functionality of the original fin script.  From this directory, you can compare the outputs as follows:

```
$ perl fin tests/{test name}
(output is displayed)

$ python3 ../crunchy.py tests{test name}
(output is displayed)
```

The outputs should be similar, with the exception that crunchy.py can read files recursively.

## Authors
* **Andy Warmack** - *Initial work* - [technigit](https://github.com/technigit)
