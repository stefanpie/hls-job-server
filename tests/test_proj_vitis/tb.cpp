#include "kernel.h"

#include <cmath>

int main()
{
    float in_0_golden[array_size];
    float in_1_golden[array_size];
    float out_golden[array_size];

    for (int i = 0; i < array_size; i++)
    {
        in_0_golden[i] = (i - array_size / 2) * 0.25;
        in_1_golden[i] = (i - array_size / 2) * 0.15;

        out_golden[i] = in_0_golden[i] + in_1_golden[i];
    }

    fixed_16_8 in_0[array_size];
    fixed_16_8 in_1[array_size];
    fixed_16_8 out[array_size];
    float out_float[array_size];

    for (int i = 0; i < array_size; i++)
    {
        in_0[i] = fixed_16_8(in_0_golden[i]);
        in_1[i] = fixed_16_8(in_1_golden[i]);
    }

    kernel(in_0, in_1, out);

    for (int i = 0; i < array_size; i++)
    {
        out_float[i] = float(out_golden[i]);
    }

    float errors_abs[array_size];
    for (int i = 0; i < array_size; i++)
    {
        errors_abs[i] = std::abs(out_float[i] - out_golden[i]);
    }

    const float epsilon = 0.01;
    for (int i = 0; i < array_size; i++)
    {
        if (errors_abs[i] > epsilon)
        {
            printf("Error bigger than epsilon detected: %f\n", errors_abs[i]);
            printf("out_golden[%d] = %f\n", i, out_golden[i]);
            printf("out[%d] = %f\n", i, out_float[i]);
            return 1;
        }
    }

    printf("All good! Errors are within epsilon of %f\n", epsilon);
    for (int i = 0; i < array_size; i++)
    {
        printf("error_abs[%d]: %f\n", i, errors_abs[i]);
    }

    return 0;
}