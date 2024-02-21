import datetime

from problog.extern import problog_export, problog_export_nondet, problog_export_raw

@problog_export('+str', '-int')
def get_hour(A):
    A = A.replace("'", "")
    dt = datetime.datetime.strptime(A, "%Y-%m-%d %H:%M:%S")
    B = dt.hour
    return B

@problog_export('+str', '-int')
def get_minute(A):
    A = A.replace("'", "")
    dt = datetime.datetime.strptime(A, "%Y-%m-%d %H:%M:%S")
    B = dt.minute
    return B

@problog_export('+str', '-int')
def get_stamp(A):
    A = A.replace("'", "")
    dt = datetime.datetime.strptime(A, "%Y-%m-%d %H:%M:%S")
    B = dt.timestamp()
    return B

@problog_export('+str', '-int')
def get_weekday(A):
    A = A.replace("'", "")
    dt = datetime.datetime.strptime(A, "%Y-%m-%d %H:%M:%S")
    B = dt.weekday()
    return B