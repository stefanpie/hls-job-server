open_project -reset hls_project__simulation

add_files kernel.h
add_files kernel.cpp
add_files -tb tb.cpp

set_top kernel

open_solution -reset hls_project__synthesis

set_part {xczu9eg-ffvb1156-2-e}
create_clock -period 3.3 -name default

csim_design