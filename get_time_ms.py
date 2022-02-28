import time

# Check the system clock provides `ms` granularity for current unix time
# TODO
# possible way to check
#   get time.time_ns()
#   if last 10^9 digits are 0 # I guess there is a very small prob this can actually happen?
#       run again, to reduce probably of accident even more 
#       if still all zeros -> raise Exception("apparently unable to get unix 
#       time smaller than seconds. We depend on `ms` so running this won't work.
#       Exiting.")

s = time.time_ns()
# get time ms
time_ns = time.time_ns()
print(
    f"took {(time.time_ns() - s) / 1_000_000} ms to get the current unix time in ns."
)
