import sys
import logging

log = logging.getLogger()
log.setLevel(logging.INFO)
strm = logging.StreamHandler(sys.stdout)
frmt = logging.Formatter("%(name)s - %(levelname)s %(message)s")
strm.setFormatter(frmt)
log.addHandler(strm)

from pdfexploder.coverageutils import file_range, size_range

def shouldbenotcovered():
    log.info("not covered")

if __name__ == "__main__":
    log.info("in dontinclude main")
