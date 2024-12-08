#include "kernel.h"

void kernel(fixed_16_8 in1[array_size], fixed_16_8 in2[array_size], fixed_16_8 out[array_size])
{
#pragma HLS TOP name=kernel

#pragma HLS PIPELINE II = 1
#pragma HLS ARRAY_PARTITION variable = in1 complete dim = 1
#pragma HLS ARRAY_PARTITION variable = in2 complete dim = 1
#pragma HLS ARRAY_PARTITION variable = out complete dim = 1
    for (int i = 0; i < array_size; i++)
    {
#pragma HLS UNROLL
        out[i] = in1[i] + in2[i];
    }
}
