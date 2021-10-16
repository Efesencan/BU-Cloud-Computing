from chrisapp.base import ChrisApp
import pandas as pd
import os
import glob
import argparse
from tqdm import tqdm


class AgeAtScan(ChrisApp):
    """
     blah blah
     """
    PACKAGE = __package__
    TITLE = 'Age Calculation'
    CATEGORY = 'Format'
    TYPE = 'ds'
    ICON = ''  # url of an icon image
    MIN_NUMBER_OF_WORKERS = 1  # Override with the minimum number of workers as int
    MAX_NUMBER_OF_WORKERS = 1  # Override with the maximum number of workers as int
    MIN_CPU_LIMIT = 1000  # Override with millicore value as int (1000 millicores == 1 CPU core)
    MIN_MEMORY_LIMIT = 200  # Override with memory MegaByte (MB) limit as int
    MIN_GPU_LIMIT = 0  # Override with the minimum number of GPUs as int
    MAX_GPU_LIMIT = 0  # Override with the maximum number of GPUs as int
    
    OUTPUT_META_DICT = {}

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
                          default=False,
                          optional=True,
                          type=bool
                          )

    def run(self, options):
        input_files = glob.iglob(os.path.join(options.inputdir, options.inputPathFilter))
        #outputdir = Path(options.outputdir).resolve()
        #os.chdir(options.inputdir)
        def convert_delta(delta, options):
            if options.unit in ['mths', 'months', 'm']:
                return round(delta.dt.days / 365.25 * 12, 1)
            else:
                return delta.dt.days

        for file in tqdm(input_files):
            csv = pd.read_csv(file)
            csv[[options.minuend, options.subtrahend]] = csv[
                [options.minuend, options.subtrahend]].apply(pd.to_datetime)
            csv[options.result] = convert_delta(csv[options.minuend] - csv[options.subtrahend], options)
            if options.verbose:
                print(csv.to_csv(index=False))
            else:
                csv.to_csv(str(options.outputdir+'/'+os.path.basename(file)), index=False)

    def show_man_page(self):
        self.print_help()
