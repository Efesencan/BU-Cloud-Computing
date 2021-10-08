from chrisapp.base import ChrisApp
import pandas as pd
import os
import glob
import argparse
from tqdm import tqdm


class AgeAtScan(ChrisApp):
    def define_parameters(self):
        self.add_argument(
            '-p', '--inputPathFilter',
            dest='inputPathFilter',
            help='selection (glob) for which files to evaluate.',
            default='*.csv',
            type=str,
            optional=True
        )
        self.add_argument('-s', '--subtrahend',
                          dest='subtrahend',
                          help='Date of birth.',
                          default="DateOfBirth",
                          optional=True,
                          type=str
                          )
        self.add_argument('-m', '--minuend',
                          dest='minuend',
                          help='Date of scan.',
                          default="DateOfScan",
                          optional=True,
                          type=str
                          )
        self.add_argument('-r', '--result',
                          dest='result',
                          help='Title of results column',
                          default="AgeAtScan",
                          optional=True,
                          type=str
                          )
        self.add_argument('-u', '--unit',
                          dest='unit',
                          help='Unit of difference (days, months). Defaults to days if no flag',
                          default="days",
                          optional=True,
                          type=str
                          )
        self.add_argument('-v', '--verbose',
                          dest='verbose',
                          help='Display CSV in stdout. File is not written to',
                          optional=True,
                          type=str
                          )

    def run(self, options):
        input_files = glob.iglob(os.path.join(options.inputdir, options.inputPathFilter))

        def convert_delta(delta, options):
            if options['unit'] in ['mths', 'months', 'm']:
                return round(delta.dt.days / 365.25 * 12, 1)
            else:
                return delta.dt.days

        for file in tqdm(input_files):
            csv = pd.read_csv(file)
            csv[[options.minuend, options.subtrahend]] = csv[
                [options.minuend, options.subtrahend]].apply(pd.to_datetime)
            csv[options['result']] = convert_delta(csv[options.minuend] - csv[options.subtrahend], options)
            if options.verbose:
                print(csv.to_csv(index=False))
            else:
                csv.to_csv(file, index=False)

    def show_man_page(self):
        self.print_help()
