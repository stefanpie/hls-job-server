
#include "ap_fixed.h"

typedef ap_fixed<16, 8> fixed_16_8;
const int array_size = 16;

void kernel(fixed_16_8 in1[array_size], fixed_16_8 in2[array_size], fixed_16_8 out[array_size]);